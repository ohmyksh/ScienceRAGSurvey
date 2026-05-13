#!/usr/bin/env python3
"""Render the full HTML site from data/papers.json.

Outputs:
  index.html                — landing page with K×O grid + search
  about.html                — survey context + methodology
  browse.html               — full paper browser with client-side filter
  cell/<K>.<O>.html         — 12 K×O cell pages
  domain/<dom>.html         — 8 domain pages
  topics/<type>.html        — 4 type pages (method/benchmark/dataset/survey)
"""
import html
import json
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path('/gallery_millet/yerim.oh/ScienceRAGServey/site')
papers = json.loads((ROOT / 'data/papers.json').read_text())

# ---------- Reference tables (mirror generate_content.py) ----------
K_LABELS = {
    'K1': ('Primary Literature', 'Peer-reviewed papers, preprints, scientific corpora (PubMed, arXiv, S2ORC, ChemRxiv, bioRxiv).'),
    'K2': ('Curated Knowledge Base', 'Community-maintained structured records (PubChem, RCSB PDB, AlphaFold DB, ChEMBL, UMLS, PrimeKG, Materials Project, OQMD, AFLOW).'),
    'K3': ('Observational & Experimental', 'Raw modality data: images, spectra, sequencing, time-series (cryo-EM, mass spec, telescope archives, EHR images).'),
    'K4': ('Tacit Knowledge', 'Institutional memory (RHIC, DUNE, CMS), lab protocols, private EHRs, governmental/industry process docs. ★ Novelty axis.'),
}
O_LABELS = {
    'O1': ('Ground', 'Single-source grounding: retrieve, cite, answer over one corpus.'),
    'O2': ('Synthesis', 'Multi-source integration, claim verification across documents.'),
    'O3': ('Hypothesis', 'Generate new scientific candidates — molecules, mechanisms, parameters.'),
}
DOMAIN_LABELS = {
    'bio': 'Biology', 'chem': 'Chemistry', 'medical': 'Medicine',
    'material': 'Materials Science', 'physics': 'Physics', 'earth': 'Earth Science',
    'astronomy': 'Astronomy', 'Quantum': 'Quantum', 'general': 'General Science',
}
DOMAIN_EMOJI = {
    'bio': '🧬', 'chem': '⚗️', 'medical': '🩺', 'material': '🪨',
    'physics': '⚛️', 'earth': '🌍', 'astronomy': '🔭', 'Quantum': '🌀', 'general': '📚',
}
TYPE_LABELS = {
    'Method': 'Methods', 'benchmark': 'Benchmarks',
    'dataset': 'Datasets', 'summary': 'Surveys',
}

# ---------- Group ----------
by_cell = defaultdict(list)
by_dom = defaultdict(list)
by_type = defaultdict(list)
for p in papers:
    for c in p.get('ko_cells', []):
        by_cell[c].append(p)
    for d in p.get('domain', []):
        by_dom[d].append(p)
    by_type[p.get('type', 'unknown')].append(p)


def esc(s):
    if s is None:
        return ''
    return html.escape(str(s))


def year_sort(p):
    y = p.get('year')
    try:
        return -int(y)
    except (TypeError, ValueError):
        return 0


# ---------- Common HTML pieces ----------
def page_head(title, base='', desc='Scientific RAG Hub — a curated catalog of retrieval-augmented generation systems for scientific discovery.'):
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} — Scientific RAG Hub</title>
<meta name="description" content="{esc(desc)}">
<link rel="stylesheet" href="{base}static/style.css">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Ctext y='52' font-size='52'%3E%F0%9F%94%AC%3C/text%3E%3C/svg%3E">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a href="{base}index.html" class="logo">
      <span class="logo-mark">🔬</span>
      <span class="logo-text">Scientific RAG Hub</span>
    </a>
    <nav class="nav">
      <a href="{base}index.html">Home</a>
      <a href="{base}browse.html">Browse</a>
      <a href="{base}index.html#grid">K×O Grid</a>
      <a href="{base}index.html#domains">Domains</a>
      <a href="{base}about.html">About</a>
      <a href="{base}llms.txt" title="LLM-friendly index">llms.txt</a>
    </nav>
  </div>
