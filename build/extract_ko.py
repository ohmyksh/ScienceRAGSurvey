#!/usr/bin/env python3
"""Extract K×O cell assignments from science_rag_paper_assignment.md.

Reads the "Master K×O Grid" section, which has headings like:
    ### Cell [K1.O1] Primary Literature × Ground (n=51)
followed by lines of the form:
    - `bib_key` — description (year, domain).
Outputs ko_assignments.json: {bib_key: {"K": "K1", "O": "O1", "cells": [...], "note": "..."}}
A paper can be cross-listed under multiple cells (cross-source); we record all.
"""
import json
import re
from pathlib import Path

SRC = Path('/gallery_millet/yerim.oh/.claude/projects/-gallery-millet-yerim-oh/memory/science_rag_paper_assignment.md')
OUT = Path('/gallery_millet/yerim.oh/ScienceRAGServey/site/data/ko_assignments.json')

CELL_RE = re.compile(r'^###\s+Cell\s+\[(K[1-4])\.(O[1-3])\]')
ENTRY_RE = re.compile(r'^-\s+`([^`]+)`\s*[—-]\s*(.+?)\s*$')

assignments = {}  # bib_key → {primary_cells: [], notes: []}
current_cell = None

for line in SRC.read_text().splitlines():
    m = CELL_RE.match(line)
    if m:
        current_cell = f'{m.group(1)}.{m.group(2)}'
        continue
    if current_cell is None:
        continue
    m = ENTRY_RE.match(line)
    if m:
        bk, note = m.group(1), m.group(2)
        # strip parenthetical year/domain
        rec = assignments.setdefault(bk, {'cells': [], 'note': note})
        if current_cell not in rec['cells']:
            rec['cells'].append(current_cell)

# Also parse the Cross-Source Tag Index table for secondary cells
TABLE_RE = re.compile(r'^\|\s*`([^`]+)`\s*\|\s*(K[1-4]\.O[1-3])\s*\|\s*(K[1-4](?:\.O[1-3])?(?:/[KO][1-4]?)?)\s*\|\s*(.+?)\s*\|')
in_xs = False
for line in SRC.read_text().splitlines():
    if 'Cross-Source Tag Index' in line:
        in_xs = True
        continue
    if in_xs:
        m = TABLE_RE.match(line)
        if m:
            bk, primary, secondary, note = m.groups()
            rec = assignments.setdefault(bk, {'cells': [], 'note': note})
            rec['cross_source'] = True
            rec['secondary'] = secondary

# Derive primary K and O (first cell) for filtering
for bk, rec in assignments.items():
    if rec['cells']:
        p = rec['cells'][0]
        rec['K'], rec['O'] = p.split('.')
    else:
        rec['K'], rec['O'] = None, None

OUT.write_text(json.dumps(assignments, indent=2, ensure_ascii=False))
print(f'Extracted {len(assignments)} K×O assignments → {OUT}')
print(f'Sample 5:')
for i, (k, v) in enumerate(assignments.items()):
    if i >= 5:
        break
    print(f'  {k}: {v}')

# Cell counts
from collections import Counter
cells = Counter()
for v in assignments.values():
    for c in v['cells']:
        cells[c] += 1
print(f'\nCell counts (primary OR cross-listed):')
for c in sorted(cells):
    print(f'  {c}: {cells[c]}')
