#!/usr/bin/env python3
"""Generate an HTML report of lexical fields covered/missing in lully/words.py.

For each hand-picked semantic field, a small set of representative French
words is checked against the current NOUNS/ADJECTIVES tuples. The report
highlights, per field, which of those representative words are still absent
from the corpus — a checklist for humans hunting for words to add with
addwords.py.

Usage:
    python lexical_report.py [--words lully/words.py] [--out docs/index.html]
"""
import argparse
import ast
import json
import os
import html as html_lib


# (field name, "N" nom / "A" adjectif / "N+A" les deux, mots-témoins, note optionnelle)
FIELDS = [
    ("Figures de style & rhétorique", "N", [
        "anacoluthe", "antanaclase", "antonomase", "asyndète", "litote", "métaphore",
        "métonymie", "anaphore", "antithèse", "paronomase", "hyperbate", "parembole",
        "allitération", "anadiplose", "apostrophe", "hypallage", "hyperbole", "allégorie",
        "synecdoque", "ellipse", "antiphrase", "périphrase",
        "tautologie", "gradation", "comparaison", "personnification",
    ], ""),
    ("Sciences savantes en -logie / -graphie", "N", [
        "biologie", "astronomie", "anthropologie", "cristallographie", "démographie",
        "géologie", "sociologie", "psychologie", "chronologie", "météorologie",
        "cartographie", "bibliographie", "numismatique", "botanique", "zoologie",
        "criminologie", "climatologie", "ethnologie", "phonologie", "morphologie", "physiologie",
    ], ""),
    ("Métiers & professions féminisées", "N", [
        "institutrice", "avocate", "danseuse", "chercheuse", "journaliste", "pianiste",
        "bibliothécaire", "infirmière", "architecte", "biographe", "astronome", "actrice",
        "autrice", "conductrice", "ouvrière", "couturière", "boulangère", "artificière",
        "chirurgienne", "juriste",
    ], ""),
    ("Émotions & états d'âme", "N", [
        "joie", "tristesse", "angoisse", "nostalgie", "mélancolie", "extase", "frayeur",
        "colère", "ardeur", "peur", "honte", "fierté", "jalousie", "envie", "allégresse",
        "désolation", "inquiétude", "anxiété", "exaltation", "consternation",
    ], ""),
    ("Flore : fleurs, plantes", "N", [
        "fougère", "bruyère", "marguerite", "jonquille", "aubépine", "ortie", "camomille",
        "lavande", "glycine", "pâquerette", "clémentine", "groseille", "framboise",
        "myrtille", "luzerne",
    ], ""),
    ("Faune : animaux, insectes", "N", [
        "libellule", "coccinelle", "hirondelle", "baleine", "mygale", "araignée", "fourmi",
        "abeille", "chenille", "biche", "corneille", "grenouille", "hyène", "panthère",
        "murène", "otarie",
    ], ""),
    ("Vêtements & parures", "N", [
        "chemise", "ceinture", "cravate", "écharpe", "capuche", "jupe", "chaussette",
        "casquette", "robe", "veste", "cagoule", "mitaine", "chemisette",
    ], ""),
    ("Habitat & architecture", "N", [
        "chaumière", "cathédrale", "forteresse", "chapelle", "masure", "bâtisse",
        "citadelle", "abbaye", "bibliothèque", "ferme", "auberge", "caserne", "mairie",
    ], ""),
    ("Objets & outils du quotidien", "N", [
        "pince", "fourchette", "cuillère", "casserole", "bouilloire", "aiguille", "épingle",
        "brosse", "éponge", "bassine", "louche", "lime",
    ], ""),
    ("Musique, danse, instruments", "N", [
        "guitare", "cornemuse", "harpe", "clarinette", "chorale", "gigue", "cymbale",
        "flûte", "mandoline", "sarabande", "tarentelle", "polka",
    ], ""),
    ("Armement & guerre", "N", [
        "arquebuse", "cuirasse", "armure", "artillerie", "bataille", "embuscade", "arbalète",
        "hallebarde", "baïonnette", "catapulte", "garnison",
    ], ""),
    ("Temps & durée", "N", [
        "décennie", "journée", "matinée", "soirée", "éternité", "semaine", "année",
        "seconde", "minute", "heure", "époque", "ère",
    ], ""),
    ("Cuisine & gourmandise", "N", [
        "confiture", "choucroute", "fondue", "marmelade", "charcuterie", "pâtisserie",
        "brioche", "omelette", "soupe", "compote", "confiserie",
    ], ""),
    ("Relief & paysages d'eau", "N", [
        "montagne", "vallée", "rivière", "falaise", "colline", "plaine", "presqu'île",
        "péninsule", "crique", "lagune", "cascade",
    ], ""),
    ("Finance & économie", "N", [
        "banque", "bourse", "capitalisation", "liquidité", "dette", "monnaie", "fortune",
        "prospérité", "inflation", "récession", "spéculation", "économie", "rentabilité",
        "solvabilité",
    ], ""),
    ("Textures & matières", "A", [
        "rugueuse", "lisse", "soyeuse", "visqueuse", "granuleuse", "poreuse", "élastique",
        "collante", "huileuse", "cotonneuse",
    ], ""),
    ("Sciences & techniques en -ique", "A", [
        "chimique", "biologique", "électrique", "magnétique", "acoustique", "génétique",
        "atomique", "numérique", "mécanique", "organique",
    ], ""),
    ("Saveurs", "A", [
        "sucrée", "salée", "amère", "acide", "épicée", "fade", "savoureuse", "insipide",
    ], ""),
    ("États émotionnels", "A", [
        "joyeuse", "triste", "anxieuse", "sereine", "mélancolique", "exaltée", "apaisée",
        "furieuse", "radieuse", "morose",
    ], ""),
    ("Anatomie, corps humain", "N", [
        "clavicule", "mâchoire", "nuque", "cheville", "paupière", "narine", "cuisse",
        "hanche", "gencive", "rotule", "rétine", "aisselle", "omoplate", "phalange", "vertèbre",
    ], "le noyau (visage, membres) est souvent là ; les organes internes, moins"),
    ("Médecine, maux du corps", "N", [
        "bronchite", "arthrite", "appendicite", "mycose", "névralgie", "claustrophobie",
        "agoraphobie", "hydrophobie", "migraine", "tuberculose", "anosmie", "agueusie",
        "cirrhose", "gastrite", "otite", "laryngite", "conjonctivite", "dermatite",
        "hépatite", "angine", "allergie", "insomnie", "anémie", "fracture", "entorse",
        "cicatrice", "blessure", "fièvre", "toux", "nausée",
    ], "les symptômes du quotidien passent, le jargon savant en -ite/-ose résiste"),
    ("Religion & liturgie", "N", [
        "bénédiction", "absolution", "communion", "providence", "liturgie", "prière",
        "confession", "messe", "procession", "dévotion", "foi", "grâce", "offrande",
        "idolâtrie", "hérésie", "canonisation", "excommunication", "apparition",
        "résurrection", "ascension", "annonciation", "épiphanie", "transsubstantiation",
    ], "vocabulaire chrétien surtout ; les autres traditions religieuses sont un angle mort"),
    ("Droit, justice, politique", "N", [
        "constitution", "sanction", "ordonnance", "souveraineté", "juridiction",
        "législation", "citoyenneté", "élection", "démocratie", "monarchie",
    ], ""),
    ("Vocabulaire logiciel / dev", "N", [
        "application", "numérisation", "robotique", "informatique", "connexion",
        "interface", "plateforme", "algorithmique", "cybersécurité", "intelligence", "base",
        "donnée", "messagerie", "notification", "synchronisation", "virtualisation",
        "modélisation", "instanciation", "journalisation",
    ], "un clin d'œil facile pour qui code : ce champ parlera à Lucas plus qu'au grand public"),
    ("Parenté proche", "N", [
        "mère", "sœur", "fille", "tante", "nièce", "cousine", "marraine", "filleule",
        "belle-mère", "grand-mère", "aïeule", "matriarche", "bru", "veuve", "épouse",
        "fiancée", "concubine",
    ], "le cercle proche est couvert, la parentèle plus éloignée beaucoup moins"),
    ("Sport & activités physiques", "N", [
        "natation", "gymnastique", "compétition", "course", "mêlée", "escalade",
        "randonnée", "plongée", "boxe", "lutte", "escrime", "équitation", "voile",
        "luge", "pétanque",
    ], ""),
    ("Écologie & environnement", "N", [
        "biodiversité", "pollution", "biomasse", "reforestation", "surpêche",
        "déforestation", "canicule", "sécheresse", "empreinte", "transition",
        "permaculture", "renaturation",
    ], ""),
    ("Espace, astronomie concrète", "N", [
        "comète", "galaxie", "nébuleuse", "étoile", "supernova", "constellation",
        "météorite", "exoplanète", "orbite",
    ], ""),
    ("Registre familier léger", "N", [
        "bagnole", "gueule", "fringue", "bouffe", "galère", "embrouille", "combine",
        "cagoule", "provoc", "tune",
    ], ""),
    ("Couleurs nommées", "N+A", [
        "rose", "mauve", "pourpre", "vermeille", "écarlate", "turquoise", "indigo", "ocre",
        "ivoire", "corail", "cramoisie", "incarnate", "safran", "kaki", "beige", "argentée",
        "dorée", "cuivrée", "opaline",
    ], "champ pénalisé par la grammaire : une couleur est un nom masculin par défaut "
       "(« le rouge »), or le corpus est presque tout féminin"),
    ("Tailles & formes", "A", [
        "ronde", "carrée", "étroite", "vaste", "massive", "difforme", "oblongue",
        "concave", "convexe",
    ], ""),
    ("Parenté par adjectif (filiation)", "A", [
        "maternelle", "paternelle", "fraternelle", "filiale", "conjugale", "matrimoniale",
        "ancestrale", "cousine", "gémellaire", "adoptive", "veuve", "célibataire",
    ], ""),
    ("Numérique grand public (IA, réseaux, smartphone)", "N", [
        "robotique", "cybersécurité", "intelligence-artificielle", "publication", "story",
        "notification", "selfie", "messagerie", "vidéoconférence", "géolocalisation",
        "authentification", "biométrie", "domotique", "réalité-virtuelle", "blockchain",
        "cryptomonnaie",
    ], "quasi vierge : bon terrain de chasse si le corpus doit parler du monde d'aujourd'hui"),
]

