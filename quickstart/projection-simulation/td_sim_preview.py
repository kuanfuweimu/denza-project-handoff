"""Physical projection preview: projector outputs re-projected as light onto a grey wall, with shadows.

Run inside TD after td_build_mapping.py. Rebuilds /project1/mapping_denza/sim_preview (own sub-COMP).
"""
import os

ROOT = r"D:/Codex/workspace/tengshi-projection/td_assets"
NULL_BLUE = (0.1843137255, 0.3490196078, 0.6784313725)
M = op("/project1/mapping_denza")
fails = []


def setp(op_, **kw):
    for k, v in kw.items():
        p = getattr(op_.par, k, None)
        if p is None:
            fails.append(f"{op_.path}.{k}")
            continue
        try:
            if isinstance(v, str) and v.startswith("="):
                p.expr = v[1:]
            else:
                p.val = v
        except Exception as e:
            fails.append(f"{op_.path}.{k}={v!r}: {e}")


def mk(parent, t, name, x, y, **kw):
    o = parent.create(t, name)
    o.nodeX, o.nodeY = x, y
    o.viewer = True
    setp(o, **kw)
    if o.type == "null":
        o.color = NULL_BLUE
    return o


# ---------- preview controls on the main COMP ----------
if not any(p.name == "Preview" for p in M.customPages):
    pg = M.appendCustomPage("Preview")
    pg.appendFloat("Orbit", label="Orbit (deg)")[0].normMin = -90
    M.par.Orbit.normMax = 90
    pg.appendFloat("Tilt", label="Tilt (deg)")
    M.par.Tilt.normMin, M.par.Tilt.normMax = -10, 60
    pg.appendFloat("Distance", label="Distance (m)")
    M.par.Distance.normMin, M.par.Distance.normMax = 5, 40
    pg.appendFloat("Wallalbedo", label="Wall Brightness (albedo)")
    pg.appendFloat("Ambient", label="Room Ambient")
    pg.appendToggle("Shadows", label="Shadows")
    for n, v in (("Orbit", 0), ("Tilt", 8), ("Distance", 20), ("Wallalbedo", 0.75), ("Ambient", 0.04), ("Shadows", 1)):
        getattr(M.par, n).default = v
        getattr(M.par, n).val = v

if M.op("sim_preview"):
    M.op("sim_preview").destroy()
S = M.create(baseCOMP, "sim_preview")
S.nodeX, S.nodeY = 1900, -160
S.viewer = True

# ---------- materials ----------
mat = mk(S, phongMAT, "phong_wall", 0, 300,
diffr="=parent(2).par.Wallalbedo", diffg="=parent(2).par.Wallalbedo", diffb="=parent(2).par.Wallalbedo",
ambr="=parent(2).par.Wallalbedo", ambg="=parent(2).par.Wallalbedo", ambb="=parent(2).par.Wallalbedo",
specr=0, specg=0, specb=0)
mat_box = mk(S, phongMAT, "phong_box", 0, 160, diffr=0.25, diffg=0.25, diffb=0.27, ambr=0.25, ambg=0.25, ambb=0.27,
specr=0, specg=0, specb=0)
mat_floor = mk(S, phongMAT, "phong_floor", 0, 20, diffr=0.12, diffg=0.12, diffb=0.12, ambr=0.12, ambg=0.12, ambb=0.12,
specr=0, specg=0, specb=0)

# ---------- geometry ----------
def geo(name, obj, material, y):
    g = mk(S, geometryCOMP, name, 250, y, material=material)
    for c in list(g.children):
        c.destroy()
    s = g.create(fileinSOP, "filein_mesh")
    setp(s, file=os.path.join(ROOT, obj))
    s.render = s.display = True
    return g

geo("geo_wall_L", "wall_L.obj", "phong_wall", 300)
geo("geo_wall_R", "wall_R.obj", "phong_wall", 160)
geo("geo_box", "occluder.obj", "phong_box", 20)
fl = mk(S, geometryCOMP, "geo_floor", 250, -120, material="phong_floor")
for c in list(fl.children):
    c.destroy()
gs = fl.create(gridSOP, "grid_floor")
setp(gs, sizex=40, sizey=40, rows=2, cols=2, orient="zx", tx=15, tz=-15)
gs.render = gs.display = True

# ---------- projector lights ----------
for j, key in enumerate(("L", "R")):
    lt = mk(S, lightCOMP, f"light_proj_{key}", 500, 300 - j * 160,
    lighttype="cone", coneangle=100, conedelta=0, attenuated=False,
    projmap=f"../null_out_{key}", projmapmode="simplehorzfov",
    projangle=f"=parent(2).par.{key}fov", projmapextendu="zero", projmapextendv="zero",
    shadowtype="=('hard2d' if parent(2).par.Shadows else 'off')", shadowcasters="geo_*",
            shadowresolution1=4096, shadowresolution2=4096, dimmer=1, rord="xyz")
    for ax in "xyz":
        setp(lt, **{f"t{ax}": f"=parent(2).par.{key}t{ax}", f"r{ax}": f"=parent(2).par.{key}r{ax}"})
amb = mk(S, ambientlightCOMP, "ambient_room", 500, -20, dimmer="=parent(2).par.Ambient")

# ---------- orbit camera (looks at the wall corner) ----------
tgt = mk(S, nullCOMP, "null_look_target", 750, 140, tx=15, ty=3.0, tz=-11.5)
cam = mk(S, cameraCOMP, "cam_orbit", 750, 300, lookat="null_look_target", viewanglemethod="horzfov", fov=65,
near=0.3, far=120)
setp(cam,
tx="=15 + parent(2).par.Distance * math.sin(math.radians(parent(2).par.Orbit)) * math.cos(math.radians(parent(2).par.Tilt))",
ty="=3.0 + parent(2).par.Distance * math.sin(math.radians(parent(2).par.Tilt))",
tz="=-11.5 - parent(2).par.Distance * math.cos(math.radians(parent(2).par.Orbit)) * math.cos(math.radians(parent(2).par.Tilt))")
# camera sits on the audience side (-Z in TD = +Y in SketchUp), so flip:
setp(cam, tz="=-11.5 - parent(2).par.Distance * math.cos(math.radians(parent(2).par.Orbit)) * math.cos(math.radians(parent(2).par.Tilt))")

rnd = mk(S, renderTOP, "render_sim", 1000, 220, camera="cam_orbit", geometry="geo_*",
lights="light_proj_* ambient_room", outputresolution="custom", resolutionw=3840, resolutionh=2160,
bgcolorr=0.01, bgcolorg=0.01, bgcolorb=0.012, bgcolora=1, antialias="aa4x")
out = mk(S, nullTOP, "null_sim_preview", 1200, 220)
out.inputConnectors[0].connect(rnd)

# expose at the main COMP level
if M.op("null_sim_preview"):
    M.op("null_sim_preview").destroy()
sel = mk(M, selectTOP, "select_sim_preview", 2100, -160, top="sim_preview/null_sim_preview")
outm = mk(M, nullTOP, "null_sim_preview", 2300, -160)
outm.inputConnectors[0].connect(sel)
print("fails", fails)
