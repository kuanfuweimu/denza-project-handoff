"""Export mapping assets for TouchDesigner (Y-up, metres).

Outputs in td_assets/:
         wall_mapping.obj   groups wall_L, wall_R (unfolded UVs), occluder (box, black)
         projectors.json    plan-C projector cameras in TD coords
         uv_template.png    content canvas template (unfolded wall)
"""
import json
import math
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = "td_assets"
os.makedirs(OUT, exist_ok=True)
d = np.load("geom.npz")
T, PATH = d["tris"], d["path"]
NAMES = json.load(open("geom.json", encoding="utf-8"))["paths"]
WALL = ["/组件#56/G", "/组件#56/G/G", "/组件#57", "/组件#56/G/组件#15"]
OCC = ["/组件#46", "/组件#47"]

poly = np.array([[4.71, 16.72], [5.28, 16.72], [13.99, 8.02], [16.02, 8.02], [24.72, 16.72], [25.29, 16.72]])
seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
cum = np.r_[0, np.cumsum(seg)]
TOTAL, HEIGHT = float(cum[-1]), 6.0


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


def td(p):  # SketchUp Z-up -> TD Y-up
    return np.stack([p[..., 0], p[..., 2], -p[..., 1]], -1)


ids = lambda names: np.isin(PATH, [NAMES.index(n) for n in names])
wall = T[ids(WALL)]
occ = T[ids(OCC)]
n = np.cross(wall[:, 1] - wall[:, 0], wall[:, 2] - wall[:, 0])
A = 0.5 * np.linalg.norm(n, axis=1)
wall = wall[(A > 1e-6) & (np.abs(n[:, 2]) / (2 * A + 1e-12) < 0.95)]  # drop horizontal caps
cen = wall.mean(1)
side_left = cen[:, 0] > 15.0  # audience-left = +X in SketchUp (audience looks toward -Y)

lines = ["# Denza V-wall mapping mesh, metres, Y-up. UV = unfolded wall (u: 0..1 along %.2fm, v: 0..1 over 6m)" % TOTAL]
vi = 1


def emit(group, tris, uv=True):
    global vi
    lines.append(f"g {group}")
    for tri in tris:
        P = td(tri)
        for p in P:
            lines.append(f"v {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}")
        if uv:
            s = arc(tri[:, :2])
            for k in range(3):
                lines.append(f"vt {1 - s[k] / TOTAL:.5f} {tri[k, 2] / HEIGHT:.5f}")
            lines.append(f"f {vi}/{vi} {vi + 1}/{vi + 1} {vi + 2}/{vi + 2}")
        else:
            lines.append(f"f {vi} {vi + 1} {vi + 2}")
        vi += 3


emit("wall_L", wall[side_left])
emit("wall_R", wall[~side_left])
emit("occluder", occ, uv=False)
open(f"{OUT}/wall_mapping.obj", "w").write("\n".join(lines) + "\n")

plan = json.load(open("out_C/plan_result.json", encoding="utf-8"))
cams = {}
for key, pr in ((k2, plan["projectors"]["R" if k2 == "L" else "L"]) for k2 in ("L", "R")):
    pos = td(np.array(pr["pos"]))
    f = td(np.array(pr["aim"]))
    yaw = math.degrees(math.atan2(-f[0], -f[2]))
    pitch = math.degrees(math.asin(max(-1, min(1, f[1]))))
    cams[key] = dict(
        target_group="wall_L" if key == "L" else "wall_R",
        t=[round(float(x), 4) for x in pos], r=[round(pitch, 4), round(yaw, 4), 0.0], rord="xyz",
        fov_h_deg=round(math.degrees(2 * math.atan(pr["hw"])), 4),
        fov_v_deg=round(math.degrees(2 * math.atan(pr["hh"])), 4),
        throw_ratio=pr["throw_ratio"], resolution=[3840, 2400], native=[1920, 1200])
meta = dict(projector="Panasonic PT-RQ45K class (assumed), 3840x2400 Quad Pixel Drive", units="m, Y-up",
            wall_unfolded_m=[round(TOTAL, 3), HEIGHT], content_canvas=[7680, 1656],
            sections_m=[round(float(c), 3) for c in cum], cameras=cams)
json.dump(meta, open(f"{OUT}/projectors.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# content template: unfolded canvas with section borders and column positions
W, Hh = meta["content_canvas"]
img = Image.new("RGB", (W, Hh), (14, 14, 16))
dr = ImageDraw.Draw(img)
font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 44)
sx = W / TOTAL
for t in wall:
    s = arc(t[:, :2])
    pts = [(float((TOTAL - s[k]) * sx), float(Hh - t[k, 2] / HEIGHT * Hh)) for k in range(3)]
    c = (46, 52, 66) if cen.size else (0, 0, 0)
    dr.polygon(pts, outline=(70, 80, 100))
for c in cum:
    dr.line([(c * sx, 0), (c * sx, Hh)], fill=(200, 60, 60), width=4)
for m in range(1, 6):
    y = Hh - m / HEIGHT * Hh
    dr.line([(0, y), (W, y)], fill=(60, 60, 60), width=1)
    dr.text((10, y - 50), f"{m}m", fill=(150, 150, 150), font=font)
dr.rectangle([0, 0, W, Hh / HEIGHT * 1.0], outline=(230, 160, 40), width=6)
dr.text((cum[1] * sx + 30, 20), "顶部约 1m：方案 C 被悬挂盒子遮挡，避免放关键内容", fill=(230, 160, 40), font=font)
for i, lb in enumerate(["翼", "左墙 · 投影 L", "倒角", "右墙 · 投影 R", "翼"]):
    dr.text(((cum[i] + cum[i + 1]) / 2 * sx - 120, Hh / 2), lb, fill=(220, 220, 220), font=font)
img.save(f"{OUT}/uv_template.png")
print(json.dumps(meta, ensure_ascii=False, indent=1))
print("tris wall_L", int(side_left.sum()), "wall_R", int((~side_left).sum()), "occ", len(occ))
