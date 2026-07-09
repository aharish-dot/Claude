#!/usr/bin/env python3
"""Assemble a self-contained static site under docs/ for GitHub Pages (free hosting).

Layout produced:
  docs/index.html          - the jurisprudence map (home page)
  docs/records/*.html      - every case page the map links to
  docs/.nojekyll           - serve files as-is (no Jekyll processing)

The map's GH links are relative ("records/<case>.record.html#h{n}"), so they
resolve on the Pages site with no external host. Run after build_treatise.py.

Publish (one-time): repo Settings -> Pages -> Deploy from a branch ->
branch = claude/electricity-act-case-strategy-s2xebj, folder = /docs.
Live at: https://aharish-dot.github.io/Claude/
"""
import os, glob, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
CS = os.path.join(ROOT, "research", "case-selection")
DOCS = os.path.join(ROOT, "docs")
RECS = os.path.join(DOCS, "records")

# fresh docs/ each run so deleted cases don't linger
shutil.rmtree(DOCS, ignore_errors=True)
os.makedirs(RECS, exist_ok=True)

# 1) home page = the jurisprudence map
shutil.copyfile(os.path.join(CS, "jurisprudence_map.html"), os.path.join(DOCS, "index.html"))

# 2) all case pages: records/ plus the two root gold examples
case_pages = glob.glob(os.path.join(CS, "records", "*.record.html"))
case_pages += [os.path.join(CS, p) for p in ("SC-001.record.html", "HC-003.record.html")
               if os.path.exists(os.path.join(CS, p))]
for p in sorted(case_pages):
    shutil.copyfile(p, os.path.join(RECS, os.path.basename(p)))

# 3) disable Jekyll so every file is served verbatim
open(os.path.join(DOCS, ".nojekyll"), "w").close()

print(f"site: docs/index.html + {len(case_pages)} case pages in docs/records/")
