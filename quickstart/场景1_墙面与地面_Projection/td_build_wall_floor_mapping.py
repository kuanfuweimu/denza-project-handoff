"""Build the Denza Scene 1 Wall+Floor Dual-Projector 3D Mapping network inside TouchDesigner.
Architecture (11/14 Update):
  - Projector #1 (WALL):  1 projector -> Combined Left+Right V-Walls (wall_combined.obj, 27.784m x 6.0m)
  - Projector #2 (FLOOR): 1 projector -> Stage Floor separately (floor_stage.obj, 18.0m x 11.25m)
  - Occluders:            Central hanging square canopy (occluder.obj) + 4 foreground slanted columns (columns_fg.obj)

Run inside TouchDesigner 2025.32460 (Textport or TDMCP execute_code):
    exec(open(r'D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/td_wall_floor_pops/td_build_wall_floor_mapping.py', encoding='utf-8').read())
"""
import json
import os

ROOT = r"D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/td_assets_wall_floor"
META = json.load(open(os.path.join(ROOT, "projectors_wall_floor.json"), encoding="utf-8"))
NULL_BLUE = (0.1843137255, 0.3490196078, 0.6784313725)  # #2F59AD
report = {"created": [], "par_fail": []}


def setp(op_, **kw):
    for k, v in kw.items():
        p = getattr(op_.par, k, None)
        if p is None:
            report["par_fail"].append(f"{op_.path}.{k}")
            continue
        try:
            if isinstance(v, str) and v.startswith("="):
                p.expr = v[1:]
            else:
                p.val = v
        except Exception as e:
            report["par_fail"].append(f"{op_.path}.{k}={v!r}: {e}")


def mk(parent, optype, name, x, y, **pars):
    o = parent.create(optype, name)
    o.nodeX, o.nodeY = x, y
    o.viewer = True
    setp(o, **pars)
    if "null" in o.type.lower():
        o.color = NULL_BLUE
    report["created"].append(o.path)
    return o


def mk_annotate(parent, name, title, text, x, y, w, h, color=(0.14, 0.18, 0.24)):
    a = parent.create(annotateCOMP, name)
    a.nodeX, a.nodeY = x, y
    a.nodeWidth, a.nodeHeight = w, h
    setp(a, Titletext=title, Bodytext=text,
         Backcolorr=color[0], Backcolorg=color[1], Backcolorb=color[2], Backcoloralpha=0.32)
    report["created"].append(a.path)
    return a


parent_comp = op("/project1") or root
old = parent_comp.op("mapping_wall_floor")
if old is not None:
    i = 1
    while parent_comp.op(f"mapping_wall_floor_old{i}") is not None:
        i += 1
    old.name = f"mapping_wall_floor_old{i}"

M = parent_comp.create(baseCOMP, "mapping_wall_floor")
M.nodeX, M.nodeY = 0, -450
M.viewer = True
M.par.parentshortcut = "Mappingwallfloor"

# ---------------- 1. Custom Parameters ----------------
pg_map = M.appendCustomPage("Mapping")
s_w = pg_map.appendMenu("Wallsource", label="Wall Source")[0]
s_w.menuNames = ["template", "pops", "video", "spout"]
s_w.menuLabels = ["Wall UV Template", "POPs Generator (null_pops_wall)", "Video File", "Spout In"]
pg_map.appendTOP("Wallcontent", label="Wall Content TOP")
pg_map.appendFile("Wallvideo", label="Wall Video File")
pg_map.appendStr("Wallspout", label="Wall Spout Name")

s_f = pg_map.appendMenu("Floorsource", label="Floor Source")[0]
s_f.menuNames = ["template", "pops", "video", "spout"]
s_f.menuLabels = ["Floor UV Template", "POPs Generator (null_pops_floor)", "Video File", "Spout In"]
pg_map.appendTOP("Floorcontent", label="Floor Content TOP")
pg_map.appendFile("Floorvideo", label="Floor Video File")
pg_map.appendStr("Floorspout", label="Floor Spout Name")

pg_map.appendToggle("Testpattern", label="Force UV Templates")
pg_map.appendToggle("Includecolumns", label="Include 4 Slanted Columns")
pg_map.appendFloat("Blackout", label="Master Blackout")[0].normMax = 1.0