TIER_BOUNDS = [
    ("bien", "Bien couverts", 70),
    ("partiel", "Partiellement couverts", 40),
    ("non", "Peu ou pas couverts", 0),
]


def load_words(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src, filename=path)
    ns = {}
    exec(compile(tree, path, "exec"), ns)
    return ns["NOUNS"], ns["ADJECTIVES"]


def tier_for(pct):
    for key, label, floor in TIER_BOUNDS:
        if pct >= floor:
            return key, label
    return TIER_BOUNDS[-1][0], TIER_BOUNDS[-1][1]


def analyze(nouns, adjectives):
    nouns_lc = {w.lower() for w in nouns}
    adj_lc = {w.lower() for w in adjectives}
    results = []
    for name, typ, diag, note in FIELDS:
        if typ == "N+A":
            lexicon = nouns_lc | adj_lc
        elif typ == "A":
            lexicon = adj_lc
        else:
            lexicon = nouns_lc
        present = [w for w in diag if w in lexicon]
        missing = [w for w in diag if w not in lexicon]
        pct = round(100 * len(present) / len(diag))
        tier_key, tier_label = tier_for(pct)
        results.append({
            "name": name, "type": typ, "note": note,
            "pct": pct, "present": present, "missing": missing,
            "tier_key": tier_key, "tier_label": tier_label,
        })
    return results


