import json
import math
import os
import shutil
import numpy as np

WORK_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\_work\wall_floor_projection"
OUT_TD = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\td_assets_wall_floor"
ARCHIVE_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA 2\2026-11_DENZA Z\01_场景1_墙面双投影\墙地双投方案_1114"

d = np.load(os.path.join(WORK_DIR, "geom_new_skp.npz"), allow_pickle=True)
T, PATH = d["tris"], d["path"]
NAMES = list(d["paths"])

def to_td(p):
    return np.stack([p[..., 0], p[..., 2], -p[..., 1]], -1)

# Strictly separate occluder (hanging canopy /组件#46, /组件#47) from columns (/组件#72)
occ_ids = [i for i, n in enumerate(NAMES) if n.startswith("/组件#46") or n.startswith("/组件#47")]
col_ids = [i for i, n in enumerate(NAMES) if n.startswith("/组件#72")]

occ_tris = T[np.isin(PATH, occ_ids)]
occ_tris = occ_tris[(occ_tris.mean(1)[:, 0] < 35) & (occ_tris.mean(1)[:, 1] < 46)]
col_tris = T[np.isin(PATH, col_ids)]
col_tris = col_tris[(col_tris.mean(1)[:, 0] < 35) & (col_tris.mean(1)[:, 1] < 46)]
print(f"Strict canopy occluder tris: {len(occ_tris)}, foreground column tris: {len(col_tris)}")

def write_obj(path, group, tris):
    lines = [f"# {group} (TouchDesigner Y-up, metres)", f"g {group}"]
    vi = 1
    for tri in tris:
        P = to_td(tri)
        for p in P:
            lines.append(f"v {p[0]:.4f} {p[1]:.4f} {p[2]:.4f}")
        lines.append(f"f {vi} {vi+1} {vi+2}")
        vi += 3
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

write_obj(os.path.join(OUT_TD, "occluder.obj"), "occluder", occ_tris)
write_obj(os.path.join(OUT_TD, "columns_fg.obj"), "columns_fg", col_tris)

# Update Projector #1 (WALL) and Projector #2 (FLOOR) so both shoot cleanly under the Z=5.01m canopy!
# Note on TouchDesigner camera rotation (rord="xyz"):
# When ry=180 deg, R = Rz(0) * Ry(180) * Rx(rx) sends forward [0,0,-1] -> [0, sin(rx), cos(rx)].
# Therefore, to aim slightly DOWN (negative Y_td), rx must be NEGATIVE, and to aim steeply DOWN at floor, rx is NEGATIVE!
# Wait: let's verify! At rx = -35 deg, sin(-35) = -0.5736 (downward -Y_td), cos(-35) = +0.819 (+Z_td toward stage)!
# And for the local UP vector [0,1,0]: Rx(rx) -> [0, cos(rx), sin(rx)], then Ry(180) -> [0, cos(rx), -sin(rx)], which has positive Y_td (right-side up)!

proj_wall_pos_skp = np.array([15.0, 25.5, 2.80])   # Shoots cleanly under Z=5.01m canopy to full 6m height and full 20.58m width of V-wall!
proj_wall_aim_skp = np.array([15.0, 12.5, 2.90])
vec_w = proj_wall_aim_skp - proj_wall_pos_skp
vec_w_td = to_td(vec_w)
vec_w_td = vec_w_td / np.linalg.norm(vec_w_td)
yaw_w = math.degrees(math.atan2(-vec_w_td[0], -vec_w_td[2]))
pitch_w = math.degrees(math.asin(max(-1.0, min(1.0, vec_w_td[1]))))
fov_w_h = 98.0
tr_w = round(0.5 / math.tan(math.radians(fov_w_h / 2.0)), 3)

proj_floor_pos_skp = np.array([15.0, 19.8, 4.80])  # Right under Z=5.01m canopy rim, zero canopy shadow on floor!
proj_floor_aim_skp = np.array([15.0, 13.4, 0.0])
vec_f = proj_floor_aim_skp - proj_floor_pos_skp
vec_f_td = to_td(vec_f)
vec_f_td = vec_f_td / np.linalg.norm(vec_f_td)
yaw_f = math.degrees(math.atan2(-vec_f_td[0], -vec_f_td[2]))
pitch_f = math.degrees(math.asin(max(-1.0, min(1.0, vec_f_td[1]))))
fov_f_h = 82.0
tr_f = round(0.5 / math.tan(math.radians(fov_f_h / 2.0)), 3)

meta_path = os.path.join(OUT_TD, "projectors_wall_floor.json")
meta = json.load(open(meta_path, encoding="utf-8"))
meta["cameras"]["WALL"]["pos_sketchup_m"] = proj_wall_pos_skp.tolist()
meta["cameras"]["WALL"]["target_sketchup_m"] = proj_wall_aim_skp.tolist()
meta["cameras"]["WALL"]["t"] = [round(float(x), 4) for x in to_td(proj_wall_pos_skp)]
meta["cameras"]["WALL"]["r"] = [round(pitch_w, 4), round(yaw_w, 4), 0.0]
meta["cameras"]["WALL"]["fov_h_deg"] = fov_w_h
meta["cameras"]["WALL"]["throw_ratio_full_span"] = tr_w

meta["cameras"]["FLOOR"]["pos_sketchup_m"] = proj_floor_pos_skp.tolist()
meta["cameras"]["FLOOR"]["target_sketchup_m"] = proj_floor_aim_skp.tolist()
meta["cameras"]["FLOOR"]["t"] = [round(float(x), 4) for x in to_td(proj_floor_pos_skp)]
meta["cameras"]["FLOOR"]["r"] = [round(pitch_f, 4), round(yaw_f, 4), 0.0]
meta["cameras"]["FLOOR"]["fov_h_deg"] = fov_f_h
meta["cameras"]["FLOOR"]["throw_ratio_full_stage"] = tr_f

json.dump(meta, open(meta_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
for fn in ("occluder.obj", "columns_fg.obj", "projectors_wall_floor.json"):
    shutil.copy2(os.path.join(OUT_TD, fn), os.path.join(ARCHIVE_DIR, fn))
print("Updated projectors_wall_floor.json and strict occluder.obj!")