</header>
<main>
'''


PAGE_FOOT = '''</main>
<footer class="site-footer">
  <div class="wrap">
    <p>
      <strong>Scientific RAG Hub</strong> — companion catalog to the TPAMI 2026 survey
      <em>"Scientific Retrieval-Augmented Generation: A Survey through Knowledge Source and Scientific Mission"</em>
      by Oh et al. (Vision and Learning Lab, Seoul National University).
    </p>
    <p class="links">
      <a href="llms.txt">llms.txt</a> ·
      <a href="llms-full.txt">llms-full.txt</a> ·
      <a href="data/papers.json">papers.json</a> ·
      <a href="about.html">About</a>
    </p>
  </div>
</footer>
</body>
</html>
'''


def paper_card(p, base=''):
    title = esc(p.get('title') or p.get('bib_key', '?'))
    url = p.get('paper_link') or ''
    venue = esc(p.get('venue', ''))
    year = esc(p.get('year', ''))
    method = esc(p.get('method', ''))
    note = (p.get('note') or p.get('ko_note') or '').strip()
    if len(note) > 280:
        note = note[:277] + '…'
    note = esc(note)
    cells = p.get('ko_cells', [])
    domains = p.get('domain', [])
    typ = p.get('type', '')
    modality = p.get('modality', [])

    title_html = f'<a href="{esc(url)}" target="_blank" rel="noopener">{title} ↗</a>' if url else title
    meta_parts = []
    if method and method != title:
        meta_parts.append(f'<span class="meta-method">{method}</span>')
    if venue:
        meta_parts.append(f'<span class="meta-venue">{venue}</span>')
    if year:
        meta_parts.append(f'<span class="meta-year">{year}</span>')
    meta = ' · '.join(meta_parts)

    tag_html = []
    for c in cells:
        tag_html.append(f'<a href="{base}cell/{c}.html" class="tag tag-cell">{c}</a>')
    for d in domains:
        tag_html.append(f'<a href="{base}domain/{d}.html" class="tag tag-domain">{DOMAIN_EMOJI.get(d, "")}{esc(DOMAIN_LABELS.get(d, d))}</a>')
    if typ and typ != 'unknown':
        tag_html.append(f'<a href="{base}topics/{typ.lower()}.html" class="tag tag-type">{esc(TYPE_LABELS.get(typ, typ))}</a>')
    for m in modality:
        if m and m != 'Text':
            tag_html.append(f'<span class="tag tag-mod">{esc(m)}</span>')
    if p.get('cross_source'):
        tag_html.append('<span class="tag tag-xs">★ cross-source</span>')

    return f'''<article class="card">
  <h3 class="card-title">{title_html}</h3>
  {f'<div class="card-meta">{meta}</div>' if meta else ''}
  {f'<p class="card-note">{note}</p>' if note else ''}
  <div class="card-tags">{''.join(tag_html)}</div>
</article>
'''


# ---------- index.html ----------
def render_index():
    parts = [page_head('Home', base='')]
    parts.append(f'''
<section class="hero">
  <div class="wrap">
    <p class="eyebrow">AI for Science · Retrieval-Augmented Generation</p>
    <h1>The catalog of scientific RAG systems, organized by Knowledge × Mission.</h1>
    <p class="lede">
      <strong>{len(papers)}</strong> methods, benchmarks, and datasets across
      <strong>{len(by_dom)}</strong> scientific domains —
      classified by a dual-axis taxonomy of Knowledge Source (K) × Operational Objective (O).
      Companion to the TPAMI 2026 survey by Oh et al.
    </p>
    <div class="hero-search">
      <input id="q" type="search" placeholder="Search by title, method, dataset, venue, or tag…" autofocus>
      <span class="hero-search-hint">↵ to filter on <a href="browse.html">Browse</a></span>
    </div>
    <div class="hero-cta">
      <a href="#grid" class="btn">Explore K×O grid</a>
      <a href="browse.html" class="btn btn-secondary">Browse all {len(papers)}</a>
      <a href="about.html" class="btn btn-ghost">Read about the taxonomy</a>
    </div>
  </div>
</section>