M.par.Wallcontent.val = "/project1/z_dance_pops/null_pops_wall"
M.par.Floorcontent.val = "/project1/z_dance_pops/null_pops_floor"
M.par.Wallvideo.val = r"D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/strings-z-dance/out/z-dance_wall_combined_30s_4k60.mp4"
M.par.Floorvideo.val = r"D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/strings-z-dance/out/z-dance_floor_stage_30s_4k60.mp4"
M.par.Wallspout.val = "Arena_Wall"
M.par.Floorspout.val = "Arena_Floor"
M.par.Testpattern.val = False
M.par.Includecolumns.val = False

for json_key, par_prefix, label_prefix in (("WALL", "Wall", "Proj1 Wall"), ("FLOOR", "Floor", "Proj2 Floor")):
    c = META["cameras"][json_key]
    pp = M.appendCustomPage(f"Projector {json_key}")
    pp.appendXYZ(f"{par_prefix}t", label=f"{label_prefix} Translate (m)")
    pp.appendXYZ(f"{par_prefix}r", label=f"{label_prefix} Rotate (deg)")
    pp.appendFloat(f"{par_prefix}fov", label=f"{label_prefix} Horizontal FOV")
    pp.appendXY(f"{par_prefix}shift", label=f"{label_prefix} Lens Shift (window)")
    for i, ax in enumerate("xyz"):
        getattr(M.par, f"{par_prefix}t{ax}").default = c["t"][i]
        getattr(M.par, f"{par_prefix}t{ax}").val = c["t"][i]
        getattr(M.par, f"{par_prefix}r{ax}").default = c["r"][i]
        getattr(M.par, f"{par_prefix}r{ax}").val = c["r"][i]
    getattr(M.par, f"{par_prefix}fov").default = c["fov_h_deg"]
    getattr(M.par, f"{par_prefix}fov").val = c["fov_h_deg"]

pr = M.appendCustomPage("Output")
pr.appendInt("Projres", label="Projector Output Res", size=2)
M.par.Projres1.val, M.par.Projres1.default = 3840, 3840
M.par.Projres2.val, M.par.Projres2.default = 2160, 2160

pg_prev = M.appendCustomPage("Preview")
pg_prev.appendFloat("Orbit", label="Orbit Yaw (deg)")[0].normMin = -90
M.par.Orbit.normMax = 90
pg_prev.appendFloat("Tilt", label="Orbit Pitch (deg)")
M.par.Tilt.normMin, M.par.Tilt.normMax = 0, 65
pg_prev.appendFloat("Distance", label="Camera Distance (m)")
M.par.Distance.normMin, M.par.Distance.normMax = 8, 38
pg_prev.appendFloat("Wallalbedo", label="Wall Albedo")
pg_prev.appendFloat("Flooralbedo", label="Floor Albedo")
pg_prev.appendFloat("Ambient", label="Room Ambient")
pg_prev.appendToggle("Shadows", label="Enable 4K Shadows")
for n, v in (("Orbit", 0.0), ("Tilt", 6.5), ("Distance", 15.5), ("Wallalbedo", 0.85), ("Flooralbedo", 0.78), ("Ambient", 0.06), ("Shadows", 1)):
    getattr(M.par, n).default = v
    getattr(M.par, n).val = v

# ---------------- 2. Wall & Floor Content Input Chains ----------------
x0 = 0
# Wall input chain (Top row y = 520)
tmpl_w = mk(M, moviefileinTOP, "moviefilein_wall_template", x0, 640, file=os.path.join(ROOT, "wall_combined_uv_template.png"))
sel_w = mk(M, selectTOP, "select_wall_pops", x0, 520, top="=parent().par.Wallcontent.eval() or 'moviefilein_wall_template'")
vid_w = mk(M, moviefileinTOP, "moviefilein_wall_video", x0, 400, file="=parent().par.Wallvideo")
sp_w = mk(M, spoutinTOP, "spoutin_wall", x0, 280)
sw_w_src = mk(M, switchTOP, "switch_wall_source", x0 + 220, 500, index="=parent().par.Wallsource.menuIndex")
sw_w_src.inputConnectors[0].connect(tmpl_w)
sw_w_src.inputConnectors[1].connect(sel_w)
sw_w_src.inputConnectors[2].connect(vid_w)
sw_w_src.inputConnectors[3].connect(sp_w)

