"""Build the Denza V-wall 3D projection-mapping network inside TouchDesigner.

Run inside TD (Textport or TDMCP execute):
    exec(open(r'D:/Codex/workspace/tengshi-projection/td_build_mapping.py', encoding='utf-8').read())

Creates /project1/mapping_denza (an existing COMP of that name is renamed, never deleted).
Per-projector outputs are 3840x2400 (PT-RQ45K Quad Pixel Drive native grid, 16:10).
Audience preview is 3840x2160 (16:9).
"""
import json
import os

ROOT = r"D:/Codex/workspace/tengshi-projection/td_assets"
META = json.load(open(os.path.join(ROOT, "projectors.json"), encoding="utf-8"))
NULL_BLUE = (0.1843137255, 0.3490196078, 0.6784313725)
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
    if o.type == "null":
        o.color = NULL_BLUE
    report["created"].append(o.path)
    return o


parent_comp = op("/project1") or root
old = parent_comp.op("mapping_denza")
if old is not None:
    i = 1
    while parent_comp.op(f"mapping_denza_old{i}") is not None:
        i += 1
    old.name = f"mapping_denza_old{i}"

M = parent_comp.create(baseCOMP, "mapping_denza")
M.nodeX, M.nodeY = 0, -400

# ---------------- custom parameters (calibration surface) ----------------
pg = M.appendCustomPage("Mapping")
pg.appendTOP("Content", label="Content TOP")
pg.appendToggle("Testpattern", label="Show UV Template")
pg.appendFloat("Blackout", label="Blackout")[0].normMax = 1
for key in ("L", "R"):
    c = META["cameras"][key]
    pp = M.appendCustomPage(f"Projector {key}")
    t = pp.appendXYZ(f"{key}t", label=f"{key} Translate (m)")
    r = pp.appendXYZ(f"{key}r", label=f"{key} Rotate (deg)")
    f = pp.appendFloat(f"{key}fov", label=f"{key} Horizontal FOV")
    s = pp.appendXY(f"{key}shift", label=f"{key} Lens Shift (window)")
    for i, ax in enumerate("xyz"):
        getattr(M.par, f"{key}t{ax}").default = c["t"][i]
        getattr(M.par, f"{key}t{ax}").val = c["t"][i]
        getattr(M.par, f"{key}r{ax}").default = c["r"][i]
        getattr(M.par, f"{key}r{ax}").val = c["r"][i]
    getattr(M.par, f"{key}fov").default = c["fov_h_deg"]
    getattr(M.par, f"{key}fov").val = c["fov_h_deg"]
pr = M.appendCustomPage("Output")
res = pr.appendInt("Projres", label="Projector Resolution", size=2)
M.par.Projres1.val, M.par.Projres1.default = 3840, 3840
M.par.Projres2.val, M.par.Projres2.default = 2400, 2400
M.par.Testpattern.val = True

# ---------------- content ----------------
x0 = 0
tmpl = mk(M, moviefileinTOP, "moviefilein_uv_template", x0, 400, file=os.path.join(ROOT, "uv_template.png"))
cin = mk(M, selectTOP, "select_content", x0, 250)
cin.par.top.expr = "parent().par.Content.eval() or 'moviefilein_uv_template'"
sw = mk(M, switchTOP, "switch_content", x0 + 200, 320, index="=int(parent().par.Testpattern)")
sw.inputConnectors[0].connect(cin)
sw.inputConnectors[1].connect(tmpl)
lvl = mk(M, levelTOP, "level_blackout", x0 + 400, 320, opacity="=1 - parent().par.Blackout")
lvl.inputConnectors[0].connect(sw)
nc = mk(M, nullTOP, "null_content", x0 + 600, 320)
nc.inputConnectors[0].connect(lvl)

mat = mk(M, constantMAT, "constant_content", x0 + 800, 320, colormap="null_content")
blk = mk(M, constantMAT, "constant_black", x0 + 800, 180)
setp(blk, colorr=0, colorg=0, colorb=0)

# ---------------- geometry ----------------
def geo(name, obj, material, y):
    g = mk(M, geometryCOMP, name, x0 + 1000, y, material=material)
    for c in list(g.children):
        c.destroy()
    s = g.create(fileinSOP, "filein_mesh")
    setp(s, file=os.path.join(ROOT, obj))
    s.render = s.display = True
    return g

