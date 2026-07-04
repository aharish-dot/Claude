import sys, difflib, re
def sig(l):
    # normalize: drop digital-signature noise & page furniture for diffing
    l = re.sub(r'\d','#',l.lower())
    return l
a = open(sys.argv[1]).read().splitlines()
b = open(sys.argv[2]).read().splitlines()
sm = difflib.SequenceMatcher(None, [sig(x) for x in a], [sig(x) for x in b], autojunk=False)
out=[]
for tag,i1,i2,j1,j2 in sm.get_opcodes():
    if tag in ('replace','insert'):
        for j in range(j1,j2):
            out.append(f"{j+1}: {b[j]}")
print(f"UNIQUE-TO-{sys.argv[2]}: {len(out)} lines")
print('\n'.join(out))