def esc(s):
    return html_lib.escape(s, quote=True)


def slugify(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")


def card_html(field):
    type_label = {"N": "noms", "A": "adjectifs", "N+A": "noms & adjectifs"}[field["type"]]
    missing_words = [w.title() for w in field["missing"]]
    present_chips = "".join(
        f'<span class="chip chip--present">{esc(w.title())}</span>' for w in field["present"]
    )
    note_html = f'<p class="note">{esc(field["note"])}</p>' if field["note"] else ""
    present_row = (
        f'<div class="present-row"><span class="present-label">déjà présents ({len(field["present"])}/{len(field["present"]) + len(field["missing"])})</span>'
        f'<div class="chips">{present_chips}</div></div>'
        if present_chips else ""
    )

    if missing_words:
        pool_json = esc(json.dumps(missing_words, ensure_ascii=False))
        n = len(missing_words)
        missing_html = f"""<div class="missing-row">
            <span class="missing-label">à chercher ({n} piste{'s' if n > 1 else ''})</span>
            <div class="chips reveal-chips"></div>
            <button type="button" class="reveal-btn" data-pool="{pool_json}">🔍 Révéler un indice ({n} restant{'s' if n > 1 else ''})</button>
          </div>"""
    else:
        missing_html = """<div class="missing-row">
            <span class="missing-label">à chercher</span>
            <div class="chips"><span class="chip chip--done">rien ne manque !</span></div>
          </div>"""

    return f"""
        <article class="card" id="{slugify(field['name'])}">
          <div class="card-head">
            <h3>{esc(field['name'])}</h3>
            <span class="tag">{type_label}</span>
          </div>
          <div class="gauge" style="--pct:{field['pct']}%">
            <div class="gauge-fill"></div>
            <span class="gauge-label">{field['pct']} %</span>
          </div>
          {missing_html}
          {present_row}
          {note_html}
        </article>"""


def build_html(nouns, adjectives, source_label=""):
    results = analyze(nouns, adjectives)
    by_tier = {"bien": [], "partiel": [], "non": []}
    for r in results:
        by_tier[r["tier_key"]].append(r)
    for key in by_tier:
        by_tier[key].sort(key=lambda r: r["pct"])  # weakest first: what to tackle first

    priority = sorted(results, key=lambda r: r["pct"])[:8]
    priority_html = "".join(
        f'<li><a href="#{slugify(r["name"])}">{esc(r["name"])}</a> '
        f'<span class="prio-pct">{r["pct"]}&nbsp;%</span></li>'
        for r in priority
    )

    sections_html = ""
    for key, label, _ in TIER_BOUNDS:
        cards = "".join(card_html(r) for r in by_tier[key])
        sections_html += f"""
    <section class="tier tier--{key}">
      <h2 class="tier-node">{label} <span class="count">{len(by_tier[key])} champs</span></h2>
      <div class="cards">{cards}
      </div>
    </section>"""

    generated_line = f"<p>généré {esc(source_label)}</p>" if source_label else ""

    return TEMPLATE.format(
        n_nouns=len(nouns), n_adj=len(adjectives),
        n_fields=len(results),
        priority_html=priority_html,
        sections_html=sections_html,
        generated_line=generated_line,
    )


TEMPLATE = """<title>Lully — champs lexicaux à compléter</title>
<style>
  @media (prefers-color-scheme: light) {{ :root {{ color-scheme: light; }} }}
  @media (prefers-color-scheme: dark) {{ :root {{ color-scheme: dark; }} }}

  :root {{
    --paper: #e7e2d2;
    --paper-raised: #f4f0e2;
    --ink: #22291f;
    --ink-soft: #5a5d4d;
    --line: #c9c2a4;
    --bien: #3f6b45;
    --bien-soft: #dbe6d7;
    --partiel: #a2793a;
    --partiel-soft: #ecdfc5;
    --non: #8c3f33;
    --non-soft: #ecd8d2;
    --missing: #8c3f33;
    --missing-soft: #f3e2dc;
    --font-display: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif;
    --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --paper: #1b211c; --paper-raised: #232921; --ink: #e9e4d3; --ink-soft: #a9a491;
      --line: #3c4335; --bien: #7cb583; --bien-soft: #2b3a2c; --partiel: #d3a463;
      --partiel-soft: #3a3221; --non: #cf7767; --non-soft: #3c2723;
      --missing: #d98871; --missing-soft: #3a2924;
    }}
  }}
  :root[data-theme="dark"] {{
    --paper: #1b211c; --paper-raised: #232921; --ink: #e9e4d3; --ink-soft: #a9a491;
    --line: #3c4335; --bien: #7cb583; --bien-soft: #2b3a2c; --partiel: #d3a463;
    --partiel-soft: #3a3221; --non: #cf7767; --non-soft: #3c2723;
    --missing: #d98871; --missing-soft: #3a2924;
  }}
  :root[data-theme="light"] {{
    --paper: #e7e2d2; --paper-raised: #f4f0e2; --ink: #22291f; --ink-soft: #5a5d4d;
    --line: #c9c2a4; --bien: #3f6b45; --bien-soft: #dbe6d7; --partiel: #a2793a;
    --partiel-soft: #ecdfc5; --non: #8c3f33; --non-soft: #ecd8d2;
    --missing: #8c3f33; --missing-soft: #f3e2dc;
  }}

  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--paper);
    color: var(--ink);
    font-family: var(--font-body);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  main {{ max-width: 880px; margin: 0 auto; padding: 2.25rem 1.25rem 5rem; }}

  header.page-head {{ margin-bottom: 2.25rem; }}
  .eyebrow {{
    font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--ink-soft);
  }}
  h1 {{
    font-family: var(--font-display); font-weight: 600;
    font-size: clamp(1.6rem, 5vw, 2.35rem); margin: 0.35rem 0 0.6rem; text-wrap: balance;
  }}
  .lede {{ max-width: 62ch; color: var(--ink-soft); font-size: 0.98rem; }}
  .lede b {{ color: var(--ink); font-weight: 600; }}

  .stats {{ display: flex; gap: 1.5rem; margin-top: 1.15rem; flex-wrap: wrap; }}
  .stat {{ font-family: var(--font-mono); font-variant-numeric: tabular-nums; }}
  .stat .n {{ font-size: 1.3rem; color: var(--ink); }}
  .stat .l {{
    display: block; font-size: 0.68rem; color: var(--ink-soft);
    letter-spacing: 0.06em; text-transform: uppercase;
  }}

  .priority {{
    margin: 1.5rem 0 0;
    padding: 0.9rem 1rem;
    background: var(--missing-soft);
    border-left: 3px solid var(--missing);
    border-radius: 0 3px 3px 0;
  }}
  .priority h2 {{
    font-family: var(--font-display); font-size: 1.05rem; margin: 0 0 0.5rem;
  }}
  .priority ol {{ margin: 0; padding-left: 1.2rem; columns: 2; column-gap: 1.5rem; }}
  .priority li {{ font-size: 0.88rem; margin-bottom: 0.25rem; break-inside: avoid; }}
  .priority a {{ color: var(--ink); }}
  .prio-pct {{ font-family: var(--font-mono); font-size: 0.75rem; color: var(--ink-soft); }}

  .tree {{ position: relative; margin-left: 0.6rem; padding-left: 1.6rem; border-left: 3px solid var(--line); margin-top: 2rem; }}
  .tier {{ position: relative; margin-bottom: 2.75rem; }}
  .tier:last-child {{ margin-bottom: 0; }}
  .tier-node {{
    position: relative; display: flex; align-items: baseline; gap: 0.6rem;
    font-family: var(--font-display); font-size: 1.28rem; font-weight: 600;
    margin: 0 0 1.1rem; padding-bottom: 0.5rem; border-bottom: 1px solid var(--line);
  }}
  .tier-node::before {{
    content: ""; position: absolute; left: -1.98rem; top: 0.55em;
    width: 1.3rem; height: 3px; background: var(--dot);
  }}
  .tier-node::after {{
    content: ""; position: absolute; left: -2.35rem; top: 0.35em;
    width: 0.85rem; height: 0.85rem; border-radius: 50%;
    background: var(--paper); border: 3px solid var(--dot);
  }}
  .tier--bien {{ --dot: var(--bien); }}
  .tier--partiel {{ --dot: var(--partiel); }}
  .tier--non {{ --dot: var(--non); }}
  .tier-node .count {{ font-family: var(--font-mono); font-size: 0.85rem; font-weight: 400; color: var(--ink-soft); }}

  .cards {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 0.85rem; }}

  .card {{
    background: var(--paper-raised); border: 1px solid var(--line);
    border-left: 4px solid var(--dot); border-radius: 3px; padding: 0.85rem 0.95rem 0.95rem;
    scroll-margin-top: 1rem;
  }}
  .card-head {{ display: flex; justify-content: space-between; align-items: baseline; gap: 0.5rem; margin-bottom: 0.55rem; }}
  .card h3 {{ font-family: var(--font-display); font-size: 1.02rem; font-weight: 600; margin: 0; text-wrap: balance; }}
  .tag {{
    flex: none; font-family: var(--font-mono); font-size: 0.62rem; letter-spacing: 0.05em;
    text-transform: uppercase; color: var(--ink-soft); border: 1px solid var(--line);
    border-radius: 2px; padding: 0.1rem 0.35rem; white-space: nowrap;
  }}
  .gauge {{
    position: relative; height: 0.55rem; background: var(--paper); border: 1px solid var(--line);
    border-radius: 2px; margin-bottom: 0.75rem; overflow: hidden;
  }}
  .gauge-fill {{ position: absolute; inset: 0; width: var(--pct); background: var(--dot); border-radius: 2px 0 0 2px; }}
  .gauge-label {{
    position: absolute; right: 0.35rem; top: -1.2rem; font-family: var(--font-mono);
    font-size: 0.7rem; font-variant-numeric: tabular-nums; color: var(--ink-soft);
  }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 0.3rem; }}
  .chip {{ font-size: 0.76rem; border-radius: 20px; padding: 0.12rem 0.55rem; }}
  .chip--missing {{
    background: transparent; color: var(--missing); border: 1px dashed var(--missing);
  }}
  .chip--done {{ font-style: italic; color: var(--ink-soft); border: 1px solid var(--line); }}
  .chip--present {{ background: var(--paper); color: var(--ink-soft); border: 1px solid var(--line); }}
  .missing-row {{ margin-bottom: 0.5rem; }}
  .missing-label, .present-label {{
    display: block; font-family: var(--font-mono); font-size: 0.65rem; letter-spacing: 0.04em;
    text-transform: uppercase; margin-bottom: 0.3rem;
  }}
  .missing-label {{ color: var(--missing); }}
  .present-label {{ color: var(--ink-soft); }}
  .present-row {{ margin-top: 0.55rem; padding-top: 0.55rem; border-top: 1px dashed var(--line); }}
  .note {{ margin: 0.55rem 0 0; font-size: 0.78rem; color: var(--ink-soft); font-style: italic; }}

  .reveal-chips:empty {{ display: none; }}
  .reveal-chips {{ margin-bottom: 0.4rem; }}
  .reveal-btn {{
    font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.02em;
    color: var(--missing); background: var(--missing-soft); border: 1px solid var(--missing);
    border-radius: 20px; padding: 0.28rem 0.7rem; cursor: pointer;
  }}
  .reveal-btn:hover {{ filter: brightness(1.08); }}
  .reveal-btn:disabled {{
    cursor: default; color: var(--ink-soft); background: transparent;
    border-color: var(--line); filter: none;
  }}
  .chip--revealed {{ background: var(--missing-soft); color: var(--missing); border: 1px solid var(--missing); }}
  @media (prefers-reduced-motion: no-preference) {{
    .chip--revealed {{ animation: reveal 0.25s ease-out; }}
    @keyframes reveal {{
      from {{ opacity: 0; transform: translateY(-2px) scale(0.92); }}
      to {{ opacity: 1; transform: none; }}
    }}
  }}

  footer.legend {{
    margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid var(--line);
    font-size: 0.82rem; color: var(--ink-soft); max-width: 62ch;
  }}
  footer.legend p {{ margin: 0 0 0.6rem; }}
  footer.legend a {{ color: var(--missing); }}

  @media (max-width: 480px) {{
    main {{ padding: 1.5rem 0.85rem 4rem; }}
    .tree {{ padding-left: 1.15rem; }}
    .tier-node::before {{ left: -1.5rem; width: 0.9rem; }}
    .tier-node::after {{ left: -1.83rem; }}
    .priority ol {{ columns: 1; }}
  }}
</style>

<main>
  <header class="page-head">
    <p class="eyebrow">Lully · rapport de champs lexicaux</p>
    <h1>Quels mots manquent encore au corpus ?</h1>
    <p class="lede">
      Pour chaque champ, une liste de mots-témoins caractéristiques du domaine est vérifiée
      contre <code>lully/words.py</code>. Essaie de trouver les manquants toi-même — le bouton
      « Révéler un indice » de chaque carte en sort un à la fois si tu sèches, prêt à copier
      dans <code>addwords.py</code>. Ce rapport se régénère à chaque commit qui touche le corpus.
    </p>
    <div class="stats">
      <div class="stat"><span class="n">{n_nouns}</span><span class="l">noms</span></div>
      <div class="stat"><span class="n">{n_adj}</span><span class="l">adjectifs</span></div>
      <div class="stat"><span class="n">{n_fields}</span><span class="l">champs suivis</span></div>
    </div>
    <div class="priority">
      <h2>Par où commencer</h2>
      <ol>{priority_html}</ol>
    </div>
  </header>

  <div class="tree">{sections_html}
  </div>

  <footer class="legend">
    <p><b>Méthode</b> — chaque champ est une liste-témoin de 8 à 30 mots caractéristiques,
    vérifiée mot à mot (insensible à la casse) contre le corpus actuel. Un champ à 90 % n'a
    pas forcément 90 % du vocabulaire français du domaine — seulement 90 % des mots-témoins
    choisis. Les tiers (bien / partiellement / peu couverts) sont recalculés à chaque
    génération, à partir de l'état courant du corpus. Envie de piocher plus large que ces
    33 champs ? Voir les <a href="candidates.html">mots candidats</a> (14&nbsp;000+ noms,
    12&nbsp;000+ adjectifs, tirés du Wiktionnaire), ou la <a href="letters.html">distribution
    par lettre</a> pour repérer un biais plutôt qu'un thème.</p>
    {generated_line}
  </footer>
</main>

<script>
  document.addEventListener("click", function (event) {{
    var btn = event.target.closest(".reveal-btn");
    if (!btn || btn.disabled) return;
    var pool;
    try {{
      pool = JSON.parse(btn.dataset.pool || "[]");
    }} catch (err) {{
      pool = [];
    }}
    if (!pool.length) return;
    var index = Math.floor(Math.random() * pool.length);
    var word = pool.splice(index, 1)[0];
    btn.dataset.pool = JSON.stringify(pool);
    var chip = document.createElement("span");
    chip.className = "chip chip--revealed";
    chip.textContent = word;
    btn.parentElement.querySelector(".reveal-chips").appendChild(chip);
    if (pool.length > 0) {{
      btn.textContent = "\\ud83d\\udd0d R\\u00e9v\\u00e9ler un indice (" + pool.length + " restant" + (pool.length > 1 ? "s" : "") + ")";
    }} else {{
      btn.textContent = "\\u2713 Tout est sorti";
      btn.disabled = true;
    }}
  }});
</script>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--words", default="lully/words.py", help="path to words.py")
    parser.add_argument("--out", default="docs/index.html", help="output HTML path")
    args = parser.parse_args()

    nouns, adjectives = load_words(args.words)

    # Only stamp a "generated" line in CI (GITHUB_SHA set). Local runs leave it
    # blank so re-running this script produces byte-identical output given the
    # same corpus - a wall-clock timestamp here would make every local
    # regeneration a spurious diff against whatever CI last committed.
    commit = os.environ.get("GITHUB_SHA", "")[:7]
    source_label = f"automatiquement (commit {commit})" if commit else ""
    html_out = build_html(nouns, adjectives, source_label)

    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {args.out} ({len(nouns)} nouns, {len(adjectives)} adjectives, "
          f"{len(FIELDS)} fields)")


if __name__ == "__main__":
    main()
