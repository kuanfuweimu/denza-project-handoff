import os
import json
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\_work\wall_floor_projection"
TD_ASSETS_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\td_assets_wall_floor"
ARCHIVE_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA 2\2026-11_DENZA Z\01_场景1_墙面双投影\墙地双投方案_1114"
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(TD_ASSETS_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

d = np.load(os.path.join(WORK_DIR, "geom_new_skp.npz"), allow_pickle=True)
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

WALL_NAMES = ["/组件#56/G", "/组件#56/G/G", "/组件#57", "/组件#56/G/组件#15"]
CANOPY_NAMES = ["/组件#46", "/组件#46/组件#24", "/组件#47"]
FG_COL_NAMES = ["/组件#72", "/组件#27/G/G/组件#22", "/组件#27/G/组件#23", "/组件#27/G/组件#24"]

wall_raw = get_tris(WALL_NAMES)
wn = np.cross(wall_raw[:, 1] - wall_raw[:, 0], wall_raw[:, 2] - wall_raw[:, 0])
wa = 0.5 * np.linalg.norm(wn, axis=1)
wall_tris = wall_raw[(wa > 1e-6) & (np.abs(wn[:, 2]) / (2 * wa + 1e-12) < 0.95)]

canopy_tris = get_tris(CANOPY_NAMES)
fg_col_tris = get_tris(FG_COL_NAMES)

# V-wall polyline in XY (metres, Z-up)
poly = np.array([
    [4.71, 16.72],
    [5.28, 16.72],
    [13.99, 8.02],
    [16.02, 8.02],
    [24.72, 16.72],
    [25.29, 16.72]
])
seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
cum = np.r_[0, np.cumsum(seg)]
TOTAL_WALL_W, WALL_H = float(cum[-1]), 6.0

def arc(p2):
    best = np.full(len(p2), 1e9)
    s = np.zeros(len(p2))
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i + 1]
        t = np.clip(((p2 - a) @ (b - a)) / seg[i] ** 2, 0, 1)
        dd = np.linalg.norm(p2 - (a + t[:, None] * (b - a)), axis=1)
        m = dd < best
        best[m], s[m] = dd[m], cum[i] + t[m] * seg[i]
    return s

def td_coord(p):  # SketchUp (x, y, z) Z-up -> TD (x, z, -y) Y-up
    return np.stack([p[..., 0], p[..., 2], -p[..., 1]], -1)

# Build clean stage floor mesh in front of the V-wall:
# The stage floor is the diamond polygon bounded by the V-wall inner base:
# P0(5.28, 16.72) -> P1(13.99, 8.02) -> P2(16.02, 8.02) -> P3(24.72, 16.72) -> Front apex P4(15.00, 26.37)
floor_poly_xy = np.array([
    [5.28, 16.72],   # Right wing base (audience right)
    [13.99, 8.02],   # Right apex chamfer
    [16.02, 8.02],   # Left apex chamfer
    [24.72, 16.72],  # Left wing base (audience left)
    [15.00, 26.37],  # Front diamond corner
])
# Subdivide stage floor into a high-res grid for clean projection & lighting in TD
floor_tris_list = []
center_xy = np.array([15.00, 17.20])
# Triangulate fan from center_xy and subdivide 16x16
N_SUB = 24
for i in range(len(floor_poly_xy)):
    A = center_xy
    B = floor_poly_xy[i]
    C = floor_poly_xy[(i + 1) % len(floor_poly_xy)]
    for u_i in range(N_SUB):
        for v_i in range(N_SUB - u_i):
            u0, v0 = u_i / N_SUB, v_i / N_SUB
            u1, v1 = (u_i + 1) / N_SUB, (v_i + 1) / N_SUB
            p00 = A + u0 * (B - A) + v0 * (C - A)
            p10 = A + u1 * (B - A) + v0 * (C - A)
            p01 = A + u0 * (B - A) + v1 * (C - A)
            floor_tris_list.append([[p00[0], p00[1], 0.0], [p10[0], p10[1], 0.0], [p01[0], p01[1], 0.0]])
            if u_i + v_i + 2 <= N_SUB:
                p11 = A + u1 * (B - A) + v1 * (C - A)
                floor_tris_list.append([[p10[0], p10[1], 0.0], [p11[0], p11[1], 0.0], [p01[0], p01[1], 0.0]])
