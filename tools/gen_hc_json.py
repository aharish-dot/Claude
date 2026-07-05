#!/usr/bin/env python3
"""HC/SC per-case JSON summary generator: extract JSON -> clean machine-readable digest JSON.

Usage: python tools/gen_hc_json.py <extract.json> <out.json>

The digest HTML (tools/gen_hc.py) is for human reading; this is its machine-readable twin,
written to <COURT>/summaries/json/<caseid>.json. It strips the inline presentation HTML
(<em>, <strong>, <span class="cn">, &nbsp; etc.) from the extract to plain text and reshapes
the [lead, body] / [heading, text] pairs into named objects, so the merged compilations and
any downstream tooling can consume it without parsing HTML.
"""
import sys, json, re, html as _h


def clean(x):
    """Inline-HTML string -> plain text."""
    if x is None:
        return ""
    x = re.sub(r'<[^>]+>', '', str(x))          # drop tags (em/strong/span.cn/...)
    x = _h.unescape(x)                           # &nbsp; &mdash; &rsquo; &amp; ...
    x = x.replace('\xa0', ' ').replace('‑', '-')
    return re.sub(r'\s+', ' ', x).strip()


def pairs(items):
    """[[lead, body], ...] -> [{point, explanation}, ...]"""
    out = []
    for it in items or []:
        if isinstance(it, (list, tuple)) and len(it) == 2:
            out.append({"point": clean(it[0]).rstrip('.'), "explanation": clean(it[1])})
    return out


def interps(items):
    """[[heading, text], ...] -> [{provision, interpretation}, ...]"""
    return [{"provision": clean(h), "interpretation": clean(t)}
            for h, t in (i for i in (items or []) if isinstance(i, (list, tuple)) and len(i) == 2)]


def build(c):
    return {
        "case_id": c.get("case_id", ""),
        "title": clean(c.get("title")),
        "subcite": clean(c.get("subcite")),
        "court": clean(c.get("court")),
        "court_short": clean(c.get("court_short")),
        "scope": clean(c.get("scope")),
        "coram": clean(c.get("coram")),
        "date_of_judgment": clean(c.get("date_of_judgment")),
        "nature": clean(c.get("nature")),
        "parties": clean(c.get("parties")),
        "provisions": clean(c.get("provisions")),
        "result": clean(c.get("result")),
        "issues": [clean(i) for i in c.get("issues", [])],
        "facts": [clean(p) for p in c.get("facts", [])],
        "headnote": clean(c.get("headnote")),
        "reasoning": pairs(c.get("reasoning")),
        "interpretations": interps(c.get("interpretation")),
        "ratio": clean(c.get("ratio")),
        "obiter": pairs(c.get("obiter")),
        "disposition": clean(c.get("disposition")),
        "significance": pairs(c.get("significance")),
        "authorities": [
            {
                "name": clean(a.get("name")),
                "citation": clean(a.get("cite")),
                "court": clean(a.get("court")),
                "docid": str(a.get("docid", "")).strip(),
                "treatment": clean(a.get("treatment")),
                "proposition": clean(a.get("prop")),
            }
            for a in c.get("authorities", [])
        ],
    }


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    c = json.load(open(src))
    d = build(c)
    with open(out, "w") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print(f"wrote {out} from {src} "
          f"({len(d['authorities'])} authorities, {len(d['issues'])} issues, "
          f"{len(d['interpretations'])} interpretations)")
