import os
import json
import numpy as np

sim_dir = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\denza-project-handoff\quickstart\projection-simulation"
d = np.load(os.path.join(sim_dir, "geom.npz"))
tris = d["tris"]
path_ids = d["path"]
meta = json.load(open(os.path.join(sim_dir, "geom.json"), encoding="utf-8"))
paths = meta["paths"]

print("=== geom.npz components ===")
for idx, p in enumerate(paths):
    m = path_ids == idx
    t = tris[m]
    if len(t) == 0:
        continue
    v = t.reshape(-1, 3)
    bmin = v.min(0).round(2)
    bmax = v.max(0).round(2)
    # check normals z
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    area = 0.5 * np.linalg.norm(n, axis=1)
    nz = np.abs(n[:, 2]) / (2 * area + 1e-12)
    horiz_area = area[nz > 0.9].sum()
    vert_area = area[nz <= 0.9].sum()
    print(f"[{idx:2d}] {p:25s} | tris={len(t):5d} | min={bmin} max={bmax} | vert_area={vert_area:.1f}m2 horiz_area={horiz_area:.1f}m2")