<section id="grid" class="ko-grid-section">
  <div class="wrap">
    <h2 class="section-title">The K×O Grid — 12 cells</h2>
    <p class="section-sub">
      Each cell pairs a <em>knowledge source</em> (K, row) with an <em>operational objective</em> (O, column).
      Cell counts include cross-listed cross-source papers. Sparse cells <strong>[K3.O3]</strong> and
      <strong>[K4.O3]</strong> are explicit frontier opportunities in §11.
    </p>
    <table class="ko-grid">
      <thead>
        <tr>
          <th class="corner"></th>
''')
    for O in ['O1', 'O2', 'O3']:
        on, od = O_LABELS[O]
        parts.append(f'          <th class="o-head"><span class="cell-axis">{O}</span> {esc(on)}<span class="cell-axis-desc">{esc(od)}</span></th>\n')
    parts.append('        </tr>\n      </thead>\n      <tbody>\n')

    for K in ['K1', 'K2', 'K3', 'K4']:
        kn, kd = K_LABELS[K]
        parts.append(f'        <tr>\n          <th class="k-head"><span class="cell-axis">{K}</span> {esc(kn)}<span class="cell-axis-desc">{esc(kd)}</span></th>\n')
        for O in ['O1', 'O2', 'O3']:
            cell = f'{K}.{O}'
            ps = by_cell.get(cell, [])
            n = len(ps)
            heat = 'heat-zero' if n == 0 else 'heat-low' if n < 5 else 'heat-mid' if n < 20 else 'heat-high'
            top = sorted(ps, key=year_sort)[:3]
            top_html = '\n'.join(
                f'<li>{esc((p.get("method") or p.get("title") or "?")[:60])}</li>' for p in top
            )
            frontier = ' frontier' if (n <= 3 and K in ('K3', 'K4') and O == 'O3') else ''
            parts.append(f'''          <td class="ko-cell {heat}{frontier}">
            <a href="cell/{cell}.html" class="cell-link">
              <span class="cell-id">[{cell}]</span>
              <span class="cell-count">{n}</span>
              <ul class="cell-top">{top_html}</ul>
            </a>
          </td>
''')
        parts.append('        </tr>\n')
    parts.append('      </tbody>\n    </table>\n  </div>\n</section>\n')

    # Domains row
    parts.append('''
<section id="domains" class="domains-section">
  <div class="wrap">
    <h2 class="section-title">By scientific domain</h2>
    <div class="domain-grid">
''')
    for d, label in DOMAIN_LABELS.items():
        if d not in by_dom:
            continue
        n = len(by_dom[d])
        parts.append(f'''      <a href="domain/{d}.html" class="domain-card">
        <span class="domain-emoji">{DOMAIN_EMOJI.get(d, "")}</span>
        <span class="domain-name">{esc(label)}</span>
        <span class="domain-count">{n} entries</span>
      </a>
''')
    parts.append('    </div>\n  </div>\n</section>\n')

    # Type row
    parts.append('''
<section class="types-section">
  <div class="wrap">
    <h2 class="section-title">By resource type</h2>
    <div class="type-grid">
''')
    for t, label in TYPE_LABELS.items():
        if t not in by_type:
            continue
        n = len(by_type[t])
        parts.append(f'      <a href="topics/{t.lower()}.html" class="type-card"><strong>{esc(label)}</strong><span>{n}</span></a>\n')
    parts.append('    </div>\n  </div>\n</section>\n')

    # Recent / featured
    recent = sorted([p for p in papers if str(p.get('year', '')).isdigit() and int(p['year']) >= 2025], key=year_sort)[:9]
    parts.append('''
<section class="recent-section">
  <div class="wrap">
    <h2 class="section-title">Recently added (2025-2026)</h2>
    <div class="card-grid">
''')
    for p in recent:
        parts.append(paper_card(p))
    parts.append('    </div>\n  </div>\n</section>\n')

    # Inline search JS hook
    parts.append('''
<script>
document.getElementById('q')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') {
    const q = encodeURIComponent(e.target.value);
    window.location.href = 'browse.html?q=' + q;
  }
});
</script>
''')
    parts.append(PAGE_FOOT)
    (ROOT / 'index.html').write_text(''.join(parts))


# ---------- about.html ----------
def render_about():
    cell_counts = '\n'.join(
        f'    <tr><th>{c}</th><td>{len(by_cell.get(c, []))}</td><td>{esc(K_LABELS[c.split(".")[0]][0])} × {esc(O_LABELS[c.split(".")[1]][0])}</td></tr>'
        for K in ['K1', 'K2', 'K3', 'K4'] for O in ['O1', 'O2', 'O3'] for c in [f'{K}.{O}']
    )
    body = f'''
