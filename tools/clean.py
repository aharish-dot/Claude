import re, html, json, sys
src, dst = sys.argv[1], sys.argv[2]
raw = open(src).read()
try:
    d = json.loads(raw)
    txt = d['fileContent']
except (json.JSONDecodeError, KeyError):
    txt = raw
txt = txt.replace('\\<','<').replace('\\>','>').replace('\\_','_').replace('\\&','&').replace('\\#','#')
txt = re.sub(r'<[^>]+>', ' ', txt)
txt = html.unescape(txt)
lines = [re.sub(r'[ \t]+',' ',l).strip() for l in txt.splitlines()]
lines = [l for l in lines if l]
open(dst,'w').write('\n'.join(lines))
print(dst, len(lines), 'lines')
