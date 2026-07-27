#!/usr/bin/env python3
"""Compare the first-letter distribution of lully/words.py against a
broad, uncurated reference sample (candidate_words.json, mined from
French Wiktionary) — one dumbbell chart per word type, to spot which
letters Lucas's own curation over- or under-represents relative to
French vocabulary at large.

Usage:
    python letter_distribution.py [--words lully/words.py]
                                   [--candidates candidate_words.json]
                                   [--out docs/letters.html]
"""
import argparse
import ast
import html as html_lib
import json
import unicodedata
from collections import Counter

SERIES_LULLY = {"light": "#1baf7a", "dark": "#199e70"}
SERIES_REF = {"light": "#2a78d6", "dark": "#3987e5"}


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


def distribution(words):
    counts = Counter(base_letter(w) for w in words)
    total = sum(counts.values())
    return counts, total


def esc(s):
    return html_lib.escape(s, quote=True)


def build_rows(lully_words, ref_words, scale_max):
    lully_counts, lully_total = distribution(lully_words)
    ref_counts, ref_total = distribution(ref_words)
    letters = sorted(set(lully_counts) | set(ref_counts))

    rows = []
    for letter in letters:
        l_n = lully_counts.get(letter, 0)
        r_n = ref_counts.get(letter, 0)
        l_pct = l_n / lully_total * 100 if lully_total else 0
        r_pct = r_n / ref_total * 100 if ref_total else 0
        delta = l_pct - r_pct
        left = min(l_pct, r_pct) / scale_max * 100
        width = abs(l_pct - r_pct) / scale_max * 100
        rows.append(f"""
        <div class="letter-row">
          <span class="letter-label">{letter}</span>
          <div class="track">
            <div class="connector" style="left:{left:.2f}%; width:{width:.2f}%"></div>
            <div class="dot dot--ref" style="left:{r_pct / scale_max * 100:.2f}%"
                 title="Référence : {r_n} mots ({r_pct:.1f} %)"></div>
            <div class="dot dot--lully" style="left:{l_pct / scale_max * 100:.2f}%"
                 title="Corpus Lully : {l_n} mots ({l_pct:.1f} %)"></div>
          </div>
          <span class="value-labels"><b>{l_pct:.1f}%</b> <span class="vs">vs</span> {r_pct:.1f}%
            <span class="delta {'delta--over' if delta > 0 else 'delta--under' if delta < 0 else ''}">{'+' if delta > 0 else ''}{delta:.1f}</span>
          </span>
        </div>""")

    table_rows = "".join(
        f"<tr><td>{letter}</td><td>{lully_counts.get(letter, 0)}</td>"
        f"<td>{lully_counts.get(letter, 0) / lully_total * 100:.1f}%</td>"
        f"<td>{ref_counts.get(letter, 0)}</td>"
        f"<td>{ref_counts.get(letter, 0) / ref_total * 100:.1f}%</td>"
        f"<td>{(lully_counts.get(letter, 0) / lully_total * 100 - ref_counts.get(letter, 0) / ref_total * 100):+.1f}</td></tr>"
        for letter in letters
    )

    # biggest over/under representations, for the callout
    deltas = []
    for letter in letters:
        l_pct = lully_counts.get(letter, 0) / lully_total * 100 if lully_total else 0
        r_pct = ref_counts.get(letter, 0) / ref_total * 100 if ref_total else 0
        deltas.append((letter, l_pct - r_pct))
    deltas.sort(key=lambda x: x[1])
    under = deltas[:3]
    over = deltas[-3:][::-1]

    return "".join(rows), table_rows, over, under, lully_total, ref_total


