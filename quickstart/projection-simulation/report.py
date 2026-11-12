"""Evaluate a 2-projector plan, render unfolded coverage map + perspective check view."""
import json
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sim import samples, evaluate, metrics, TRIS, OCC_FULL, RES, AUD, normals, TARGET_MASK, PATH, NAMES
from raster import raster, shade

plan = json.loads(sys.argv[1])  # {"L":[x,y,z], "R":[x,y,z]}
P, N, A = samples(0.25)
left = P[:, 0] <= 15.0
occ = TRIS[OCC_FULL]
res = {}
lit_by = np.zeros(len(P), int)
pix = {k: np.full(len(P), np.nan) for k in RES}
E = np.zeros(len(P))
for key, sel in (("L", left), ("R", ~left)):
    pos = np.array(plan[key], float)
    ev = evaluate(pos, P[sel], N[sel], A[sel], occ)
    # full lens frame may also reach the other half: evaluate all pts in that frame
    v = P - pos
    z = v @ ev["f"]
    x, y = (v @ ev["r"]) / z, (v @ ev["u"]) / z
    infr = (z > 0) & (np.abs(x) <= ev["hw"]) & (np.abs(y) <= ev["hh"])
    dist = np.linalg.norm(v, axis=1)
    cosi = np.einsum("ij,ij->i", -v / dist[:, None], N)
    from sim import hits
    vis = infr & (cosi > 0.17)
    vis[vis] &= ~hits(pos, P[vis], occ)
    ev2 = dict(ev, dist=dist, cosi=cosi)
    for rk, rv in RES.items():
        pl, e = metrics(pos, ev2, N, A, rv)
        own = vis & sel
        pix[rk][own] = pl[own]
    pl, e = metrics(pos, ev2, N, A, RES["WUXGA 1920x1200"])
    E[vis] += e[vis]
    lit_by[vis & sel] |= 1
    lit_by[vis & ~sel] |= 2  # spill/backup onto other half
    w = 2 * ev["hw"] * dist[sel].mean()
    res[key] = dict(pos=list(map(float, pos)), throw_ratio=round(float(ev["tr"]), 2),
             img_w_at_mean_dist_m=round(float(w), 1), mean_dist_m=round(float(dist[sel].mean()), 1),
             cover_own_half=round(float(A[sel][vis[sel]].sum() / A[sel].sum()), 3),
             aim=list(map(float, ev["f"])), right=list(map(float, ev["r"])), up=list(map(float, ev["u"])),
             hw=float(ev["hw"]), hh=float(ev["hh"]))
covered = (lit_by & 1).astype(bool)
tot = A.sum()
summary = dict(projectors=res, wall_area_visible_m2=round(float(tot), 1),
    covered_pct=round(100 * float(A[covered].sum() / tot), 1),
    shadow_pct=round(100 * float(A[~covered].sum() / tot), 1))
for rk in RES:
    q = pix[rk][covered]
    summary[f"pixel_mm_{rk}"] = dict(median=round(float(np.nanmedian(q) * 1000), 1), p90=round(float(np.nanpercentile(q, 90) * 1000), 1))
Ec = E[covered]
for refl, nm in ((0.75, "light_grey_paint"), (0.30, "dark_stone")):
    summary[f"nits_{nm}"] = dict(median=round(float(np.median(Ec) * refl / np.pi), 0), min=round(float(np.percentile(Ec, 5) * refl / np.pi), 0))
summary["lux_median"] = round(float(np.median(Ec)), 0)
json.dump(summary, open("plan_result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False, indent=1))

# ---------- unfolded elevation map ----------
# arc-length along the wall polyline (seen from audience): left wing -> left face -> chamfer -> right face -> right wing
poly = np.array([[4.71, 16.72], [5.28, 16.72], [13.99, 8.02], [16.02, 8.02], [24.72, 16.72], [25.29, 16.72]])
pts2 = P[:, :2]
seg_len = np.linalg.norm(np.diff(poly, axis=0), axis=1)
cum = np.r_[0, np.cumsum(seg_len)]
best = np.full(len(P), 1e9)
s_of = np.zeros(len(P))
for i in range(len(poly) - 1):
    a, b = poly[i], poly[i + 1]
    t = np.clip(((pts2 - a) @ (b - a)) / (seg_len[i] ** 2), 0, 1)
    dd = np.linalg.norm(pts2 - (a + t[:, None] * (b - a)), axis=1)
    m = dd < best
    best[m] = dd[m]
    s_of[m] = cum[i] + t[m] * seg_len[i]
# wings are slanted: use their projection onto the polyline
SC = 60  # px per metre
Wpx, Hpx = int(cum[-1] * SC) + 120, int(6.5 * SC) + 330
img = Image.new("RGB", (Wpx, Hpx), (18, 18, 20))
dr = ImageDraw.Draw(img)
try:
    font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 22)
    font_s = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 18)
    font_b = ImageFont.truetype("C:/Windows/Fonts/msyhbd.ttc", 30)
except OSError:
    font = font_s = font_b = ImageFont.load_default()