<section class="prose">
  <div class="wrap">
    <h1>About Scientific RAG Hub</h1>
    <p class="lede">
      A curated catalog of <strong>{len(papers)} retrieval-augmented generation</strong> systems,
      benchmarks, and datasets across the sciences — the companion resource to the TPAMI 2026 survey
      <em>"Scientific Retrieval-Augmented Generation: A Survey through Knowledge Source and Scientific Mission."</em>
    </p>

    <h2>The K×O taxonomy</h2>
    <p>
      We argue that scientific RAG is a <em>deterministic engine</em> constrained by physical laws,
      stoichiometric exactness, and experimental protocols — not by the probabilistic semantic proximity
      on which general-purpose RAG depends. Two axes capture what most shapes a scientific RAG system:
    </p>
    <h3>Knowledge Source (K) — what you draw upon</h3>
    <ul>
      <li><strong>K1 Primary Literature</strong> — peer-reviewed papers, preprints, scientific corpora.</li>
      <li><strong>K2 Curated Knowledge Base</strong> — community-maintained structured records (PubChem, RCSB PDB, Materials Project…).</li>
      <li><strong>K3 Observational & Experimental</strong> — image, spectra, sequencing, time-series modalities.</li>
      <li><strong>K4 Tacit Knowledge</strong> — institutional memory, lab protocols, private EHRs, industry process docs. ★ Novelty axis.</li>
    </ul>
    <h3>Operational Objective (O) — what you do with it</h3>
    <ul>
      <li><strong>O1 Ground</strong> — single-source grounding (retrieve · cite · answer).</li>
      <li><strong>O2 Synthesis</strong> — multi-source integration, claim verification.</li>
      <li><strong>O3 Hypothesis</strong> — generate new candidates (molecules, mechanisms, parameters).</li>
    </ul>

    <h2>Why this taxonomy</h2>
    <p>
      Existing RAG surveys classify systems by retriever-generator pipeline. That view misses what most
      shapes a <em>scientific</em> RAG system: the epistemic tier of the source and the scientific operation
      performed on it. The K×O grid surfaces structural patterns invisible to pipeline-centric views —
      dense cells (e.g. <strong>[K1.O1]</strong> medical QA, <strong>[K2.O3]</strong> drug/catalyst generation),
      and frontier cells (<strong>[K3.O3]</strong>, <strong>[K4.O3]</strong>) where opportunity remains.
    </p>

    <h2>Cell distribution</h2>
    <table class="ko-stat">
      <thead><tr><th>Cell</th><th>Count</th><th>K × O</th></tr></thead>
      <tbody>
{cell_counts}
      </tbody>
    </table>

    <h2>Five Unique Requirements of Scientific RAG</h2>
    <ol>
      <li><strong>Mandatory Claim Attribution</strong> — every claim traceable to source unit.</li>
      <li><strong>Relational Knowledge Coupling</strong> — facts in webs (PDB ↔ UniProt ↔ ChEMBL); traverse couplings.</li>
      <li><strong>Source Reliability Tiering</strong> — paper / preprint / curated / lab-note carry different epistemic weight.</li>
      <li><strong>Protocol-level Reproducibility</strong> — enough method detail for expert to reproduce.</li>
      <li><strong>Domain-Native Representations</strong> — SMILES, InChI, FASTA, LaTeX, CIF, DICOM — no text flattening.</li>
    </ol>

    <h2>How to use the catalog</h2>
    <ul>
      <li><a href="index.html#grid">K×O Grid</a> — pick a cell to see all systems landing there.</li>
      <li><a href="index.html#domains">Domains</a> — browse by scientific field.</li>
      <li><a href="browse.html">Browse</a> — full searchable, filterable catalog.</li>
      <li><a href="llms.txt">/llms.txt</a> · <a href="llms-full.txt">/llms-full.txt</a> — LLM-friendly indices.</li>
      <li><a href="data/papers.json">papers.json</a> — full machine-readable dump (one JSON, all metadata).</li>
    </ul>

    <h2>Methodology</h2>
    <p>
      Entries are sourced from a Notion-tracked literature database curated by the Vision and Learning Lab,
      cross-referenced against the survey's master bibliography. K×O assignments are author-verified for
      138 papers via full Notion fetch; the remaining ~44 are tagged provisionally pending re-verification.
      Cross-source papers (e.g. <strong>MedGraphRAG</strong> spanning K1+K2+K4) appear in multiple cells.
    </p>
    <p>
      Authoritative source files live in <code>/gallery_millet/yerim.oh/ScienceRAGServey/ver/2/</code>
      (<code>main.tex</code>, <code>references.bib</code>). The catalog data pipeline is reproducible from
      <code>site/build/</code>.
    </p>

    <h2>Contributing</h2>
    <p>
      Missing entries, mis-classifications, or new systems? Open an issue or PR on the
      GitHub repo. The build is fully deterministic — edit <code>data/ko_assignments.json</code>
      (or the source Notion DB) and re-run <code>build/render_html.py</code>.
    </p>

    <h2>Cite</h2>
    <pre><code>@article{{oh2026sciragsurvey,
  title   = {{Scientific Retrieval-Augmented Generation: A Survey through
             Knowledge Source and Scientific Mission}},
  author  = {{Oh, Yerim and others}},
  journal = {{IEEE Transactions on Pattern Analysis and Machine Intelligence}},
  year    = {{2026}}
}}</code></pre>
  </div>
