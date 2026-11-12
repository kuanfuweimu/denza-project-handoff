"""Grid-search projector positions for the left section; mirror for the right."""
import numpy as np
from sim import samples, evaluate, TRIS, OCC_FAST

P, N, A = samples(0.6)
left = P[:, 0] <= 15.0
Pl, Nl, Al = P[left], N[left], A[left]
print("samples", len(P), "left", left.sum(), "left area", round(Al.sum(), 1))

floor_ok = lambda x, y: abs(x - 15) + abs(y - 14.21) <= 11.8
inside_v = lambda x, y: (x + y > 22.4) and (x - y < 7.4)  # audience side of the V wall
box = lambda x, y, z: abs(x - 15) + abs(y - 17.61) <= 5.2 and 4.8 <= z <= 8.9

res = []
for x in np.arange(4, 26.1, 2.0):
    for y in np.arange(9, 26.1, 2.0):
        if not (floor_ok(x, y) and inside_v(x, y)):
            continue
        for z in [2.5, 3.5, 4.5, 6.0, 7.5, 9.5, 11.5]:
            if box(x, y, z):
                continue
            pos = np.array([x, y, z])
            ev = evaluate(pos, Pl, Nl, Al, TRIS[OCC_FAST])
            if ev["tr"] < 0.36:
                continue
            inc = np.degrees(np.arccos(np.clip(ev["cosi"][ev["lit"]], -1, 1))).mean() if ev["lit"].any() else 90
            res.append((ev["cover"], -inc, x, y, z, ev["tr"]))
res.sort(reverse=True)
print("cover  meanInc  x     y     z    TR")
for c, ni, x, y, z, tr in res[:25]:
    print(f"{c:5.3f}  {-ni:5.1f}  {x:5.1f} {y:5.1f} {z:4.1f} {tr:5.2f}")
np.save("search.npy", np.array(res))