floor_tris = np.array(floor_tris_list, dtype=np.float64)

# Floor UV mapping:
# Audience looks from +Y toward -Y (so audience-left is +X = 24.72, audience-right is -X = 5.28)
# Let floor u = 0 (audience left, X=25.29) .. 1 (audience right, X=4.71) to match wall_combined UV horizontal direction!
# Let floor v = 0 (front of stage, Y=26.37) .. 1 (back V-wall apex, Y=8.02) so v=1 touches the base of the wall (v=0 of wall)!
FLOOR_X_MIN, FLOOR_X_MAX = 4.71, 25.29
FLOOR_Y_MIN, FLOOR_Y_MAX = 8.02, 26.37
FLOOR_SPAN_W = FLOOR_X_MAX - FLOOR_X_MIN  # 20.58 m
FLOOR_SPAN_D = FLOOR_Y_MAX - FLOOR_Y_MIN  # 18.35 m

def floor_uv(xy):
    u = 1.0 - (xy[..., 0] - FLOOR_X_MIN) / FLOOR_SPAN_W
    v = 1.0 - (xy[..., 1] - FLOOR_Y_MIN) / FLOOR_SPAN_D
    return np.stack([np.clip(u, 0, 1), np.clip(v, 0, 1)], -1)

# Export OBJ files for TD
def write_obj(path, groups):
    lines = ["# Denza Wall+Floor Mapping Mesh (metres, TD Y-up)"]
    vi = 1
    ti = 1
    for gname, tris, uv_mode in groups:
        lines.append(f"g {gname}")
        for tri in tris:
            P_td = td_coord(tri)
            for p in P_td:
                lines.append(f"v {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}")
            if uv_mode == "wall":
                s = arc(tri[:, :2])
                for k in range(3):
                    u = 1.0 - s[k] / TOTAL_WALL_W
                    v = tri[k, 2] / WALL_H
                    lines.append(f"vt {u:.5f} {v:.5f}")
                lines.append(f"f {vi}/{ti} {vi+1}/{ti+1} {vi+2}/{ti+2}")
                ti += 3
            elif uv_mode == "floor":
                uvs = floor_uv(tri[:, :2])
                for k in range(3):
                    lines.append(f"vt {uvs[k, 0]:.5f} {uvs[k, 1]:.5f}")
                lines.append(f"f {vi}/{ti} {vi+1}/{ti+1} {vi+2}/{ti+2}")
                ti += 3
            else:
                lines.append(f"f {vi} {vi+1} {vi+2}")
            vi += 3
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

write_obj(os.path.join(TD_ASSETS_DIR, "wall_combined.obj"), [("wall_combined", wall_tris, "wall")])
write_obj(os.path.join(TD_ASSETS_DIR, "floor_stage.obj"), [("floor_stage", floor_tris, "floor")])
write_obj(os.path.join(TD_ASSETS_DIR, "occluder.obj"), [("occluder_canopy", canopy_tris, None)])
write_obj(os.path.join(TD_ASSETS_DIR, "columns_fg.obj"), [("columns_fg", fg_col_tris, None)])
write_obj(os.path.join(TD_ASSETS_DIR, "stage_all_mapping.obj"), [
    ("wall_combined", wall_tris, "wall"),
    ("floor_stage", floor_tris, "floor"),
    ("occluder_canopy", canopy_tris, None),
    ("columns_fg", fg_col_tris, None)
])

