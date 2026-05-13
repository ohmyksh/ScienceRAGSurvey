#!/usr/bin/env python3
"""Generate llms.txt, llms-full.txt, topics/*.md, cell/*.md, domain/*.md.

Mimics the huggingscience.co layout: a top-level llms.txt with category overview,
an llms-full.txt with every entry, and per-topic markdown files.
"""
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path('/gallery_millet/yerim.oh/ScienceRAGServey/site')
papers = json.loads((ROOT / 'data/papers.json').read_text())

# --- Reference tables ---

K_LABELS = {
    'K1': ('Primary Literature', 'Peer-reviewed papers, preprints, scientific corpora (PubMed, arXiv, S2ORC, ChemRxiv).'),
    'K2': ('Curated Knowledge Base', 'Community-maintained structured records (PubChem, RCSB PDB, AlphaFold DB, ChEMBL, UMLS, PrimeKG, Materials Project).'),
    'K3': ('Observational & Experimental', 'Raw modality data: images, spectra, sequencing, time-series (cryo-EM, mass spec, telescope archives, EHR images).'),
    'K4': ('Tacit Knowledge', 'Institutional memory (RHIC, DUNE, CMS), lab protocols, private EHRs, governmental/industry process docs. ★ Novelty axis.'),
}

O_LABELS = {
    'O1': ('Ground', 'Single-source grounding: retrieve, cite, answer.'),
    'O2': ('Synthesis', 'Multi-source integration, claim verification.'),
    'O3': ('Hypothesis', 'Generate new candidates — molecules, mechanisms, parameters.'),
}

DOMAIN_LABELS = {
    'bio': 'Biology',
    'chem': 'Chemistry',
    'medical': 'Medicine',
    'material': 'Materials Science',
    'physics': 'Physics',
    'earth': 'Earth Science',
    'astronomy': 'Astronomy',
    'Quantum': 'Quantum',
    'general': 'General Science',
}

TYPE_LABELS = {
    'Method': 'Methods',
    'benchmark': 'Benchmarks',
    'dataset': 'Datasets',
    'summary': 'Surveys',
}

# --- Helpers ---

def short_desc(p):
    """Build a one-line description, ≤ 200 chars."""
    parts = []
    if p.get('method') and p.get('method') != p.get('title', ''):
        parts.append(p['method'])
    if p.get('venue'):
        parts.append(p.get('venue', ''))
    if p.get('year'):
        parts.append(str(p['year']))
    head = ' · '.join([x for x in parts if x])
    note = p.get('note') or p.get('ko_note') or ''
    if note:
        note = note.strip().rstrip('.').strip()
        if len(note) > 180:
            note = note[:177] + '…'
    return f'{head} — {note}' if head and note else (head or note)


def entry_md(p, show_tags=True):
    """Render a paper as one markdown bullet (huggingscience.co style)."""
    title = p.get('title') or p.get('bib_key', '?')
    url = p.get('paper_link') or ''
    desc = short_desc(p)
    if url:
        line = f'- **[{title}]({url})**'
    else:
        line = f'- **{title}**'
    if desc:
        line += f' — {desc}'
    if show_tags:
        tags = []
        for c in p.get('ko_cells', []):
            tags.append(c)
        for d in p.get('domain', []):
            tags.append(DOMAIN_LABELS.get(d, d))
        if p.get('type') and p['type'] != 'unknown':
            tags.append(TYPE_LABELS.get(p['type'], p['type']))
        if tags:
            line += f'  `[{", ".join(tags)}]`'
    return line


# --- Group papers ---
by_cell = defaultdict(list)
by_dom = defaultdict(list)
by_type = defaultdict(list)
unassigned = []

for p in papers:
    cells = p.get('ko_cells') or []
    if cells:
        for c in cells:
            by_cell[c].append(p)
    else:
        unassigned.append(p)
    for d in p.get('domain', []):
        by_dom[d].append(p)
    t = p.get('type', 'unknown')
    by_type[t].append(p)

# --- llms.txt: compact overview ---

def cell_intro(cell):
    K, O = cell.split('.')
    return f'**[{cell}]** {K_LABELS[K][0]} × {O_LABELS[O][0]}'


llms_lines = [
    '# Scientific RAG Hub — AI for Science Retrieval-Augmented Generation Index',
    '',
    'A curated catalog of Retrieval-Augmented Generation (RAG) systems, benchmarks, and datasets',
    'across nine scientific domains, organized by a dual-axis Knowledge Source × Operational Objective',
    f'taxonomy. {len(papers)} entries; {sum(len(v) for v in by_cell.values())} K×O cell assignments across 12 cells.',
    '',
    'Companion to the TPAMI 2026 survey "Scientific Retrieval-Augmented Generation: A Survey through',
    'Knowledge Source and Scientific Mission" (Oh et al., Vision and Learning Lab, Seoul National University).',
    '',
    '## Browse by K×O cell (12 cells)',
    '',
]
for K in ['K1', 'K2', 'K3', 'K4']:
    for O in ['O1', 'O2', 'O3']:
        cell = f'{K}.{O}'
        count = len(by_cell.get(cell, []))
        kn, kd = K_LABELS[K]
        on, od = O_LABELS[O]
        llms_lines.append(f'- [/cell/{cell}.md]({cell}.md) — {kn} × {on} ({count} entries)')
