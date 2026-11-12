import sys
ind = lambda l: len(l) - len(l.lstrip(" "))
def fixfile(f):
 lines = open(f, encoding="utf-8").read().split("\n"); out = []; prev = ""
 for l in lines: bad = bool(l.strip()) and ind(l) % 4 != 0; n = (ind(prev) + 4 if prev.rstrip().endswith(":") else ind(prev)) if bad else ind(l); l = (" " * n + l.lstrip(" ")) if bad else l; prev = l if l.strip() else prev; out.append(l)
 open(f, "w", encoding="utf-8").write("\n".join(out))
for f in sys.argv[1:]: fixfile(f)
