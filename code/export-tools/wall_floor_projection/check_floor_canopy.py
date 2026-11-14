import numpy as np

d = np.load(r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\_work\wall_floor_projection\geom_new_skp.npz", allow_pickle=True)
T = d["tris"]
P = d["path"]
paths = list(d["paths"])

def get_tris(name_list):
    idxs = [paths.index(n) for n in name_list if n in paths]
    m = np.isin(P, idxs)
    t = T[m]
    c = t.mean(1)
    keep = (c[:, 0] < 35) & (c[:, 1] < 46)
    return t[keep]

floor_g = get_tris(["/G"])
n = np.cross(floor_g[:, 1] - floor_g[:, 0], floor_g[:, 2] - floor_g[:, 0])
area = 0.5 * np.linalg.norm(n, axis=1)
nz = np.abs(n[:, 2]) / (2 * area + 1e-12)
floor_horiz = floor_g[(nz > 0.95) & (np.abs(floor_g[:, :, 2].mean(1)) < 0.05)]
print("Floor (/G z≈0) tris:", len(floor_horiz), "total area (top+bottom):", area[(nz > 0.95) & (np.abs(floor_g[:, :, 2].mean(1)) < 0.05)].sum())
fv = floor_horiz.reshape(-1, 3)
print("Floor vertices min:", fv.min(0).round(2), "max:", fv.max(0).round(2))
# Find the 4 outer corners of the diamond floor
for label, fn in [("min X (Right wing)", lambda v: v[:, 0]), ("max X (Left wing)", lambda v: -v[:, 0]),
                  ("min Y (Back apex)", lambda v: v[:, 1]), ("max Y (Front apex)", lambda v: -v[:, 1])]:
    idx = np.argmin(fn(fv))
    print(f"  Corner {label}: {fv[idx].round(2)}")

# Check canopy /组件#46 and /组件#47 horizontal faces
canopy = get_tris(["/组件#46", "/组件#46/组件#24", "/组件#47"])
cn = np.cross(canopy[:, 1] - canopy[:, 0], canopy[:, 2] - canopy[:, 0])
ca = 0.5 * np.linalg.norm(cn, axis=1)
cnz = np.abs(cn[:, 2]) / (2 * ca + 1e-12)
print("Canopy horiz area:", ca[cnz > 0.9].sum(), "vert area:", ca[cnz <= 0.9].sum())
for t_tri, a_val in zip(canopy[cnz > 0.9], ca[cnz > 0.9]):
    if a_val > 2.0:
        print("  Large canopy horiz tri z=", t_tri[:, 2].mean().round(2), "area=", round(float(a_val), 2), "xy_min=", t_tri[:, :2].min(0).round(2), "xy_max=", t_tri[:, :2].max(0).round(2))