</section>
'''
    (ROOT / 'about.html').write_text(page_head('About') + body + PAGE_FOOT)


# ---------- browse.html (client-side filter) ----------
def render_browse():
    domain_opts = '\n'.join(f'<option value="{d}">{esc(DOMAIN_LABELS[d])} ({len(by_dom[d])})</option>' for d in DOMAIN_LABELS if d in by_dom)
    type_opts = '\n'.join(f'<option value="{t}">{esc(TYPE_LABELS[t])} ({len(by_type[t])})</option>' for t in TYPE_LABELS if t in by_type)
    cell_opts = '\n'.join(f'<option value="{K}.{O}">[{K}.{O}] {esc(K_LABELS[K][0])} × {esc(O_LABELS[O][0])} ({len(by_cell.get(K+"."+O, []))})</option>' for K in ['K1','K2','K3','K4'] for O in ['O1','O2','O3'])
    body = f'''
<section class="browse-hero">
  <div class="wrap">
    <h1>Browse all {len(papers)} entries</h1>
    <p class="lede">Filter by K×O cell, domain, type, or year. Search hits title · method · note · tags.</p>
    <div class="filters">
      <input id="q" type="search" placeholder="Search…" autofocus>
      <select id="f-cell"><option value="">All K×O cells</option>{cell_opts}</select>
      <select id="f-domain"><option value="">All domains</option>{domain_opts}</select>
      <select id="f-type"><option value="">All types</option>{type_opts}</select>
      <select id="f-year">
        <option value="">All years</option>
        <option value="2026">2026</option>
        <option value="2025">2025</option>
        <option value="2024">2024</option>
        <option value="2023">2023</option>
        <option value="<2023">≤ 2022</option>
      </select>
      <button id="f-reset" type="button">Reset</button>
      <span id="result-count" class="result-count"></span>
    </div>
  </div>
</section>

<section class="browse-list">
  <div class="wrap">
    <div id="cards" class="card-grid"></div>
    <p id="empty" class="empty" hidden>No matching entries — try a broader search.</p>
  </div>
</section>

<script src="static/search.js"></script>
'''
    (ROOT / 'browse.html').write_text(page_head('Browse', base='') + body + PAGE_FOOT)


# ---------- cell/<K>.<O>.html ----------
def render_cell_pages():
    for K in ['K1', 'K2', 'K3', 'K4']:
        for O in ['O1', 'O2', 'O3']:
            cell = f'{K}.{O}'
            ps = sorted(by_cell.get(cell, []), key=year_sort)
            kn, kd = K_LABELS[K]
            on, od = O_LABELS[O]

            other_cells_nav = '\n'.join(
                f'<a href="{c}.html" class="pill {"current" if c == cell else ""}">{c}</a>'
                for c in [f'{kk}.{oo}' for kk in ['K1','K2','K3','K4'] for oo in ['O1','O2','O3']]
            )

            cards = '\n'.join(paper_card(p, base='../') for p in ps) or '<p class="empty">No verified entries in this cell yet — see <a href="../about.html#methodology">methodology</a> and the survey §11 frontier discussion.</p>'

            body = f'''