# Raycast & Projector Simulation for:
# Projector 1 (WALL_COMBINED): Single projector covering BOTH V-walls
# Projector 2 (FLOOR_STAGE): Single projector covering STAGE FLOOR
def frame(pos, target):
    f = target - pos
    f = f / np.linalg.norm(f)
    up_ref = np.array([0.0, 0.0, 1.0])
    if abs(np.dot(f, up_ref)) > 0.95:
        # For steep downward floor projector, orient 'up' toward -Y (toward V-wall apex)
        up_ref = np.array([0.0, -1.0, 0.0])
    r = np.cross(f, up_ref)
    r = r / np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u

def hits(P_orig, S_pts, O_tris, eps=1e-3):
    if len(O_tris) == 0:
        return np.zeros(len(S_pts), bool)
    D = S_pts - P_orig
    v0, e1, e2 = O_tris[:, 0], O_tris[:, 1] - O_tris[:, 0], O_tris[:, 2] - O_tris[:, 0]
    out = np.zeros(len(S_pts), bool)
    for i in range(0, len(S_pts), 256):
        Dc = D[i:i + 256][:, None, :]
        h = np.cross(Dc, e2[None])
        a = np.einsum("nmk,mk->nm", h, e1)
        ok = np.abs(a) > 1e-12
        f = np.where(ok, 1.0 / np.where(ok, a, 1), 0)
        s = (P_orig - v0)[None]
        u = f * np.einsum("nmk,nmk->nm", np.broadcast_to(s, h.shape), h)
        q = np.cross(np.broadcast_to(s, h.shape), e1[None])
        v = f * np.einsum("nmk,nmk->nm", np.broadcast_to(Dc, q.shape), q)
        t = f * np.einsum("mk,nmk->nm", e2, q)
        blk = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > eps) & (t < 1 - eps)
        out[i:i + 256] = blk.any(1)
    return out

def sample_tris(tris, cell=0.25, up_normal=False):
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    a = 0.5 * np.linalg.norm(n, axis=1)
    n = n / (2 * a[:, None] + 1e-12)
    c = tris.mean(1)
    if up_normal:
        flip = n[:, 2] < 0
        n[flip] *= -1
    else:
        aud = np.array([15.0, 25.0, 1.7])
        flip = np.einsum("ij,ij->i", aud - c, n) < 0
        n[flip] *= -1
    pts, nrm, ar = [], [], []
    for tri, nn, area_val in zip(tris, n, a):
        if area_val < 1e-4:
            continue
        L = max(np.linalg.norm(tri[1] - tri[0]), np.linalg.norm(tri[2] - tri[1]), np.linalg.norm(tri[0] - tri[2]))
        k = max(1, int(np.ceil(L / cell)))
        uu, vv = np.meshgrid(np.arange(k) + 1 / 3, np.arange(k) + 1 / 3)
        m = uu + vv < k
        uu, vv = uu[m] / k, vv[m] / k
        p = tri[0] + uu[:, None] * (tri[1] - tri[0]) + vv[:, None] * (tri[2] - tri[0])
        pts.append(p + nn * 0.01)
        nrm.append(np.repeat(nn[None], len(p), 0))
        ar.append(np.full(len(p), area_val / len(p)))
    return np.concatenate(pts), np.concatenate(nrm), np.concatenate(ar)

wall_pts, wall_nrm, wall_area = sample_tris(wall_tris, cell=0.25, up_normal=False)
floor_pts, floor_nrm, floor_area = sample_tris(floor_tris, cell=0.25, up_normal=True)

ASPECT = 16 / 10  # 3840x2400 (or 16:9 3840x2160)