fit_w = mk(M, fitTOP, "fit_wall_canvas", x0 + 420, 500, outputresolution="custom", resolutionw=7680, resolutionh=1656, fit="fill")
fit_w.inputConnectors[0].connect(sw_w_src)
sw_w_test = mk(M, switchTOP, "switch_wall_test", x0 + 620, 500, index="=1 if parent().par.Testpattern.eval() else 0")
sw_w_test.inputConnectors[0].connect(fit_w)
sw_w_test.inputConnectors[1].connect(tmpl_w)
lvl_w = mk(M, levelTOP, "level_wall_blackout", x0 + 820, 500, opacity="=1.0 - parent().par.Blackout")
lvl_w.inputConnectors[0].connect(sw_w_test)
null_w_c = mk(M, nullTOP, "null_content_wall", x0 + 1020, 500)
null_w_c.inputConnectors[0].connect(lvl_w)
mat_w = mk(M, constantMAT, "constant_wall_mat", x0 + 1220, 500, colormap="null_content_wall")

# Floor input chain (Bottom row y = 40)
tmpl_f = mk(M, moviefileinTOP, "moviefilein_floor_template", x0, 120, file=os.path.join(ROOT, "floor_uv_template.png"))
sel_f = mk(M, selectTOP, "select_floor_pops", x0, 0, top="=parent().par.Floorcontent.eval() or 'moviefilein_floor_template'")
vid_f = mk(M, moviefileinTOP, "moviefilein_floor_video", x0, -120, file="=parent().par.Floorvideo")
sp_f = mk(M, spoutinTOP, "spoutin_floor", x0, -240)
sw_f_src = mk(M, switchTOP, "switch_floor_source", x0 + 220, 0, index="=parent().par.Floorsource.menuIndex")
sw_f_src.inputConnectors[0].connect(tmpl_f)
sw_f_src.inputConnectors[1].connect(sel_f)
sw_f_src.inputConnectors[2].connect(vid_f)
sw_f_src.inputConnectors[3].connect(sp_f)

fit_f = mk(M, fitTOP, "fit_floor_canvas", x0 + 420, 0, outputresolution="custom", resolutionw=3840, resolutionh=2400, fit="fill")
fit_f.inputConnectors[0].connect(sw_f_src)
sw_f_test = mk(M, switchTOP, "switch_floor_test", x0 + 620, 0, index="=1 if parent().par.Testpattern.eval() else 0")
sw_f_test.inputConnectors[0].connect(fit_f)
sw_f_test.inputConnectors[1].connect(tmpl_f)
lvl_f = mk(M, levelTOP, "level_floor_blackout", x0 + 820, 0, opacity="=1.0 - parent().par.Blackout")
lvl_f.inputConnectors[0].connect(sw_f_test)
null_f_c = mk(M, nullTOP, "null_content_floor", x0 + 1020, 0)
null_f_c.inputConnectors[0].connect(lvl_f)
mat_f = mk(M, constantMAT, "constant_floor_mat", x0 + 1220, 0, colormap="null_content_floor")

mat_blk = mk(M, constantMAT, "constant_occluder_black", x0 + 1220, 250, colorr=0, colorg=0, colorb=0)

mk_annotate(M, "annot_inputs", "1. WALL & FLOOR CONTENT INPUTS",
            "Left+Right V-Wall (7680x1656 unfolded) & Stage Floor (3840x2400)\nAll Null TOPs styled in #2F59AD",
            x0 - 60, -300, 1450, 1080, (0.14, 0.20, 0.28))

# ---------------- 3. 3D Stage Geometry (from SketchUp 腾势空间结构.skp) ----------------
def make_geo(parent, name, obj_file, mat_name, gx, gy):
    g = mk(parent, geometryCOMP, name, gx, gy, material=mat_name)
    for c in list(g.children):
        c.destroy()
    s = g.create(fileinSOP, "filein_mesh")
    setp(s, file=os.path.join(ROOT, obj_file))
    s.render = s.display = True
    return g

g_wall = make_geo(M, "geo_wall_combined", "wall_combined.obj", "constant_wall_mat", x0 + 1480, 500)
g_occ  = make_geo(M, "geo_occluder", "occluder.obj", "constant_occluder_black", x0 + 1480, 320)
g_cols = make_geo(M, "geo_columns_fg", "columns_fg.obj", "constant_occluder_black", x0 + 1480, 160)
g_floor = make_geo(M, "geo_floor_stage", "floor_stage.obj", "constant_floor_mat", x0 + 1480, 0)

# ---------------- 4. Dual Projector Cameras & Renders ----------------
# Projector #1: WALL_COMBINED (1 projector -> both V-walls)
cam_w = mk(M, cameraCOMP, "cam_proj_WALL", x0 + 1750, 500, rord="xyz", viewanglemethod="horzfov",
           fov="=parent().par.Wallfov", winx="=parent().par.Wallshiftx", winy="=parent().par.Wallshifty", near=0.5, far=60)