def section_html(title, type_label, lully_words, ref_words, anchor):
    scale_max = max(
        max(distribution(lully_words)[0].values(), default=1) / max(distribution(lully_words)[1], 1),
        max(distribution(ref_words)[0].values(), default=1) / max(distribution(ref_words)[1], 1),
    ) * 100
    scale_max = scale_max * 1.15  # headroom so the extreme dot isn't flush against the edge

    rows_html, table_rows, over, under, lully_total, ref_total = build_rows(lully_words, ref_words, scale_max)

    over_chips = "".join(f'<span class="chip chip--over">{l} +{d:.1f}</span>' for l, d in over if d > 0)
    under_chips = "".join(f'<span class="chip chip--under">{l} {d:.1f}</span>' for l, d in under if d < 0)

    return f"""
  <section class="letter-section" id="{anchor}">
    <h2 class="section-title">{title} <span class="section-count">{lully_total} vs {ref_total} (référence)</span></h2>
    <div class="callouts">
      <div class="callout"><span class="callout-label">Sur-représentées</span><div class="chips">{over_chips or '<span class="chip">—</span>'}</div></div>
      <div class="callout"><span class="callout-label">Sous-représentées</span><div class="chips">{under_chips or '<span class="chip">—</span>'}</div></div>
    </div>
    <div class="legend">
      <span><span class="swatch swatch--lully"></span> Corpus Lully</span>
      <span><span class="swatch swatch--ref"></span> Référence (pool Wiktionary, non triée par Lucas)</span>
    </div>
    <div class="chart">{rows_html}
    </div>
    <details class="table-toggle">
      <summary>Voir le tableau</summary>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Lettre</th><th>Lully (n)</th><th>Lully (%)</th><th>Référence (n)</th><th>Référence (%)</th><th>Δ</th></tr></thead>
          <tbody>{table_rows}</tbody>
        </table>
      </div>
    </details>
  </section>"""


def build_html(nouns, adjectives, ref_nouns, ref_adjectives):
    noun_section = section_html("Noms", "N", nouns, ref_nouns, "noms")
    adj_section = section_html("Adjectifs", "A", adjectives, ref_adjectives, "adjectifs")
    return TEMPLATE.format(noun_section=noun_section, adj_section=adj_section)


