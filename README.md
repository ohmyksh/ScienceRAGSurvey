# Scientific RAG Hub

A curated catalog of **retrieval-augmented generation (RAG) systems for scientific discovery**, organized by a dual-axis **Knowledge Source × Operational Objective** taxonomy.

Companion site to the TPAMI 2026 survey *"Scientific Retrieval-Augmented Generation: A Survey through Knowledge Source and Scientific Mission"* (Oh et al., Vision and Learning Lab, Seoul National University).

🌐 **Live site:** _(set after enabling GitHub Pages — see below)_

## What's in here

- **182 entries** — methods, benchmarks, and datasets across 8 scientific domains
- **12 K×O cells** — every entry placed in the dual-axis grid (Knowledge Source K1–K4 × Operational Objective O1–O3)
- **LLM-friendly indices** — `llms.txt` (compact overview) and `llms-full.txt` (every entry)
- **Machine-readable dump** — `data/papers.json` (single JSON, all metadata)

## Structure

```
site/
├── index.html              # Landing page with K×O grid + search
├── about.html              # Survey context, taxonomy, methodology
├── browse.html             # Full client-side filterable catalog
├── llms.txt                # Compact overview for LLMs
├── llms-full.txt           # Full content listing for LLMs
├── cell/                   # 12 K×O cell pages (K1.O1.html … K4.O3.html)
├── domain/                 # 8 domain pages (bio, chem, medical, …)
├── topics/                 # 4 type pages (method, benchmark, dataset, summary)
├── data/
│   ├── papers.json         # Master data — 182 entries with full metadata
│   └── ko_assignments.json # K×O cell assignments (138 author-verified)
├── static/
│   ├── style.css
│   └── search.js           # Browse-page filter
└── build/                  # Reproducible pipeline
    ├── extract_ko.py       # Pulls K×O assignments from memory/
    ├── build_papers.py     # Merges Notion props + K×O → papers.json
    ├── generate_content.py # Builds llms.txt and topic .md files
    └── render_html.py      # Renders every HTML page from papers.json
```

## Rebuild

```bash
python3 build/extract_ko.py       # → data/ko_assignments.json
python3 build/build_papers.py     # → data/papers.json
python3 build/generate_content.py # → llms.txt, llms-full.txt, topics/*.md
python3 build/render_html.py      # → index.html + all HTML pages
```

Everything is deterministic — re-running these in order regenerates the entire site from source data.

## Deploy to GitHub Pages

1. Create a new GitHub repo (e.g. `sci-rag-hub`) and push this directory.
2. In repo **Settings → Pages**, set source to `main` branch, `/ (root)` folder.
3. GitHub will publish at `https://<user>.github.io/sci-rag-hub/`.

The site is fully static (no build step required by GitHub) — `.nojekyll` is present to skip Jekyll processing.

## Cite

```bibtex
@article{oh2026sciragsurvey,
  title   = {Scientific Retrieval-Augmented Generation: A Survey through
             Knowledge Source and Scientific Mission},
  author  = {Oh, Yerim and others},
  journal = {IEEE Transactions on Pattern Analysis and Machine Intelligence},
  year    = {2026}
}
```

## License

Catalog metadata © 2026 Vision and Learning Lab, Seoul National University. Site code under MIT.
