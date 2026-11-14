import os
import json
import math
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont

WORK_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\_work\wall_floor_projection"
TD_ASSETS_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\td_assets_wall_floor"
ARCHIVE_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA 2\2026-11_DENZA Z\01_场景1_墙面双投影\墙地双投方案_1114"
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
TOTAL_WALL_W, WALL_H = float(cum[-1]), 6.0  # 27.784m unfolded, 20.58m direct span

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

def td_coord(p):
    return np.stack([p[..., 0], p[..., 2], -p[..., 1]], -1)

# Stage floor active performance zone (in front of V-wall: X=6.0..24.0m, Y=8.02..20.5m, nested inside the V-wall & columns)
# Plus full diamond floor polygon for 3D context
FLOOR_X_MIN, FLOOR_X_MAX = 6.0, 24.0   # 18.0 m width across V opening
FLOOR_Y_MIN, FLOOR_Y_MAX = 8.02, 19.27 # 11.25 m depth from V apex to front column line (16:10 aspect = 18.0 x 11.25m!)
FLOOR_W = FLOOR_X_MAX - FLOOR_X_MIN     # 18.0 m
FLOOR_D = FLOOR_Y_MAX - FLOOR_Y_MIN     # 11.25 m

# Build clipped active stage floor mesh (inside the V-wall opening y >= 8.02 + |x - 15| - 1.015, and y <= 19.27)
floor_tris_list = []
NX, NY = 64, 40
xs = np.linspace(FLOOR_X_MIN, FLOOR_X_MAX, NX + 1)
ys = np.linspace(FLOOR_Y_MIN, FLOOR_Y_MAX, NY + 1)
def inside_v_stage(x, y):
    # In front of the V-wall polyline
    dx = abs(x - 15.0)
    wall_y = 8.02 if dx <= 1.015 else 8.02 + (dx - 1.015)
    # Also inside front diamond boundary
    front_y = 26.37 - dx
    return (y >= wall_y - 0.05) and (y <= min(FLOOR_Y_MAX + 0.05, front_y))

for ix in range(NX):
    for iy in range(NY):
        x0, x1 = xs[ix], xs[ix + 1]
        y0, y1 = ys[iy], ys[iy + 1]
        xm, ym = 0.5 * (x0 + x1), 0.5 * (y0 + y1)
        if inside_v_stage(xm, ym):
            floor_tris_list.append([[x0, y0, 0.0], [x1, y0, 0.0], [x1, y1, 0.0]])
            floor_tris_list.append([[x0, y0, 0.0], [x1, y1, 0.0], [x0, y1, 0.0]])
floor_tris = np.array(floor_tris_list, dtype=np.float64)

def floor_uv(xy):
    # Audience looks from +Y toward -Y: audience-left is +X (24.0), audience-right is -X (6.0)
    # u: 0 (audience-left X=24.0) -> 1 (audience-right X=6.0), matching wall_combined horizontal direction!
    # v: 0 (stage front Y=19.27) -> 1 (V-wall apex Y=8.02), so top of floor texture (v=1) meets bottom of wall texture (v=0)!
    u = 1.0 - (xy[..., 0] - FLOOR_X_MIN) / FLOOR_W
    v = 1.0 - (xy[..., 1] - FLOOR_Y_MIN) / FLOOR_D
    return np.stack([np.clip(u, 0, 1), np.clip(v, 0, 1)], -1)

def write_obj(path, groups):
    lines = ["# Denza Wall+Floor Mapping Mesh (metres, TD Y-up)"]
    vi, ti = 1, 1
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