gL = geo("geo_wall_L", "wall_L.obj", "constant_content", 420)
gR = geo("geo_wall_R", "wall_R.obj", "constant_content", 280)
gO = geo("geo_occluder", "occluder.obj", "constant_black", 140)

# ---------------- projector cameras + renders ----------------
for j, key in enumerate(("L", "R")):
    y = 420 - j * 280
    cam = mk(M, cameraCOMP, f"cam_proj_{key}", x0 + 1250, y)
    for ax in "xyz":
        setp(cam, **{f"t{ax}": f"=parent().par.{key}t{ax}", f"r{ax}": f"=parent().par.{key}r{ax}"})
    setp(cam, rord="xyz", viewanglemethod="horzfov", fov=f"=parent().par.{key}fov",
                winx=f"=parent().par.{key}shiftx", winy=f"=parent().par.{key}shifty", near=0.5, far=60)
    rnd = mk(M, renderTOP, f"render_proj_{key}", x0 + 1500, y,
             camera=cam.name, geometry=f"geo_wall_{key} geo_occluder", outputresolution="custom",
             resolutionw="=parent().par.Projres1", resolutionh="=parent().par.Projres2",
             bgcolorr=0, bgcolorg=0, bgcolorb=0, bgcolora=1)
    out = mk(M, nullTOP, f"null_out_{key}", x0 + 1700, y)
    out.inputConnectors[0].connect(rnd)

# both projectors side by side, for one spanned output window (7680x2400)
lay = mk(M, layoutTOP, "layout_outputs", x0 + 1900, 280, outputresolution="custom",
                resolutionw="=parent().par.Projres1 * 2", resolutionh="=parent().par.Projres2", align="horizlr")
lay.inputConnectors[0].connect(M.op("null_out_L"))  # left half of spanned output = projector L
lay.inputConnectors[1].connect(M.op("null_out_R"))
mk(M, nullTOP, "null_output", x0 + 2100, 280).inputConnectors[0].connect(lay)

# ---------------- audience preview (16:9, 3840x2160) ----------------
camA = mk(M, cameraCOMP, "cam_audience", x0 + 1250, -160, tx=15.0, ty=1.7, tz=-26.0, rx=6.0, ry=180.0,
                 viewanglemethod="horzfov", fov=70, near=0.3, far=80)
camA.par.lookat = ""
prev = mk(M, renderTOP, "render_audience_preview", x0 + 1500, -160, camera="cam_audience",
          geometry="geo_wall_L geo_wall_R geo_occluder", outputresolution="custom", resolutionw=3840, resolutionh=2160,
          bgcolorr=0.02, bgcolorg=0.02, bgcolorb=0.02, bgcolora=1)
mk(M, nullTOP, "null_preview", x0 + 1700, -160).inputConnectors[0].connect(prev)

# ---------------- notes ----------------
txt = M.create(textDAT, "text_readme")
txt.nodeX, txt.nodeY = x0, -160
txt.text = (
    "Denza V-wall 3D mapping\n"
    "- Content canvas: 7680x1656 = unfolded wall 27.78m x 6m (see uv_template.png)\n"
    "- Set Mapping > Content to your content TOP, turn off Show UV Template\n"
    "- Projector L sits stage-right and shoots the LEFT wall; R is mirrored (cross projection)\n"
    "- On site: measure real projector positions, enter on Projector pages, then nudge rotate/FOV/lens shift\n"
    "  until the template grid lines land on the wall seams and column edges\n"
    "- Top ~1m of the wall is blocked by the hanging box in this layout; keep key content out of it\n"
    "- null_out_L / null_out_R = 3840x2400 per projector; null_output = 7680x2400 spanned\n"
)
exec(open(r"D:/Codex/workspace/tengshi-projection/td_add_inputs.py", encoding="utf-8").read())
M.par.Testpattern = False
exec(open(r"D:/Codex/workspace/tengshi-projection/td_sim_preview.py", encoding="utf-8").read())
report["comp"] = M.path
print(json.dumps(report, indent=1))