for ax in "xyz":
    setp(cam_w, **{f"t{ax}": f"=parent().par.Wallt{ax}", f"r{ax}": f"=parent().par.Wallr{ax}"})

rnd_w = mk(M, renderTOP, "render_proj_WALL", x0 + 2000, 500,
           camera="cam_proj_WALL",
           geometry="='geo_wall_combined geo_occluder' + (' geo_columns_fg' if parent().par.Includecolumns else '')",
           outputresolution="custom", resolutionw="=parent().par.Projres1", resolutionh="=parent().par.Projres2",
           bgcolorr=0, bgcolorg=0, bgcolorb=0, bgcolora=1, antialias="aa4x")
out_w = mk(M, nullTOP, "null_out_WALL", x0 + 2240, 500)
out_w.inputConnectors[0].connect(rnd_w)

# Projector #2: FLOOR_STAGE (1 projector -> stage floor separately)
cam_f = mk(M, cameraCOMP, "cam_proj_FLOOR", x0 + 1750, 0, rord="xyz", viewanglemethod="horzfov",
           fov="=parent().par.Floorfov", winx="=parent().par.Floorshiftx", winy="=parent().par.Floorshifty", near=0.5, far=60)
for ax in "xyz":
    setp(cam_f, **{f"t{ax}": f"=parent().par.Floort{ax}", f"r{ax}": f"=parent().par.Floorr{ax}"})

rnd_f = mk(M, renderTOP, "render_proj_FLOOR", x0 + 2000, 0,
           camera="cam_proj_FLOOR",
           geometry="='geo_floor_stage geo_occluder' + (' geo_columns_fg' if parent().par.Includecolumns else '')",
           outputresolution="custom", resolutionw="=parent().par.Projres1", resolutionh="=parent().par.Projres2",
           bgcolorr=0, bgcolorg=0, bgcolorb=0, bgcolora=1, antialias="aa4x")
out_f = mk(M, nullTOP, "null_out_FLOOR", x0 + 2240, 0)
out_f.inputConnectors[0].connect(rnd_f)

# Dual Side-by-Side Output (Left = WALL_COMBINED, Right = FLOOR_STAGE)
lay_dual = mk(M, layoutTOP, "layout_dual_outputs", x0 + 2480, 250, outputresolution="custom",
              resolutionw="=parent().par.Projres1 * 2", resolutionh="=parent().par.Projres2", align="horizlr")
lay_dual.inputConnectors[0].connect(out_w)
lay_dual.inputConnectors[1].connect(out_f)
out_dual = mk(M, nullTOP, "null_output_dual", x0 + 2700, 250)
out_dual.inputConnectors[0].connect(lay_dual)

mk_annotate(M, "annot_projectors", "2. DUAL PROJECTOR RIG (WALL #1 + FLOOR #2)",
            "null_out_WALL = Projector #1 (Both V-Walls combined)\nnull_out_FLOOR = Projector #2 (Stage Floor separately)\nnull_output_dual = Side-by-side dual output",
            x0 + 1420, -140, 1460, 820, (0.16, 0.22, 0.18))

# ---------------- 5. Physical 3D Stage Light-Cone Simulation Sub-COMP ----------------
S = M.create(baseCOMP, "sim_preview")
S.nodeX, S.nodeY = x0 + 2000, -340
S.viewer = True

pw = mk(S, phongMAT, "phong_wall", 0, 320,
        diffr="=parent(2).par.Wallalbedo", diffg="=parent(2).par.Wallalbedo", diffb="=parent(2).par.Wallalbedo",
        ambr="=parent(2).par.Wallalbedo", ambg="=parent(2).par.Wallalbedo", ambb="=parent(2).par.Wallalbedo",
        specr=0, specg=0, specb=0)
pf = mk(S, phongMAT, "phong_floor", 0, 160,
        diffr="=parent(2).par.Flooralbedo", diffg="=parent(2).par.Flooralbedo", diffb="=parent(2).par.Flooralbedo",
        ambr="=parent(2).par.Flooralbedo", ambg="=parent(2).par.Flooralbedo", ambb="=parent(2).par.Flooralbedo",
        specr=0, specg=0, specb=0)
pb = mk(S, phongMAT, "phong_structure", 0, 0, diffr=0.22, diffg=0.23, diffb=0.26, ambr=0.22, ambg=0.23, ambb=0.26,
        specr=0, specg=0, specb=0)