# Compute practical projector configurations:
# 1. WALL Projector (1 projector covering both left + right V-walls as a single stitched/spanned canvas):
#    - Direct opening span across V-wall wings = 20.58m (X = 4.71..25.29m at Y = 16.72m), apex at (15.0, 8.02m), height = 6.0m.
#    - Recommended Camera Position W_MAIN: X = 15.0m (center line), Y = 27.5m (behind front truss/canopy line), Z = 4.2m (under canopy 4.55m/5.01m bottom edge), aiming at [15.0, 12.0, 2.8].
#      - Distance to wings (Y=16.72): sqrt(10.29^2 + 10.78^2) = 14.9m (depth dy = 10.78m -> half-angle tan = 10.29/10.78 = 0.954 -> TR = 0.524 for full 20.58m wings, or TR = 0.65 for core 17.5m V-wall span!)
#      - Distance to V-apex (Y=8.02): 19.5m; Mean throw distance across V-wall = 15.6m.
# 2. FLOOR Projector (1 projector covering the stage floor in front of the V-wall):
#    - Active floor zone inside V-pocket: width 16.0m..18.0m (or core 12.0m x 7.5m under canopy), depth Y = 8.02..19.27m.
#    - Recommended Camera Position F_MAIN (Steep Front-Truss Downward): X = 15.0m, Y = 23.5m, Z = 4.4m (or Under-Canopy Overhead X = 15.0m, Y = 16.8m, Z = 5.95m aiming at [15.0, 13.8, 0.0]).
#      - Let's include BOTH in projectors_wall_floor.json, with F_MAIN set to the clean steep overhead/front-truss rig [15.0, 21.5, 5.8] aiming at [15.0, 13.8, 0.0] (mean throw distance 9.6m, throw ratio 0.62, FOV_H = 78.6 deg)!

def make_cam_entry(name, target_group, pos_skp, aim_skp, fov_h_deg, res=(3840, 2400), notes=""):
    pos = np.array(pos_skp, dtype=float)
    aim = np.array(aim_skp, dtype=float)
    f = aim - pos
    dist_center = float(np.linalg.norm(f))
    f = f / dist_center
    pos_td = td_coord(pos)
    f_td = td_coord(f)
    yaw = math.degrees(math.atan2(-f_td[0], -f_td[2]))
    pitch = math.degrees(math.asin(max(-1.0, min(1.0, float(f_td[1])))))
    aspect = res[0] / res[1]
    hw = math.tan(math.radians(fov_h_deg / 2.0))
    hh = hw / aspect
    fov_v_deg = math.degrees(2.0 * math.atan(hh))
    tr = 1.0 / (2.0 * hw)
    return {
        "name": name,
        "target_group": target_group,
        "pos_skp_m": [round(float(x), 3) for x in pos],
        "aim_skp_m": [round(float(x), 3) for x in aim],
        "t": [round(float(x), 4) for x in pos_td],
        "r": [round(pitch, 4), round(yaw, 4), 0.0],
        "rord": "xyz",
        "fov_h_deg": round(fov_h_deg, 3),
        "fov_v_deg": round(fov_v_deg, 3),
        "throw_ratio": round(tr, 3),
        "center_throw_distance_m": round(dist_center, 2),
        "image_width_at_center_m": round(dist_center / tr, 2),
        "resolution": list(res),
        "notes": notes
    }

cam_wall = make_cam_entry(
    "WALL_COMBINED (一台投影投两面折墙)",
    "wall_combined",
    pos_skp=[15.0, 27.5, 4.2],
    aim_skp=[15.0, 12.2, 2.7],
    fov_h_deg=82.0,  # TR = 0.576 (covers full 20.58m V-opening from Y=27.5m; or TR=0.68 covers 17.5m core V-wall)
    res=(3840, 2400),
    notes="单机居中正投两面V形折墙合成画面；机位高度4.2m避开5.01m吊顶下沿遮挡；到折墙翼端14.9m、到V角顶点19.5m、平均投距约15.6m；全幅20.58m开口需约0.55-0.58短焦镜头（若缩窄两侧翼边投核心17.5m折墙则镜头比约0.65-0.75）。"
)

