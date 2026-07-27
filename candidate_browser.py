#!/usr/bin/env python3
"""Generate a browsable page of candidate words not yet in lully/words.py.

candidate_words.json is a static list mined once from the kaikki.org French
Wiktionary dump (feminine common nouns, feminine adjectives + regular -er
verb past participles), filtered for decency and basic word-shape validity.
This script re-filters it against the *current* corpus each run, so words
already added by addwords.py drop out of the list automatically, and
renders the rest as a searchable, letter-grouped, reveal-on-demand page.

Usage:
    python candidate_browser.py [--words lully/words.py]
                                 [--candidates candidate_words.json]
                                 [--out docs/candidates.html]
"""
import argparse
import ast
import json
import unicodedata


def load_words(path):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    tree = ast.parse(src, filename=path)
    ns = {}
    exec(compile(tree, path, "exec"), ns)
    return ns["NOUNS"], ns["ADJECTIVES"]


def base_letter(word):
    nf = unicodedata.normalize("NFKD", word[0])
    base = "".join(c for c in nf if not unicodedata.combining(c))
    return base.upper()


def group_by_letter(words):
    groups = {}
    for w in words:
        groups.setdefault(base_letter(w), []).append(w)
    return dict(sorted(groups.items()))


def letters_nav_html(groups, prefix):
    return "".join(
        f'<a href="#{prefix}-{letter}" class="letter-link">{letter}</a>'
        for letter in groups
    )


def letter_sections_html(groups, prefix, type_code):
    sections = []
    for letter, words in groups.items():
        sections.append(f"""
        <div class="letter-group" id="{prefix}-{letter}" data-letter="{letter}" data-type="{type_code}">
          <button type="button" class="letter-btn">
            <span class="letter-big">{letter}</span>
            <span class="letter-count">{len(words)} mots</span>
          </button>
          <div class="chips letter-chips"></div>
        </div>""")
    return "".join(sections)


def build_html(nouns, adjectives):
    noun_groups = group_by_letter(nouns)
    adj_groups = group_by_letter(adjectives)

    all_words = json.dumps(
        [[w, "N", base_letter(w)] for w in nouns] + [[w, "A", base_letter(w)] for w in adjectives],
        ensure_ascii=False,
    )

    return TEMPLATE.format(
        n_nouns=len(nouns), n_adj=len(adjectives),
        noun_nav=letters_nav_html(noun_groups, "n"),
        adj_nav=letters_nav_html(adj_groups, "a"),
        noun_sections=letter_sections_html(noun_groups, "n", "N"),
        adj_sections=letter_sections_html(adj_groups, "a", "A"),
        all_words_json=all_words,
    )


