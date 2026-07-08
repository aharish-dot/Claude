#!/usr/bin/env python3
"""Pre-clean Indian Kanoon judgment text so verbatim quotes match naturally.

Removes page-header/footer artifacts that IK interleaves INTO the judgment body
(page-number lines, "::: Uploaded on ... :::" stamps, "2 / 28 wp....odt" footers,
case-number + "#12#" / "-:73:-" / "Page 5 of 18" page markers) and repairs words
split across a line break at a hyphen ("sub-\\nsection" -> "sub-section").

These artifacts were the cause of nearly every verify re-cycle: they land in the
middle of a sentence, so a quote that spans one won't grep-match. Cleaning here
(and in fetch_batch.py for new fetches) lets extraction quote whole clauses.

Idempotent. Usage:
  clean_queue.py                # clean every queue/*.txt in place
  clean_queue.py HC-017 ...     # clean specific ids
"""
import re, os, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))

# A whole line that is nothing but a page artifact -> drop it.
_ART_LINE = [
    re.compile(r'^\s*:::.*:::\s*$'),                                  # ::: Uploaded on ... :::
    re.compile(r'^\s*\d{1,3}\s*/\s*\d{1,3}\s+\S+\.(?:odt|pdf|doc)\s*$', re.I),  # 2 / 28 wp..odt
    re.compile(r'^\s*\d{1,4}\s*$'),                                   # bare page number
    re.compile(r'^\s*-\s*\d{1,4}\s*-\s*$'),                           # dashed page number  -2-
    re.compile(r'^\s*(?:W\.?P\.?|CWP|RFA|LPA|WPA|WA|CWJC|S\.?B\.?|MAT)\b.{0,70}#\d+#.*$', re.I),  # case-no + #n#
    re.compile(r'^.{0,55}-:\s*\d+\s*:-\s*$'),                         # "... Cases -:73:-"
    re.compile(r'^.{0,45}No\.[^ ]*\d{4}\s+\d{1,3}\s*$'),              # SC docket + page: "C.A.@S.L.P(c) No.22207/2018 21"
    re.compile(r'^\s*All corrections made in the judgment.*$', re.I), # trailing IK boilerplate
    re.compile(r'^\s*\d{1,2}\s+.{0,70}\(\d{4}\)\s+\d+\s+[A-Z][A-Za-z.]{1,6}\s+\d+\.?\s*$'),  # footnote defn: "3 (1986) 4 SCC 447."
    re.compile(r'^\s*AIR\s+\d{4}\b.{0,40}$'),                         # footnote defn: "AIR 2016 (NOC) 39 (M.P.)"
]
# Artifacts that appear INLINE within a content line -> squeeze to a space.
_INLINE = [
    (re.compile(r'\s*#\s*\d+\s*#\s*'), ' '),                          # inline #3#
    (re.compile(r'\s*-:\s*\d+\s*:-\s*'), ' '),                        # inline -:73:-
    (re.compile(r'\s*Page\s+\d+\s+of\s+\d+\s*'), ' '),               # Page 5 of 18
    (re.compile(r':::\s*Uploaded on.*?:::'), ' '),                    # inline upload stamp
]

def clean(text: str) -> str:
    lines = [ln for ln in text.split('\n') if not any(p.match(ln) for p in _ART_LINE)]
    t = '\n'.join(lines)
    t = re.sub(r'(\w)-[ \t]*\n\s*(\w)', r'\1-\2', t)      # rejoin hyphenated line-breaks (keep hyphen; span blank lines)
    for p, r in _INLINE:
        t = p.sub(r, t)
    t = re.sub(r'[ \t]+', ' ', t)                          # collapse runs of spaces/tabs
    t = re.sub(r'\n{3,}', '\n\n', t)                       # collapse blank-line runs
    return t.strip() + '\n'

def main():
    ids = sys.argv[1:]
    paths = ([os.path.join(HERE, 'queue', f'{i}.txt') for i in ids] if ids
             else sorted(glob.glob(os.path.join(HERE, 'queue', '*.txt'))))
    for p in paths:
        if not os.path.exists(p):
            print(f'  missing {p}'); continue
        raw = open(p).read()
        out = clean(raw)
        open(p, 'w').write(out)
        print(f'  {os.path.basename(p):14s} {len(raw):>7} -> {len(out):>7} chars')
    print('done')

if __name__ == '__main__':
    main()