TEMPLATE = """<title>Lully — distribution par lettre</title>
<style>
  @media (prefers-color-scheme: light) {{ :root {{ color-scheme: light; }} }}
  @media (prefers-color-scheme: dark) {{ :root {{ color-scheme: dark; }} }}

  :root {{
    --paper: #e7e2d2; --paper-raised: #f4f0e2; --ink: #22291f; --ink-soft: #5a5d4d;
    --line: #c9c2a4;
    --series-lully: #1baf7a; --series-ref: #2a78d6;
    --over-soft: #f3e2dc; --over: #8c3f33;
    --under-soft: #dde3ee; --under: #2a78d6;
    --font-display: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif;
    --font-body: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{
      --paper: #1b211c; --paper-raised: #232921; --ink: #e9e4d3; --ink-soft: #a9a491;
      --line: #3c4335; --series-lully: #199e70; --series-ref: #3987e5;
      --over-soft: #3c2723; --over: #cf7767; --under-soft: #262d3c; --under: #8fabd6;
    }}
  }}
  :root[data-theme="dark"] {{
    --paper: #1b211c; --paper-raised: #232921; --ink: #e9e4d3; --ink-soft: #a9a491;
    --line: #3c4335; --series-lully: #199e70; --series-ref: #3987e5;
    --over-soft: #3c2723; --over: #cf7767; --under-soft: #262d3c; --under: #8fabd6;
  }}
  :root[data-theme="light"] {{
    --paper: #e7e2d2; --paper-raised: #f4f0e2; --ink: #22291f; --ink-soft: #5a5d4d;
    --line: #c9c2a4; --series-lully: #1baf7a; --series-ref: #2a78d6;
    --over-soft: #f3e2dc; --over: #8c3f33; --under-soft: #dde3ee; --under: #2a78d6;
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
  .lede {{ max-width: 62ch; color: var(--ink-soft); font-size: 0.98rem; margin-bottom: 2rem; }}
  .lede code {{ color: var(--ink); }}

  h2.section-title {{
    font-family: var(--font-display); font-size: 1.35rem; font-weight: 600;
    display: flex; align-items: baseline; gap: 0.6rem; flex-wrap: wrap;
    margin: 2.5rem 0 1rem; padding-bottom: 0.4rem; border-bottom: 2px solid var(--line);
  }}
  .section-count {{ font-family: var(--font-mono); font-size: 0.78rem; font-weight: 400; color: var(--ink-soft); }}

  .callouts {{ display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1rem; }}
  .callout {{ flex: 1 1 220px; }}
  .callout-label {{
    display: block; font-family: var(--font-mono); font-size: 0.68rem; letter-spacing: 0.05em;
    text-transform: uppercase; color: var(--ink-soft); margin-bottom: 0.35rem;
  }}
  .chip {{ font-size: 0.8rem; border-radius: 20px; padding: 0.15rem 0.6rem; border: 1px solid var(--line); }}
  .chip--over {{ background: var(--over-soft); color: var(--over); border-color: var(--over); }}
  .chip--under {{ background: var(--under-soft); color: var(--under); border-color: var(--under); }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 0.3rem; }}

  .legend {{
    display: flex; gap: 1.25rem; flex-wrap: wrap; font-size: 0.8rem;
    color: var(--ink-soft); margin-bottom: 1.1rem;
  }}
  .legend span {{ display: inline-flex; align-items: center; gap: 0.4rem; }}
  .swatch {{ width: 0.65rem; height: 0.65rem; border-radius: 50%; display: inline-block; }}
  .swatch--lully {{ background: var(--series-lully); }}
  .swatch--ref {{ background: var(--series-ref); }}

  .chart {{ display: flex; flex-direction: column; gap: 0.55rem; }}
  .letter-row {{ display: grid; grid-template-columns: 1.4rem 1fr auto; align-items: center; gap: 0.7rem; }}
  .letter-label {{ font-family: var(--font-display); font-weight: 600; font-size: 0.95rem; text-align: center; }}
  .track {{
    position: relative; height: 1.15rem; background: var(--paper-raised);
    border-radius: 3px; border: 1px solid var(--line);
  }}
  .connector {{ position: absolute; top: 50%; height: 2px; background: var(--ink-soft); transform: translateY(-50%); opacity: 0.5; }}
  .dot {{
    position: absolute; top: 50%; width: 11px; height: 11px; border-radius: 50%;
    transform: translate(-50%, -50%); border: 2px solid var(--paper-raised);
  }}
  .dot--lully {{ background: var(--series-lully); }}
  .dot--ref {{ background: var(--series-ref); }}
  .value-labels {{
    font-family: var(--font-mono); font-size: 0.72rem; color: var(--ink-soft);
    white-space: nowrap; text-align: right;
  }}
  .value-labels b {{ color: var(--ink); font-weight: 600; }}
  .value-labels .vs {{ opacity: 0.55; }}
  .delta {{ display: inline-block; min-width: 2.6rem; text-align: right; }}
  .delta--over {{ color: var(--over); }}
  .delta--under {{ color: var(--under); }}

  .table-toggle {{ margin-top: 1.5rem; font-size: 0.85rem; }}
  .table-toggle summary {{ cursor: pointer; color: var(--ink-soft); }}
  .table-wrap {{ overflow-x: auto; margin-top: 0.6rem; }}
  table {{ border-collapse: collapse; width: 100%; font-size: 0.82rem; font-variant-numeric: tabular-nums; }}
  th, td {{ text-align: right; padding: 0.3rem 0.6rem; border-bottom: 1px solid var(--line); }}
  th:first-child, td:first-child {{ text-align: left; font-family: var(--font-display); font-weight: 600; }}
  th {{ font-family: var(--font-mono); font-size: 0.68rem; text-transform: uppercase; color: var(--ink-soft); font-weight: 400; }}

  footer.legend-note {{
    margin-top: 3rem; padding-top: 1.25rem; border-top: 1px solid var(--line);
    font-size: 0.82rem; color: var(--ink-soft); max-width: 62ch;
  }}
  footer.legend-note a {{ color: var(--series-ref); }}

  @media (max-width: 480px) {{
    main {{ padding: 1.5rem 0.85rem 4rem; }}
    .value-labels {{ font-size: 0.66rem; }}
  }}
</style>

<main>
  <header>
    <p class="eyebrow">Lully · distribution par lettre</p>
    <h1>Ton corpus favorise-t-il certaines lettres ?</h1>
    <p class="lede">
      Chaque ligne compare, pour une lettre donnée, sa part dans <code>lully/words.py</code>
      (point vert) contre sa part dans le grand bassin de mots du Wiktionnaire non trié
      par toi (point bleu, <code>candidate_words.json</code>) — un échantillon large et
      indépendant de tes propres choix, pas "tout le français", mais un bon témoin neutre.
      Un point vert à droite du bleu = lettre sur-représentée chez toi ; à gauche = sous-représentée.
    </p>
  </header>
  {noun_section}
  {adj_section}
  <footer class="legend-note">
    <p>Voir aussi le <a href="index.html">rapport de champs lexicaux</a> et les
    <a href="candidates.html">mots candidats</a>. Régénéré à chaque commit qui touche
    <code>lully/words.py</code>.</p>
  </footer>
</main>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--words", default="lully/words.py")
    parser.add_argument("--candidates", default="candidate_words.json")
    parser.add_argument("--out", default="docs/letters.html")
    args = parser.parse_args()

    nouns, adjectives = load_words(args.words)
    with open(args.candidates, encoding="utf-8") as f:
        pool = json.load(f)

    html_out = build_html(nouns, adjectives, pool["nouns"], pool["adjectives"])
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