TEMPLATE = """<title>Lully — mots candidats</title>
<style>
  @media (prefers-color-scheme: light) {{ :root {{ color-scheme: light; }} }}
  @media (prefers-color-scheme: dark) {{ :root {{ color-scheme: dark; }} }}

  :root {{
    --paper: #e7e2d2; --paper-raised: #f4f0e2; --ink: #22291f; --ink-soft: #5a5d4d;
    --line: #c9c2a4; --accent: #4d6fa3; --accent-soft: #dde3ee;
    --font-display: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif;
    --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --paper: #1b211c; --paper-raised: #232921; --ink: #e9e4d3; --ink-soft: #a9a491;
      --line: #3c4335; --accent: #8fabd6; --accent-soft: #262d3c;
    }}
  }}
  :root[data-theme="dark"] {{
    --paper: #1b211c; --paper-raised: #232921; --ink: #e9e4d3; --ink-soft: #a9a491;
    --line: #3c4335; --accent: #8fabd6; --accent-soft: #262d3c;
  }}
  :root[data-theme="light"] {{
    --paper: #e7e2d2; --paper-raised: #f4f0e2; --ink: #22291f; --ink-soft: #5a5d4d;
    --line: #c9c2a4; --accent: #4d6fa3; --accent-soft: #dde3ee;
  }}

  * {{ box-sizing: border-box; }}
  html, body {{ margin: 0; padding: 0; }}
  body {{
    background: var(--paper); color: var(--ink); font-family: var(--font-body);
    line-height: 1.5; -webkit-font-smoothing: antialiased;
  }}
  main {{ max-width: 880px; margin: 0 auto; padding: 2.25rem 1.25rem 5rem; }}

  .eyebrow {{
    font-family: var(--font-mono); font-size: 0.72rem; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--ink-soft);
  }}
  h1 {{
    font-family: var(--font-display); font-weight: 600;
    font-size: clamp(1.6rem, 5vw, 2.35rem); margin: 0.35rem 0 0.6rem; text-wrap: balance;
  }}
  .lede {{ max-width: 62ch; color: var(--ink-soft); font-size: 0.98rem; }}
  .lede code {{ color: var(--ink); }}

  .stats {{ display: flex; gap: 1.5rem; margin: 1.15rem 0 1.5rem; flex-wrap: wrap; }}
  .stat {{ font-family: var(--font-mono); font-variant-numeric: tabular-nums; }}
  .stat .n {{ font-size: 1.3rem; color: var(--ink); }}
  .stat .l {{
    display: block; font-size: 0.68rem; color: var(--ink-soft);
    letter-spacing: 0.06em; text-transform: uppercase;
  }}

  .search-box {{ position: relative; margin-bottom: 0.5rem; }}
  .search-box input {{
    width: 100%; font-family: var(--font-body); font-size: 1rem;
    padding: 0.6rem 0.8rem; border: 1px solid var(--line); border-radius: 4px;
    background: var(--paper-raised); color: var(--ink);
  }}
  .search-box input:focus {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
  .search-results {{
    display: none; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.6rem;
    max-height: 40vh; overflow-y: auto; padding: 0.6rem; border: 1px solid var(--line);
    border-radius: 4px; background: var(--paper-raised);
  }}
  .search-results.active {{ display: flex; }}
  .search-hint {{ font-size: 0.8rem; color: var(--ink-soft); margin: 0.4rem 0 1.75rem; }}

  h2.section-title {{
    font-family: var(--font-display); font-size: 1.35rem; font-weight: 600;
    margin: 2.25rem 0 0.75rem; padding-bottom: 0.4rem; border-bottom: 2px solid var(--line);
  }}
  .letter-nav {{
    display: flex; flex-wrap: wrap; gap: 0.3rem; margin-bottom: 1.25rem;
    font-family: var(--font-mono); font-size: 0.8rem;
  }}
  .letter-link {{
    color: var(--accent); border: 1px solid var(--line); border-radius: 3px;
    padding: 0.1rem 0.45rem; text-decoration: none;
  }}
  .letter-group {{ margin-bottom: 0.6rem; scroll-margin-top: 1rem; }}
  .letter-btn {{
    display: flex; align-items: baseline; gap: 0.6rem; width: 100%;
    text-align: left; background: var(--paper-raised); border: 1px solid var(--line);
    border-radius: 4px; padding: 0.5rem 0.8rem; cursor: pointer; color: var(--ink);
  }}
  .letter-btn:hover {{ border-color: var(--accent); }}
  .letter-big {{ font-family: var(--font-display); font-size: 1.15rem; font-weight: 600; }}
  .letter-count {{ font-family: var(--font-mono); font-size: 0.75rem; color: var(--ink-soft); }}
  .letter-btn::after {{
    content: "révéler"; margin-left: auto; font-family: var(--font-mono);
    font-size: 0.7rem; color: var(--accent);
  }}
  .letter-group.open .letter-btn::after {{ content: "masquer"; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 0.3rem; }}
  .letter-chips {{ margin-top: 0.5rem; }}
  .letter-group:not(.open) .letter-chips {{ display: none; }}
  .chip {{
    font-size: 0.8rem; border-radius: 20px; padding: 0.15rem 0.6rem;
    background: var(--accent-soft); border: 1px solid var(--accent); color: var(--ink);
  }}

  footer.legend {{
    margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid var(--line);
    font-size: 0.82rem; color: var(--ink-soft); max-width: 62ch;
  }}
  footer.legend a {{ color: var(--accent); }}

  @media (max-width: 480px) {{
    main {{ padding: 1.5rem 0.85rem 4rem; }}
  }}
</style>

<main>
  <header>
    <p class="eyebrow">Lully · mots candidats</p>
    <h1>Plus de {n_nouns} noms et {n_adj} adjectifs à piocher</h1>
    <p class="lede">
      Mots féminins tirés du Wiktionnaire français (via <a href="https://kaikki.org">kaikki.org</a>),
      pas encore dans <code>lully/words.py</code> — prêts à copier dans <code>addwords.py</code>.
      Cette liste se met à jour toute seule : un mot que tu ajoutes disparaît d'ici au prochain
      commit. Pas de tri par fréquence ici (le Wiktionnaire n'en fournit pas) — c'est du
      classement alphabétique, à parcourir ou à chercher directement.
    </p>
    <div class="stats">
      <div class="stat"><span class="n">{n_nouns}</span><span class="l">noms candidats</span></div>
      <div class="stat"><span class="n">{n_adj}</span><span class="l">adjectifs candidats</span></div>
    </div>
    <div class="search-box">
      <input type="text" id="search" placeholder="chercher un mot ou un fragment (ex : phobie, -logie, astro)" autocomplete="off">
    </div>
    <div class="search-results" id="search-results"></div>
    <p class="search-hint">La recherche filtre en direct sur les deux listes ci-dessous.</p>
  </header>

  <h2 class="section-title">Noms ({n_nouns})</h2>
  <div class="letter-nav">{noun_nav}</div>
  <div id="noun-groups">{noun_sections}</div>

  <h2 class="section-title">Adjectifs ({n_adj})</h2>
  <div class="letter-nav">{adj_nav}</div>
  <div id="adj-groups">{adj_sections}</div>

  <footer class="legend">
    <p>Régénéré à chaque commit qui touche <code>lully/words.py</code> ou
    <code>candidate_words.json</code>. Voir aussi le
    <a href="index.html">rapport de champs lexicaux</a> pour une recherche plus ciblée par thème,
    ou la <a href="letters.html">distribution par lettre</a>.</p>
  </footer>
</main>

<script type="application/json" id="all-words-data">{all_words_json}</script>
<script>
  var ALL_WORDS = JSON.parse(document.getElementById("all-words-data").textContent);

  // group once by "type|LETTER" so per-letter reveal doesn't rescan 27k words each click
  var BY_GROUP = {{}};
  ALL_WORDS.forEach(function (pair) {{
    var key = pair[1] + "|" + pair[2];
    (BY_GROUP[key] = BY_GROUP[key] || []).push(pair[0]);
  }});

  document.addEventListener("click", function (event) {{
    var btn = event.target.closest(".letter-btn");
    if (!btn) return;
    var group = btn.closest(".letter-group");
    var wasOpen = group.classList.contains("open");
    group.classList.toggle("open");
    if (!wasOpen && !group.dataset.rendered) {{
      var key = group.dataset.type + "|" + group.dataset.letter;
      var words = BY_GROUP[key] || [];
      var container = group.querySelector(".letter-chips");
      var frag = document.createDocumentFragment();
      words.forEach(function (w) {{
        var chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = w;
        frag.appendChild(chip);
      }});
      container.appendChild(frag);
      group.dataset.rendered = "1";
    }}
  }});
  var searchInput = document.getElementById("search");
  var resultsBox = document.getElementById("search-results");

  searchInput.addEventListener("input", function () {{
    var q = searchInput.value.trim().toLowerCase();
    resultsBox.textContent = "";
    if (q.length < 2) {{
      resultsBox.classList.remove("active");
      return;
    }}
    var matches = [];
    for (var i = 0; i < ALL_WORDS.length && matches.length < 300; i++) {{
      if (ALL_WORDS[i][0].toLowerCase().indexOf(q) !== -1) matches.push(ALL_WORDS[i]);
    }}
    var frag = document.createDocumentFragment();
    if (matches.length === 0) {{
      var none = document.createElement("span");
      none.className = "search-hint";
      none.textContent = "aucun résultat";
      frag.appendChild(none);
    }} else {{
      matches.forEach(function (pair) {{
        var chip = document.createElement("span");
        chip.className = "chip";
        chip.textContent = pair[0] + " · " + (pair[1] === "N" ? "nom" : "adj.");
        frag.appendChild(chip);
      }});
    }}
    resultsBox.appendChild(frag);
    resultsBox.classList.add("active");
  }});
</script>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--words", default="lully/words.py")
    parser.add_argument("--candidates", default="candidate_words.json")
    parser.add_argument("--out", default="docs/candidates.html")
    args = parser.parse_args()

    nouns, adjectives = load_words(args.words)
    nouns_lc = {w.lower() for w in nouns}
    adj_lc = {w.lower() for w in adjectives}

    with open(args.candidates, encoding="utf-8") as f:
        pool = json.load(f)

    remaining_nouns = [w.title() for w in pool["nouns"] if w.lower() not in nouns_lc]
    remaining_adj = [w.title() for w in pool["adjectives"] if w.lower() not in adj_lc]
    remaining_nouns.sort()
    remaining_adj.sort()

    html_out = build_html(remaining_nouns, remaining_adj)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {args.out} ({len(remaining_nouns)} noun candidates, "
          f"{len(remaining_adj)} adjective candidates)")


if __name__ == "__main__":
    main()