cam_floor = make_cam_entry(
    "FLOOR_STAGE (一台投影单独投地面)",
    "floor_stage",
    pos_skp=[15.0, 21.5, 5.8],
    aim_skp=[15.0, 13.6, 0.0],
    fov_h_deg=78.0,  # TR = 0.618, center distance = 9.8m -> width ~15.8m across stage floor
    res=(3840, 2400),
    notes="单机高机位斜下投射V形墙前方舞台地面；机位位于中庭顶部(Z=5.8m, Y=21.5m)朝舞台中心(Y=13.6m, Z=0m)俯投；中心投距约9.8m（最短5.9m、最远14.6m），覆盖宽约15.8m×深11.2m舞台地面，镜头比约0.62（若仅投中心12m×7.5m核心舞区则镜头比约0.80）。"
)

proj_meta = {
    "schema": "denza-wall-floor-dual-projection-v1",
    "updated_at": "2026-11-14",
    "architecture": "1 Projector -> Both V-Walls Combined + 1 Projector -> Stage Floor Separate",
    "projector_assumed": "Panasonic PT-RQ45K class (assumed reference, 3840x2400 16:10 or 3840x2160 16:9)",
    "units": "m, TD Y-up (SketchUp Z-up converted via (x,y,z)->(x,z,-y))",
    "wall_geometry": {
        "unfolded_width_m": round(TOTAL_WALL_W, 3),
        "direct_span_width_m": 20.58,
        "height_m": WALL_H,
        "apex_xy_m": [15.0, 8.02],
        "wings_xy_m": [[4.71, 16.72], [25.29, 16.72]],
        "visible_area_m2": 159.8,
        "recommended_canvas_unfolded": [7680, 1656],
        "recommended_canvas_16_9": [3840, 2160],
        "recommended_projector_output": [3840, 2400]
    },
    "floor_geometry": {
        "active_stage_width_m": FLOOR_W,
        "active_stage_depth_m": FLOOR_D,
        "active_stage_area_m2": 128.5,
        "full_diamond_floor_area_m2": 295.8,
        "recommended_canvas_16_9": [3840, 2160],
        "recommended_projector_output": [3840, 2400]
    },
    "cameras": {
        "WALL": cam_wall,
        "FLOOR": cam_floor
    }
}

with open(os.path.join(TD_ASSETS_DIR, "projectors_wall_floor.json"), "w", encoding="utf-8") as f:
    json.dump(proj_meta, f, ensure_ascii=False, indent=2)

# Generate high-res UV Template 1: wall_combined_uv_template.png (3840x2160 & 7680x1656)
font_lg = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
font_md = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 34)
font_sm = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 24)

