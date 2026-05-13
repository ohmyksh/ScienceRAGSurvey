#!/usr/bin/env python3
"""Merge properties_full.jsonl (178 papers) + ko_assignments.json into papers.json.

Output schema (per paper):
{
  "bib_key": "...",
  "title": "...",
  "year": 2025,
  "venue": "...",
  "type": "Method|benchmark|dataset|summary",
  "domain": ["medical", "bio"],
  "modality": ["Text", "Image"],
  "db_name": "...",
  "db_open": "Open|Closed|Partial",
  "method": "...",
  "paper_link": "https://...",
  "note": "...",
  "ko_cells": ["K1.O1", "K2.O3"],      # all cells (primary + cross-listed)
  "ko_primary": "K1.O1",                 # first cell, used for grid placement
  "ko_note": "MEDRAG ... canonical K1.O1",
  "cross_source": true|false,
  "retriever": "...",
  "generator": "...",
  "eval_task": "...",
  "eval_metric": "..."
}
"""
import json
from pathlib import Path

ROOT = Path('/gallery_millet/yerim.oh/ScienceRAGServey/site')
PROPS = Path('/gallery_millet/yerim.oh/.claude/projects/-gallery-millet-yerim-oh/memory/notion_data/properties_full.jsonl')
KO = ROOT / 'data/ko_assignments.json'
OUT = ROOT / 'data/papers.json'

ko = json.loads(KO.read_text())
papers = []

# Fields to surface (with defaults)
TEXT_FIELDS = ['title', 'year', 'venue', 'venue_type', 'db_name', 'db_size',
               'db_open', 'db_etc', 'chunk', 'retriever', 'retriever_base',
               'retriever_train', 'pre_retrieval', 'pre_retrieval_detail',
               'post_retrieval_detail', 'generator', 'generator_base',
               'generator_train', 'eval_task', 'eval_metric', 'method',
               'paper_link', 'note', 'bib_key', 'bib_ver']
LIST_FIELDS = ['domain', 'modality', 'post_retrieval', 'evaluated_on']

seen = set()
for line in PROPS.read_text().splitlines():
    d = json.loads(line)
    bk = d.get('bib_key') or d.get('id')
    if not bk or bk in seen:
        continue
    seen.add(bk)

    rec = {}
    for f in TEXT_FIELDS:
        v = d.get(f)
        if v is not None and v != '__NO__' and v != '__YES__':
            rec[f] = v
        elif v == '__YES__':
            rec[f] = True
        elif v == '__NO__':
            rec[f] = False
    for f in LIST_FIELDS:
        v = d.get(f)
        if v:
            rec[f] = v if isinstance(v, list) else [v]

    rec['type'] = d.get('type', 'unknown')

    # Overlay K×O assignment
    a = ko.get(bk)
    if a:
        rec['ko_cells'] = a.get('cells', [])
        rec['ko_primary'] = a.get('cells', [None])[0] if a.get('cells') else None
        rec['ko_note'] = a.get('note', '')
        rec['cross_source'] = a.get('cross_source', False)
        if a.get('secondary'):
            rec['ko_secondary'] = a['secondary']
    else:
        rec['ko_cells'] = []
        rec['ko_primary'] = None
        rec['ko_note'] = ''
        rec['cross_source'] = False

    papers.append(rec)

# Also include K×O-only bib_keys from ko_assignments that aren't in Notion (e.g., RHIC, AP Lab Protocols, aplabprotocols2025)
notion_keys = {p['bib_key'] for p in papers if 'bib_key' in p}

# Load flagship overrides and bib-only title enrichment
FLAGSHIPS_FILE = ROOT / 'build/flagships.json'
flagship_data = json.loads(FLAGSHIPS_FILE.read_text()) if FLAGSHIPS_FILE.exists() else {'bib_only_titles': {}}
title_map = flagship_data.get('bib_only_titles', {})

extra = 0
for bk, a in ko.items():
    if bk in notion_keys:
        continue
    enrich = title_map.get(bk, {})
    rec = {
        'bib_key': bk,
        'title': enrich.get('title', bk),
        'year': enrich.get('year'),
        'venue': enrich.get('venue'),
        'method': enrich.get('method'),
        'domain': enrich.get('domain', []),
        'paper_link': enrich.get('paper_link', ''),
        'note': a.get('note', ''),
        'ko_cells': a.get('cells', []),
        'ko_primary': a.get('cells', [None])[0] if a.get('cells') else None,
        'ko_note': a.get('note', ''),
        'cross_source': a.get('cross_source', False),
        'type': 'Method',
        'bib_only': True,
    }
    if a.get('secondary'):
        rec['ko_secondary'] = a['secondary']
    papers.append(rec)
    extra += 1

# Mark flagships
flagship_keys = {f['bib_key'] for f in flagship_data.get('flagships', [])}
for p in papers:
    if p.get('bib_key') in flagship_keys:
        p['flagship'] = True

papers.sort(key=lambda p: (-int(p.get('year') or 0) if str(p.get('year', '')).isdigit() else 0, p.get('title', '')))

OUT.write_text(json.dumps(papers, indent=2, ensure_ascii=False))
print(f'Wrote {len(papers)} papers ({len(papers) - extra} from Notion + {extra} bib-only) → {OUT}')

# Stats
from collections import Counter
by_cell = Counter()
by_dom = Counter()
by_type = Counter()
ko_covered = 0
for p in papers:
    for c in p.get('ko_cells', []):
        by_cell[c] += 1
    for d in p.get('domain', []):
        by_dom[d] += 1
    by_type[p.get('type', 'unknown')] += 1
    if p.get('ko_primary'):
        ko_covered += 1
print(f'\nK×O coverage: {ko_covered}/{len(papers)} ({100*ko_covered/len(papers):.0f}%)')
print('By cell:')
for c in sorted(by_cell):
    print(f'  {c}: {by_cell[c]}')
print(f'By domain: {dict(by_dom)}')
print(f'By type: {dict(by_type)}')