make_geo(S, "geo_wall_combined", "wall_combined.obj", "phong_wall", 260, 320)
make_geo(S, "geo_floor_stage", "floor_stage.obj", "phong_floor", 260, 160)
make_geo(S, "geo_occluder", "occluder.obj", "phong_structure", 260, 0)
make_geo(S, "geo_columns_fg", "columns_fg.obj", "phong_structure", 260, -160)

for j, (json_key, par_prefix) in enumerate((("WALL", "Wall"), ("FLOOR", "Floor"))):
    lt = mk(S, lightCOMP, f"light_proj_{json_key}", 540, 300 - j * 200,
            lighttype="cone", coneangle=105, conedelta=0, attenuated=False,
            projmap=f"../null_out_{json_key}", projmapmode="simplehorzfov",
            projangle=f"=parent(2).par.{par_prefix}fov", projmapextendu="zero", projmapextendv="zero",
            shadowtype="=('hard2d' if parent(2).par.Shadows else 'off')",
            shadowcasters="='geo_occluder' + (' geo_columns_fg' if parent(2).par.Includecolumns else '')",
            shadowresolution1=4096, shadowresolution2=4096, dimmer=1.0, rord="xyz")
    for ax in "xyz":
        setp(lt, **{f"t{ax}": f"=parent(2).par.{par_prefix}t{ax}", f"r{ax}": f"=parent(2).par.{par_prefix}r{ax}"})

amb = mk(S, ambientlightCOMP, "ambient_room", 540, -100, dimmer="=parent(2).par.Ambient")
tgt = mk(S, nullCOMP, "null_look_target", 800, 120, tx=15.0, ty=2.1, tz=-12.5)
cam_sim = mk(S, cameraCOMP, "cam_orbit", 800, 300, lookat="null_look_target", viewanglemethod="horzfov", fov=68, near=0.3, far=120)
setp(cam_sim,
     tx="=15.0 + parent(2).par.Distance * math.sin(math.radians(parent(2).par.Orbit)) * math.cos(math.radians(parent(2).par.Tilt))",
     ty="=2.1 + parent(2).par.Distance * math.sin(math.radians(parent(2).par.Tilt))",
     tz="=-12.5 - parent(2).par.Distance * math.cos(math.radians(parent(2).par.Orbit)) * math.cos(math.radians(parent(2).par.Tilt))")

rnd_sim = mk(S, renderTOP, "render_sim", 1060, 220, camera="cam_orbit",
             geometry="='geo_wall_combined geo_floor_stage geo_occluder' + (' geo_columns_fg' if parent(2).par.Includecolumns else '')",
             lights="light_proj_* ambient_room", outputresolution="custom", resolutionw=3840, resolutionh=2160,
             bgcolorr=0.012, bgcolorg=0.014, bgcolorb=0.018, bgcolora=1, antialias="aa4x")
out_sim_s = mk(S, nullTOP, "null_sim_preview", 1280, 220)
out_sim_s.inputConnectors[0].connect(rnd_sim)

sel_sim = mk(M, selectTOP, "select_sim_preview", x0 + 2240, -340, top="sim_preview/null_sim_preview")
out_sim = mk(M, nullTOP, "null_sim_preview", x0 + 2480, -340)
out_sim.inputConnectors[0].connect(sel_sim)

txt = M.create(textDAT, "text_readme")
txt.nodeX, txt.nodeY = x0 + 1480, -340
txt.par.language = "plain"
txt.text = (
    "DENZA Z Scene 1 — Wall + Floor Dual-Projection 3D Mapping (11/14 Architecture)\n"
    "=============================================================================\n"
    "1. Projector #1 (WALL):  1 projector -> Both Left & Right V-Walls combined (wall_combined.obj, 27.784m x 6.0m)\n"
    "2. Projector #2 (FLOOR): 1 projector -> Stage Floor separately (floor_stage.obj, 18.0m x 11.25m)\n"
    "3. Occluders:            Central hanging canopy (occluder.obj, Z=5.01..8.66m) + 4 slanted columns (columns_fg.obj)\n"
    "4. Outputs:\n"
    "   - null_out_WALL:    Projector #1 output (default 3840x2160)\n"
    "   - null_out_FLOOR:   Projector #2 output (default 3840x2160)\n"
    "   - null_output_dual: Spanned side-by-side output (7680x2160)\n"
    "   - null_sim_preview: 3840x2160 16:9 3D Stage physical light-cone + shadow simulation\n"
)

report["comp"] = M.path
print(json.dumps(report, indent=2))