<section class="cell-hero">
  <div class="wrap">
    <p class="eyebrow"><a href="../index.html#grid">← K×O Grid</a></p>
    <h1><span class="cell-id-big">[{cell}]</span> {esc(kn)} <span class="times">×</span> {esc(on)}</h1>
    <p class="lede"><strong>{len(ps)}</strong> entries.</p>
    <div class="cell-axis-pair">
      <div class="axis-card axis-k">
        <span class="axis-tag">K {K[1]}</span>
        <h3>{esc(kn)}</h3>
        <p>{esc(kd)}</p>
      </div>
      <div class="axis-card axis-o">
        <span class="axis-tag">O {O[1]}</span>
        <h3>{esc(on)}</h3>
        <p>{esc(od)}</p>
      </div>
    </div>
    <div class="cell-nav">{other_cells_nav}</div>
  </div>
</section>

<section class="cell-list">
  <div class="wrap">
    <div class="card-grid">{cards}</div>
  </div>
</section>
'''
            (ROOT / 'cell' / f'{cell}.html').write_text(page_head(f'[{cell}] {kn} × {on}', base='../') + body + PAGE_FOOT)


# ---------- domain/<d>.html ----------
def render_domain_pages():
    for d, label in DOMAIN_LABELS.items():
        if d not in by_dom:
            continue
        ps = sorted(by_dom[d], key=year_sort)
        # Cell breakdown within domain
        dom_cells = Counter()
        for p in ps:
            for c in p.get('ko_cells', []):
                dom_cells[c] += 1
        breakdown = ''.join(
            f'<a href="../cell/{c}.html" class="pill">[{c}] {dom_cells[c]}</a>'
            for c in sorted(dom_cells, key=lambda x: -dom_cells[x])
        )
        cards = '\n'.join(paper_card(p, base='../') for p in ps)
        body = f'''
<section class="domain-hero">
  <div class="wrap">
    <p class="eyebrow"><a href="../index.html#domains">← Domains</a></p>
    <h1>{DOMAIN_EMOJI.get(d, "")} {esc(label)}</h1>
    <p class="lede"><strong>{len(ps)}</strong> entries in the {esc(label.lower())} domain.</p>
    {f'<div class="cell-breakdown"><span class="muted">K×O distribution:</span> {breakdown}</div>' if breakdown else ''}
  </div>
</section>

<section class="domain-list">
  <div class="wrap">
    <div class="card-grid">{cards}</div>
  </div>
</section>
'''
        (ROOT / 'domain' / f'{d}.html').write_text(page_head(label, base='../') + body + PAGE_FOOT)


# ---------- topics/<type>.html ----------
def render_type_pages():
    for t, label in TYPE_LABELS.items():
        if t not in by_type:
            continue
        ps = sorted(by_type[t], key=year_sort)
        cards = '\n'.join(paper_card(p, base='../') for p in ps)
        body = f'''
<section class="domain-hero">
  <div class="wrap">
    <p class="eyebrow"><a href="../index.html">← Home</a></p>
    <h1>{esc(label)}</h1>
    <p class="lede"><strong>{len(ps)}</strong> entries of type <code>{esc(t)}</code>.</p>
  </div>
</section>

<section class="domain-list">
  <div class="wrap">
    <div class="card-grid">{cards}</div>
  </div>
</section>
'''
        (ROOT / 'topics' / f'{t.lower()}.html').write_text(page_head(label, base='../') + body + PAGE_FOOT)


if __name__ == '__main__':
    render_index()
    render_about()
    render_browse()
    render_cell_pages()
    render_domain_pages()
    render_type_pages()
    print('Wrote all HTML pages.')
    print(f'  index.html, about.html, browse.html')
    print(f'  cell/*.html ({len(by_cell)} cells)')
    print(f'  domain/*.html ({len([d for d in DOMAIN_LABELS if d in by_dom])} domains)')
    print(f'  topics/*.html ({len([t for t in TYPE_LABELS if t in by_type])} types)')