def eval_projector(pos, target, pts, nrm, area, occ_tris):
    f, r, u = frame(pos, target)
    v = pts - pos
    z = v @ f
    valid = z > 0.5
    x = np.where(valid, (v @ r) / np.where(valid, z, 1), 0)
    y = np.where(valid, (v @ u) / np.where(valid, z, 1), 0)
    hw = float(max(np.abs(x[valid]).max(), np.abs(y[valid]).max() * ASPECT) * 1.02)
    hh = hw / ASPECT
    tr = 1.0 / (2.0 * hw)
    dist = np.linalg.norm(v, axis=1)
    cosi = np.einsum("ij,ij->i", -v / dist[:, None], nrm)
    blocked = hits(pos, pts, occ_tris)
    lit = valid & (cosi > np.cos(np.radians(72))) & (~blocked)
    fov_h = math.degrees(2 * math.atan(hw))
    fov_v = math.degrees(2 * math.atan(hh))
    mean_dist = float(dist[lit].mean()) if lit.any() else float(dist.mean())
    min_dist = float(dist[lit].min()) if lit.any() else float(dist.min())
    max_dist = float(dist[lit].max()) if lit.any() else float(dist.max())
    # TD camera transform
    pos_td = td_coord(pos)
    f_td = td_coord(f)
    yaw = math.degrees(math.atan2(-f_td[0], -f_td[2]))
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, float(f_td[1])))))
    return {
        "pos_skp": [round(float(c), 3) for c in pos],
        "target_skp": [round(float(c), 3) for c in target],
        "t_td": [round(float(c), 4) for c in pos_td],
        "r_td": [round(pitch, 4), round(yaw, 4), 0.0],
        "fov_h_deg": round(fov_h, 3),
        "fov_v_deg": round(fov_v, 3),
        "throw_ratio_16_10": round(tr, 3),
        "throw_ratio_16_9": round(1.0 / (2.0 * max(np.abs(x[valid]).max(), np.abs(y[valid]).max() * (16/9)) * 1.02), 3),
        "mean_dist_m": round(mean_dist, 2),
        "min_dist_m": round(min_dist, 2),
        "max_dist_m": round(max_dist, 2),
        "image_width_at_mean_dist_m": round(mean_dist / tr, 2),
        "coverage_pct": round(float(area[lit].sum() / area.sum() * 100), 1),
        "shadow_pct": round(float(100 - area[lit].sum() / area.sum() * 100), 1),
        "total_target_area_m2": round(float(area.sum()), 1),
        "lit_area_m2": round(float(area[lit].sum()), 1),
        "_lit": lit
    }

# Evaluate Wall Projector options (1 projector -> both walls combined)
# Option W1: Front Center under Canopy Level (X=15.0, Y=24.5, Z=4.3) aimed at [15.0, 11.8, 2.7]
w_opt1 = eval_projector(
    np.array([15.0, 24.5, 4.3]),
    np.array([15.0, 11.8, 2.7]),
    wall_pts, wall_nrm, wall_area, canopy_tris
)
# Option W2: Mid-Stage Under-Canopy Center (X=15.0, Y=18.5, Z=4.6) aimed at [15.0, 11.8, 2.8]
w_opt2 = eval_projector(
    np.array([15.0, 18.5, 4.6]),
    np.array([15.0, 11.8, 2.8]),
    wall_pts, wall_nrm, wall_area, canopy_tris
)

# Evaluate Floor Projector options (1 projector -> stage floor)
# Option F1: High Front Truss Steep Downward (X=15.0, Y=24.2, Z=4.4) aimed at floor center [15.0, 15.8, 0.0]
f_opt1 = eval_projector(
    np.array([15.0, 24.2, 4.4]),
    np.array([15.0, 15.8, 0.0]),
    floor_pts, floor_nrm, floor_area, canopy_tris
)
# Option F2: Under-Canopy Overhead Center (X=15.0, Y=17.5, Z=5.95) aimed at floor center [15.0, 16.0, 0.0]
f_opt2 = eval_projector(
    np.array([15.0, 17.5, 5.95]),
    np.array([15.0, 16.0, 0.0]),
    floor_pts, floor_nrm, floor_area, canopy_tris
)

print("Wall Option W1 (Y=24.5, Z=4.3):", {k: v for k, v in w_opt1.items() if k != "_lit"})
print("Wall Option W2 (Y=18.5, Z=4.6):", {k: v for k, v in w_opt2.items() if k != "_lit"})
print("Floor Option F1 (Y=24.2, Z=4.4):", {k: v for k, v in f_opt1.items() if k != "_lit"})
print("Floor Option F2 (Y=17.5, Z=5.95):", {k: v for k, v in f_opt2.items() if k != "_lit"})