ox, oy = 60, 90
order = np.argsort(-best)  # draw columns (closer to audience) last
colL, colR, colBoth, colNone = (64, 120, 210), (214, 140, 60), (150, 110, 190), (200, 40, 50)
r = max(2, int(0.25 * SC * 0.55))
for i in np.argsort(best)[::-1]:
    lb = lit_by[i]
    own_left = left[i]
    if lb & 1:
        c = colL if own_left else colR
    else:
        c = colNone
    X = ox + s_of[i] * SC
    Y = oy + (6.0 - P[i, 2]) * SC
    dr.rectangle([X - r, Y - r, X + r, Y + r], fill=c)
for s in cum:
    dr.line([ox + s * SC, oy, ox + s * SC, oy + 6 * SC], fill=(90, 90, 90), width=1)
dr.rectangle([ox, oy, ox + cum[-1] * SC, oy + 6 * SC], outline=(160, 160, 160), width=2)
dr.text((ox, 20), "腾势 V 形墙 · 两台投影覆盖展开图（观众视角）", fill=(235, 235, 235), font=font_b)
labels = ["翼", "左墙 12.3m", "倒角", "右墙 12.3m", "翼"]
for i, lb in enumerate(labels):
    dr.text((ox + (cum[i] + cum[i + 1]) / 2 * SC - 40, oy + 6 * SC + 8), lb, fill=(200, 200, 200), font=font_s)
dr.text((ox - 50, oy - 10), "6m", fill=(200, 200, 200), font=font_s)
dr.text((ox - 50, oy + 6 * SC - 20), "0m", fill=(200, 200, 200), font=font_s)
ly = oy + 6 * SC + 50
for c, t in ((colL, "投影 L 覆盖"), (colR, "投影 R 覆盖"), (colNone, "打不到（遮挡 / 掠射 / 超出画面）")):
    dr.rectangle([ox, ly, ox + 26, ly + 26], fill=c)
    dr.text((ox + 36, ly - 2), t, fill=(225, 225, 225), font=font)
    ly += 40
s = summary
txt = [f"可见墙面 {s['wall_area_visible_m2']} m²，覆盖 {s['covered_pct']}%，打不到 {s['shadow_pct']}%",
f"像素尺寸（中位）WUXGA {s['pixel_mm_WUXGA 1920x1200']['median']} mm · 4K+ {s['pixel_mm_4K+ 5120x3200']['median']} mm",
              f"亮度（中位）浅灰涂料 {s['nits_light_grey_paint']['median']:.0f} nit · 深灰石材 {s['nits_dark_stone']['median']:.0f} nit",
              f"L 机 {res['L']['pos']} 投射比 {res['L']['throw_ratio']}  ·  R 机 {res['R']['pos']} 投射比 {res['R']['throw_ratio']}"]
tx = ox + 560
ty = oy + 6 * SC + 50
for t in txt:
    dr.text((tx, ty), t, fill=(225, 225, 225), font=font)
    ty += 36
img.save("coverage_unfolded.png")

# ---------- top plan with projector frusta ----------
keep = np.array([NAMES[i] != "/组件#1" for i in PATH])
T = TRIS[keep]
base = np.full((len(T), 3), 150)
top, (lo, sc, Hh) = raster(T, shade(T, base), [[1, 0, 0], [0, 1, 0], [0, 0, 1]], 1200)
dt = ImageDraw.Draw(top)
to_px = lambda p: (20 + (p[0] - lo[0]) * sc, Hh - (20 + (p[1] - lo[1]) * sc))
for key, col in (("L", colL), ("R", colR)):
    pr = res[key]
    pos = np.array(pr["pos"])
    f, rr, uu = map(np.array, (pr["aim"], pr["right"], pr["up"]))
    for sx in (-1, 1):
        d3 = f + sx * pr["hw"] * rr
        end = pos + d3 / np.linalg.norm(d3[:2]) * 14
        dt.line([to_px(pos), to_px(end)], fill=col, width=3)
    dt.ellipse([to_px(pos)[0] - 9, to_px(pos)[1] - 9, to_px(pos)[0] + 9, to_px(pos)[1] + 9], fill=col)
    dt.text((to_px(pos)[0] + 12, to_px(pos)[1] - 12), f"{key} h={pos[2]:.1f}m", fill=(20, 20, 20), font=font)
a = to_px(AUD)
dt.text((a[0] - 30, a[1]), "观众", fill=(20, 20, 20), font=font)
top.save("plan_top.png")

# ---------- coverage cells for SketchUp overlay ----------
cell = 0.25
up = np.array([0, 0, 1.0])
tang = np.cross(up, N)
tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-12
cen = P + N * 0.02
h = cell / 2 * 0.92
quads = np.stack([cen - tang * h - up * h, cen + tang * h - up * h, cen + tang * h + up * h, cen - tang * h + up * h], 1)
cls = np.where(lit_by & 1, np.where(left, 1, 2), 0)
np.savez_compressed("coverage_cells.npz", quads=quads, cls=cls)