def make_wall_template(W, Hh, filename):
    img = Image.new("RGB", (W, Hh), (12, 14, 18))
    dr = ImageDraw.Draw(img)
    sx = W / TOTAL_WALL_W
    # Draw wall mesh wireframe
    for t in wall_tris:
        s = arc(t[:, :2])
        pts = [(float((TOTAL_WALL_W - s[k]) * sx), float(Hh - t[k, 2] / WALL_H * Hh)) for k in range(3)]
        dr.polygon(pts, fill=(28, 34, 46), outline=(58, 70, 92))
    # Horizontal height lines (1m..5m)
    for m in range(1, 6):
        y = int(Hh - m / WALL_H * Hh)
        dr.line([(0, y), (W, y)], fill=(70, 80, 100), width=2)
        dr.text((24, y - 40), f"H = {m}.0m", fill=(160, 175, 200), font=font_sm)
    # Vertical section seams
    labels = ["右翼边 (0.57m)", "右墙面 · RIGHT WALL (12.31m)", "V角折缝 (2.03m)", "左墙面 · LEFT WALL (12.30m)", "左翼边 (0.57m)"]
    for i, c in enumerate(cum):
        x = int((TOTAL_WALL_W - c) * sx)
        dr.line([(x, 0), (x, Hh)], fill=(255, 110, 30), width=5)
    # Center V-apex line
    cx = W // 2
    dr.line([(cx, 0), (cx, Hh)], fill=(0, 220, 255), width=6)
    # Top 1.0m canopy occlusion warning band
    top_band_h = int(Hh / WALL_H * 1.0)
    dr.rectangle([0, 0, W, top_band_h], outline=(245, 165, 35), width=5)
    dr.text((W // 2 - 480, 18), "▲ 顶部约 1.0m（5m–6m）：中庭悬挂盒遮挡带，核心视觉保持在 0m–5m", fill=(245, 185, 60), font=font_md)
    # Section labels
    for i, lb in enumerate(labels):
        s_mid = 0.5 * (cum[i] + cum[i + 1])
        x_mid = int((TOTAL_WALL_W - s_mid) * sx)
        if i in (1, 3):
            dr.text((x_mid - 260, Hh // 2 - 60), lb, fill=(240, 245, 255), font=font_lg)
        elif i == 2:
            dr.text((x_mid - 110, Hh // 2 + 40), lb, fill=(0, 220, 255), font=font_md)
    dr.text((40, Hh - 60), f"DENZA Z · 墙面单机合投画布 (Projector 1 -> Left + Right V-Walls Combined) | 展开 {TOTAL_WALL_W:.2f}m × {WALL_H:.1f}m | 开口跨度 20.58m", fill=(200, 210, 230), font=font_md)
    img.save(os.path.join(TD_ASSETS_DIR, filename))

make_wall_template(7680, 1656, "wall_combined_uv_template.png")
make_wall_template(3840, 2160, "wall_combined_uv_16x9.png")

# Generate high-res UV Template 2: floor_uv_template.png (3840x2400 & 3840x2160)
def make_floor_template(W, Hh, filename):
    img = Image.new("RGB", (W, Hh), (10, 12, 16))
    dr = ImageDraw.Draw(img)
    # Draw floor active polygon
    for t in floor_tris:
        uvs = floor_uv(t[:, :2])
        pts = [(float(uvs[k, 0] * W), float((1.0 - uvs[k, 1]) * Hh)) for k in range(3)]
        dr.polygon(pts, fill=(22, 32, 38), outline=(42, 60, 72))
    # Meter grid in X (6..24m) and Y (8.02..19.27m)
    for xm in range(6, 25):
        u = 1.0 - (xm - FLOOR_X_MIN) / FLOOR_W
        px = int(u * W)
        col = (0, 210, 255) if xm == 15 else (65, 85, 100)
        w_line = 5 if xm == 15 else 2
        dr.line([(px, 0), (px, Hh)], fill=col, width=w_line)
        dr.text((px + 6, Hh - 45), f"X={xm}m", fill=(140, 165, 185), font=font_sm)
    for ym in range(9, 20):
        v = 1.0 - (ym - FLOOR_Y_MIN) / FLOOR_D
        py = int((1.0 - v) * Hh)
        dr.line([(0, py), (W, py)], fill=(65, 85, 100), width=2)
        dr.text((20, py - 32), f"Y={ym}m", fill=(140, 165, 185), font=font_sm)
    # Draw V-wall contact boundary at top of floor canvas (v -> 1)
    v_pts = []
    for pt in poly:
        uv = floor_uv(pt)
        v_pts.append((float(uv[0] * W), float((1.0 - uv[1]) * Hh)))
    dr.line(v_pts, fill=(255, 110, 30), width=10)
    dr.text((W // 2 - 340, 28), "▲ 墙地交界线（V形折墙底边 Y=8.02m..16.72m，与墙面画面底部无缝衔接）", fill=(255, 145, 60), font=font_md)
    # Draw Dancer Formation Circles (P12/P13/P19: Solo axis & 5-dancer/group tire-sequence circle at X=15.0, Y=13.6m)
    c_uv = floor_uv(np.array([15.0, 13.6]))
    cx, cy = int(c_uv[0] * W), int((1.0 - c_uv[1]) * Hh)
    for idx_c, (r_m, col_c, lb) in enumerate([(1.5, (255, 120, 40), "独舞轴心 R=1.5m (P13)"), (3.2, (0, 220, 255), "5人/群舞圆环阵型 R=3.2m (P12/P19)"), (4.8, (120, 200, 160), "外圈队列包络 R=4.8m")]):
        rx = int(r_m / FLOOR_W * W)
        ry = int(r_m / FLOOR_D * Hh)
        dr.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=col_c, width=4)
        dr.text((cx - 180, cy - ry + 14), lb, fill=col_c, font=font_md)
    # Draw Z-configuration diagonal guide lines
    dr.line([(cx - int(4.0 / FLOOR_W * W), cy - int(2.8 / FLOOR_D * Hh)),
             (cx + int(4.0 / FLOOR_W * W), cy - int(2.8 / FLOOR_D * Hh)),
             (cx - int(4.0 / FLOOR_W * W), cy + int(2.8 / FLOOR_D * Hh)),
             (cx + int(4.0 / FLOOR_W * W), cy + int(2.8 / FLOOR_D * Hh))], fill=(255, 160, 50), width=4)
    dr.text((40, Hh - 95), f"DENZA Z · 舞台地面单机独投画布 (Projector 2 -> Stage Floor Separate) | 覆盖 {FLOOR_W:.1f}m × {FLOOR_D:.2f}m", fill=(220, 235, 245), font=font_md)
    img.save(os.path.join(TD_ASSETS_DIR, filename))

make_floor_template(3840, 2400, "floor_uv_template.png")
make_floor_template(3840, 2160, "floor_uv_16x9.png")

# Generate Architectural Plan + Section Diagram: coverage_wall_floor_plan.png
plan_img = Image.new("RGB", (2400, 1350), (14, 16, 22))
pdr = ImageDraw.Draw(plan_img)

# Left panel: Top-Down Plan View (X: 0..30m, Y: 1..30m)
def to_plan_px(x, y):
    # X: 2..28m -> px 80..1180; Y: 1.5..29.5m -> py 200..1240
    px = int(80 + (x - 2.0) / 26.0 * 1100)
    py = int(200 + (y - 1.5) / 28.0 * 1040)
    return (px, py)

pdr.text((80, 40), "DENZA Z · 场景一「一机投双墙 + 一机投地面」空间机位与覆盖平面/剖面图", fill=(245, 248, 255), font=font_lg)
pdr.text((80, 105), "左：俯视平面图（SketchUp 真实比例，单位：米） | 右：中轴纵剖面图（X = 15.0m）与核心光学参数", fill=(165, 180, 205), font=font_md)

# Draw diamond floor outline
diamond_pts = [to_plan_px(2.84, 14.21), to_plan_px(15.0, 2.05), to_plan_px(27.16, 14.21), to_plan_px(15.0, 26.37)]
pdr.polygon(diamond_pts, fill=(24, 28, 36), outline=(70, 80, 100))

# Draw active floor projection zone
for t in floor_tris:
    pts = [to_plan_px(t[k, 0], t[k, 1]) for k in range(3)]
    pdr.polygon(pts, fill=(18, 56, 72))

# Draw V-wall
wall_plan_pts = [to_plan_px(pt[0], pt[1]) for pt in poly]
pdr.line(wall_plan_pts, fill=(255, 120, 30), width=10)
pdr.text((to_plan_px(15.0, 8.02)[0] - 110, to_plan_px(15.0, 8.02)[1] - 42), "V形折墙顶点 (15.0, 8.02)", fill=(255, 150, 70), font=font_sm)
pdr.text((to_plan_px(4.71, 16.72)[0] - 40, to_plan_px(4.71, 16.72)[1] - 40), "右墙翼 (4.71, 16.72)", fill=(255, 150, 70), font=font_sm)
pdr.text((to_plan_px(25.29, 16.72)[0] - 120, to_plan_px(25.29, 16.72)[1] - 40), "左墙翼 (25.29, 16.72)", fill=(255, 150, 70), font=font_sm)

# Draw central canopy outline (10.05..19.95, 12.66..22.56 rotated square)
canopy_plan = [to_plan_px(15.0, 12.66), to_plan_px(19.95, 17.61), to_plan_px(15.0, 22.56), to_plan_px(10.05, 17.61)]
pdr.polygon(canopy_plan, outline=(220, 180, 60), width=3)
pdr.text((to_plan_px(15.0, 17.6)[0] - 110, to_plan_px(15.0, 17.6)[1] - 14), "中庭悬挂顶框 (Z=5.01~6.2m)", fill=(220, 180, 60), font=font_sm)

# Draw Projector 1 (Wall) and frustum rays
pw_px = to_plan_px(15.0, 27.5)
pdr.line([pw_px, to_plan_px(4.71, 16.72)], fill=(255, 130, 40), width=3)
pdr.line([pw_px, to_plan_px(25.29, 16.72)], fill=(255, 130, 40), width=3)
pdr.line([pw_px, to_plan_px(15.0, 8.02)], fill=(255, 130, 40), width=2)
pdr.ellipse([pw_px[0]-12, pw_px[1]-12, pw_px[0]+12, pw_px[1]+12], fill=(255, 110, 20), outline=(255, 255, 255))
pdr.text((pw_px[0] - 210, pw_px[1] + 16), "投影机 #1 (投双墙合成画面) [15.0, 27.5, 4.2m]", fill=(255, 150, 60), font=font_md)

# Draw Projector 2 (Floor) and frustum rays
pf_px = to_plan_px(15.0, 21.5)
pdr.line([pf_px, to_plan_px(6.5, 15.5)], fill=(0, 220, 255), width=3)
pdr.line([pf_px, to_plan_px(23.5, 15.5)], fill=(0, 220, 255), width=3)
pdr.line([pf_px, to_plan_px(15.0, 8.5)], fill=(0, 220, 255), width=2)
pdr.ellipse([pf_px[0]-12, pf_px[1]-12, pf_px[0]+12, pf_px[1]+12], fill=(0, 210, 255), outline=(255, 255, 255))
pdr.text((pf_px[0] - 210, pf_px[1] + 16), "投影机 #2 (单独投地面) [15.0, 21.5, 5.8m]", fill=(0, 225, 255), font=font_md)

# Right panel: Side Elevation along X=15m (Y: 6..29m -> px 1280..2320, Z: 0..10m -> py 760..220)
def to_elev_px(y, z):
    px = int(1280 + (y - 6.0) / 23.0 * 1040)
    py = int(740 - (z / 10.0) * 500)
    return (px, py)

# Floor line z=0
pdr.line([to_elev_px(6.0, 0.0), to_elev_px(28.5, 0.0)], fill=(0, 210, 255), width=6)
pdr.text((1320, 752), "舞台地面 (Z = 0.0m, 投射深 Y=8.02m~19.3m)", fill=(0, 220, 255), font=font_sm)
# V-wall vertical line at Y=8.02..16.72, Z=0..6m
pdr.rectangle([to_elev_px(8.02, 6.0), to_elev_px(16.72, 0.0)], outline=(255, 120, 30), width=4)
pdr.line([to_elev_px(8.02, 0.0), to_elev_px(8.02, 6.0)], fill=(255, 120, 30), width=8)
pdr.text((1285, 390), "V形折墙\nH=6.0m", fill=(255, 150, 70), font=font_sm)
# Canopy box Y=12.66..22.56, Z=5.01..8.66
pdr.rectangle([to_elev_px(12.66, 8.66), to_elev_px(22.56, 5.01)], fill=(45, 42, 32), outline=(220, 180, 60), width=3)
pdr.text((to_elev_px(13.5, 7.2)[0], to_elev_px(13.5, 7.2)[1]), "中庭吊顶结构 (下沿 Z=5.01m, 顶板 Z=6.20m)", fill=(230, 195, 80), font=font_sm)

# Projector 1 in elevation
pw_el = to_elev_px(27.5, 4.2)
pdr.line([pw_el, to_elev_px(8.02, 4.8)], fill=(255, 130, 40), width=3)
pdr.line([pw_el, to_elev_px(8.02, 0.0)], fill=(255, 130, 40), width=3)
pdr.ellipse([pw_el[0]-10, pw_el[1]-10, pw_el[0]+10, pw_el[1]+10], fill=(255, 110, 20), outline=(255, 255, 255))
pdr.text((pw_el[0] - 250, pw_el[1] - 42), "投影 #1 (双墙合投 Z=4.2m)", fill=(255, 150, 60), font=font_sm)

# Projector 2 in elevation
pf_el = to_elev_px(21.5, 5.8)
pdr.line([pf_el, to_elev_px(8.02, 0.0)], fill=(0, 220, 255), width=3)
pdr.line([pf_el, to_elev_px(19.27, 0.0)], fill=(0, 220, 255), width=3)
pdr.ellipse([pf_el[0]-10, pf_el[1]-10, pf_el[0]+10, pf_el[1]+10], fill=(0, 210, 255), outline=(255, 255, 255))
pdr.text((pf_el[0] - 120, pf_el[1] - 42), "投影 #2 (地面独投 Z=5.8m)", fill=(0, 225, 255), font=font_sm)

# Parameter summary box in bottom-right
pdr.rectangle([1280, 820, 2330, 1290], fill=(22, 26, 34), outline=(70, 85, 110), width=2)
summary_lines = [
    "【架构调整：一机投双墙合成画面 + 一机单独投地面】",
    "1. 投影机 #1（墙面合投 · WALL_COMBINED）：",
    "   · 目标表面：左墙 + 右墙拼成单一连续画面（展开 27.78m×6.0m，V口水平跨度 20.58m）",
    "   · 模拟机位：中轴 X=15.0m, Y=27.5m, 高度 Z=4.2m（低于 5.01m 吊顶下沿，避开正面遮挡）",
    "   · 投距与镜头比：到左右墙翼约 14.9m、到V角顶点 19.5m（平均约 15.6m）；",
    "     全幅覆盖 20.58m 开口需短焦镜头 TR ≈ 0.55–0.58；若投核心 17.5m 折墙则 TR ≈ 0.65–0.75。",
    "2. 投影机 #2（地面独投 · FLOOR_STAGE）：",
    "   · 目标表面：V形折墙前方菱形舞台地面（核心舞区宽 18.0m × 深 11.25m，或内圈 12m × 7.5m）",
    "   · 模拟机位：中庭下沿高机位 X=15.0m, Y=21.5m, 高度 Z=5.8m（或黑棚马道高点下投）",
    "   · 投距与镜头比：中心投距约 9.8m（最近 5.9m、最远 14.6m）；覆盖 15.8m 宽地面 TR ≈ 0.62",
    "     （若仅投中心 12m × 7.5m 舞者圆环阵型区，则 TR ≈ 0.80）。"
]
for idx_l, line_str in enumerate(summary_lines):
    col_txt = (255, 200, 90) if idx_l == 0 else ((235, 240, 250) if line_str.startswith(("1.", "2.")) else (185, 198, 218))
    pdr.text((1305, 838 + idx_l * 39), line_str, fill=col_txt, font=font_sm)

plan_path = os.path.join(TD_ASSETS_DIR, "coverage_wall_floor_plan.png")
plan_img.save(plan_path)

# Copy all generated assets to ARCHIVE_DIR as well
for fn in os.listdir(TD_ASSETS_DIR):
    shutil.copy2(os.path.join(TD_ASSETS_DIR, fn), os.path.join(ARCHIVE_DIR, fn))

print("Generated all wall+floor mapping OBJs, UV templates, JSON, and plan diagram!")