llms_lines += [
    '',
    '## Browse by scientific domain',
    '',
]
for d, label in DOMAIN_LABELS.items():
    if d in by_dom:
        llms_lines.append(f'- [/domain/{d}.md]({d}.md) — {label} ({len(by_dom[d])} entries)')

llms_lines += [
    '',
    '## Browse by resource type',
    '',
]
for t, label in TYPE_LABELS.items():
    if t in by_type:
        llms_lines.append(f'- [/topics/{t.lower()}.md]({t.lower()}.md) — {label} ({len(by_type[t])} entries)')

llms_lines += [
    '',
    '## Knowledge Source axis (K1-K4)',
    '',
]
for K, (n, d) in K_LABELS.items():
    llms_lines.append(f'- **{K} {n}** — {d}')
llms_lines += [
    '',
    '## Operational Objective axis (O1-O3)',
    '',
]
for O, (n, d) in O_LABELS.items():
    llms_lines.append(f'- **{O} {n}** — {d}')
llms_lines += [
    '',
    'For the full catalog with descriptions, see /llms-full.txt',
    '',
]
(ROOT / 'llms.txt').write_text('\n'.join(llms_lines))
print(f'Wrote llms.txt ({len(llms_lines)} lines)')


# --- llms-full.txt: every entry ---
full = [
    '# Scientific RAG Hub — Full Catalog',
    '',
    f'{len(papers)} retrieval-augmented generation systems, benchmarks, and datasets for scientific discovery.',
    'Organized by the K × O dual-axis taxonomy (Knowledge Source × Operational Objective).',
    '',
    'Each entry carries tags `[K.O cell(s), domain(s), type]`. Cross-source papers appear in multiple cells.',
    '',
]
for K in ['K1', 'K2', 'K3', 'K4']:
    kn, kd = K_LABELS[K]
    full.append(f'## K{K[1]} — {kn}')
    full.append('')
    full.append(f'_{kd}_')
    full.append('')
    for O in ['O1', 'O2', 'O3']:
        cell = f'{K}.{O}'
        on, od = O_LABELS[O]
        ps = by_cell.get(cell, [])
        full.append(f'### {cell}  ·  {kn} × {on}  ({len(ps)})')
        full.append(f'_{od}_')
        full.append('')
        for p in sorted(ps, key=lambda x: -int(x.get('year') or 0) if str(x.get('year', '')).isdigit() else 0):
            full.append(entry_md(p))
        full.append('')

if unassigned:
    full.append('## Unassigned (K×O pending)')
    full.append('')
    full.append(f'{len(unassigned)} entries from the Notion catalog without verified K×O assignment yet.')
    full.append('')
    for p in unassigned:
        full.append(entry_md(p))
    full.append('')

(ROOT / 'llms-full.txt').write_text('\n'.join(full))
print(f'Wrote llms-full.txt ({len(full)} lines)')


# --- Per-cell markdown pages ---
for K in ['K1', 'K2', 'K3', 'K4']:
    for O in ['O1', 'O2', 'O3']:
        cell = f'{K}.{O}'
        kn, kd = K_LABELS[K]
        on, od = O_LABELS[O]
        ps = by_cell.get(cell, [])
        lines = [
            f'# [{cell}]  {kn} × {on}',
            '',
            f'**K {K[1]}:** {kd}',
            '',
            f'**O {O[1]}:** {od}',
            '',
            f'_{len(ps)} entries_',
            '',
            '---',
            '',
        ]
        for p in sorted(ps, key=lambda x: -int(x.get('year') or 0) if str(x.get('year', '')).isdigit() else 0):
            lines.append(entry_md(p, show_tags=False))
        lines.append('')
        (ROOT / 'cell' / f'{cell}.md').write_text('\n'.join(lines))

# --- Per-domain markdown pages ---
for d, label in DOMAIN_LABELS.items():
    if d not in by_dom:
        continue
    ps = by_dom[d]
    lines = [
        f'# {label}',
        '',
        f'_{len(ps)} entries in the {label.lower()} domain._',
        '',
        '---',
        '',
    ]
    for p in sorted(ps, key=lambda x: -int(x.get('year') or 0) if str(x.get('year', '')).isdigit() else 0):
        lines.append(entry_md(p))
    lines.append('')
    (ROOT / 'domain' / f'{d}.md').write_text('\n'.join(lines))

# --- Per-type markdown pages ---
for t, label in TYPE_LABELS.items():
    if t not in by_type:
        continue
    ps = by_type[t]
    lines = [
        f'# {label}',
        '',
        f'_{len(ps)} entries of type "{t}"._',
        '',
        '---',
        '',
    ]
    for p in sorted(ps, key=lambda x: -int(x.get('year') or 0) if str(x.get('year', '')).isdigit() else 0):
        lines.append(entry_md(p))
    lines.append('')
    (ROOT / 'topics' / f'{t.lower()}.md').write_text('\n'.join(lines))

print(f'Wrote {len(by_cell)} cell/*.md, {len(by_dom)} domain/*.md, {len(by_type)} topics/*.md')
