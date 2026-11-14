"""Build the Denza Z Dance Concept (6 Chapters) Native POPs Visual Generator in TouchDesigner.
Strictly follows TouchDesigner 2025.32460 Native POPs (Point Operators) architecture:
  - 100% Native POPs (linePOP, gridPOP, circlePOP, copyPOP, transformPOP, noisePOP, mergePOP, switchPOP, nullPOP, inPOP)
  - ZERO SOPs used in the visual generator
  - ZERO custom GLSL TOPs required
  - Default 3840x2160 (16:9) output for both Wall (null_pops_wall) and Floor (null_pops_floor)
  - All Null operators (nullPOP, nullTOP, nullCHOP, nullCOMP) colored #2F59AD
  - All POPs Annotate boxes colored in SOP blue (0.15, 0.38, 0.72)

Run inside TouchDesigner 2025.30000+ (Textport or TDMCP execute_code):
    exec(open(r'D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/td_wall_floor_pops/td_build_z_dance_pops.py', encoding='utf-8').read())
"""
import json

NULL_BLUE = (0.1843137255, 0.3490196078, 0.6784313725)  # #2F59AD
SOP_BLUE_ANNOT = (0.15, 0.38, 0.72)
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


def mk_annotate(parent, name, title, text, x, y, w, h, color=SOP_BLUE_ANNOT):
    a = parent.create(annotateCOMP, name)
    a.nodeX, a.nodeY = x, y
    a.nodeWidth, a.nodeHeight = w, h
    setp(a, Titletext=title, Bodytext=text,
         Backcolorr=color[0], Backcolorg=color[1], Backcolorb=color[2], Backcoloralpha=0.34)
    report["created"].append(a.path)
    return a


parent_comp = op("/project1") or root
old = parent_comp.op("z_dance_pops")
if old is not None:
    i = 1
    while parent_comp.op(f"z_dance_pops_old{i}") is not None:
        i += 1
    old.name = f"z_dance_pops_old{i}"

P = parent_comp.create(baseCOMP, "z_dance_pops")
P.nodeX, P.nodeY = 0, 200
P.viewer = True
P.par.parentshortcut = "Zdancepops"

# ---------------- 1. Custom Parameters (6 Dance Concept Chapters + Controls) ----------------
pg = P.appendCustomPage("Z Dance POPs")
ch_menu = pg.appendMenu("Chapter", label="Dance Chapter (1-6)")[0]
ch_menu.menuNames = ["ch1", "ch2", "ch3", "ch4", "ch5", "ch6"]
ch_menu.menuLabels = [
    "Ch.1 单线握持 · 轴向旋转与圆环对接 (P12-P13)",
    "Ch.2 碳纤维致密编织 · 平行交错张力线阵 (P3, P14)",
    "Ch.3 腾势橙光影引入 · Push/Pull 穿插织网 (P10, P15)",
    "Ch.4 橙光故障线阵 · Orange Light & Glitch (P16)",
    "Ch.5 Z字交错几何构图 · 威亚网格墙空间 (P17-P18)",
    "Ch.6 轮胎滚动序列波 · 破雾光刃与终章爆发 (P19-P21)",
]
pg.appendFloat("Orange", label="DENZA Orange Mix")[0].normMax = 1.0
pg.appendFloat("Glitch", label="Glitch Amplitude")[0].normMax = 1.0
pg.appendFloat("Speed", label="Animation Speed")[0].normMax = 3.0
pg.appendFloat("Linewidth", label="Line Width")[0].normMax = 10.0
pg.appendInt("Res", label="Output Resolution (16:9)", size=2)

P.par.Orange.val, P.par.Orange.default = 0.65, 0.65
P.par.Glitch.val, P.par.Glitch.default = 0.15, 0.15
P.par.Speed.val, P.par.Speed.default = 1.0, 1.0
P.par.Linewidth.val, P.par.Linewidth.default = 3.0, 3.0
P.par.Res1.val, P.par.Res1.default = 3840, 3840
P.par.Res2.val, P.par.Res2.default = 2160, 2160

# Time driver CHOP (follows TDMCP best practice: lfoCHOP -> nullCHOP)
lfo_t = mk(P, lfoCHOP, "lfo_time", -320, 1200, wavetype="ramp", frequency="=0.05 * parent().par.Speed", amp=20.0)
null_t = mk(P, nullCHOP, "null_time", -140, 1200)
null_t.inputConnectors[0].connect(lfo_t)

# ---------------- 2. Native POPs Chains for WALL_COMBINED (Unfolded V-Wall, Ortho 16.0 x 9.0) ----------------
# Ch.1 Wall: Single axial tension line + harmonic wave ribbon (linePOP -> transformPOP -> noisePOP -> copyPOP)
w1_line = mk(P, linePOP, "line_w_ch1", 0, 1200, divs=240)
w1_xf = mk(P, transformPOP, "transform_w_ch1", 180, 1200, sx=16.0, tx=-8.0, ty=-1.2)
w1_xf.inputConnectors[0].connect(w1_line)
w1_noise = mk(P, noisePOP, "noise_w_ch1", 360, 1200,
              amp0=1.35, period=2.4, tx="=op('null_time')['chan1'] * 0.8")
w1_noise.inputConnectors[0].connect(w1_xf)
w1_copy = mk(P, copyPOP, "copy_w_ch1", 540, 1200, ncy=11, ry=1.5, ty=0.24)
w1_copy.inputConnectors[0].connect(w1_noise)
w1_null = mk(P, nullPOP, "null_w_ch1", 720, 1200)
w1_null.inputConnectors[0].connect(w1_copy)

# Ch.2 Wall: Carbon Fiber Weave & Parallel Stagger (gridPOP -> noisePOP -> transformPOP -> mergePOP)
w2_grid = mk(P, gridPOP, "grid_w_ch2", 0, 1000, rows=28, cols=160, sizex=16.0, sizey=8.6)
w2_noise = mk(P, noisePOP, "noise_w_ch2", 220, 1000,
              amp0=0.35, period=1.2, tx="=op('null_time')['chan1'] * 1.1")
w2_noise.inputConnectors[0].connect(w2_grid)
w2_xform = mk(P, transformPOP, "transform_w_ch2", 440, 1000, rz=14.0, sy=0.92)
w2_xform.inputConnectors[0].connect(w2_noise)
w2_mrg = mk(P, mergePOP, "merge_w_ch2", 620, 1000)
w2_mrg.inputConnectors[0].connect(w2_noise)
w2_mrg.inputConnectors[1].connect(w2_xform)
w2_null = mk(P, nullPOP, "null_w_ch2", 800, 1000)
w2_null.inputConnectors[0].connect(w2_mrg)

# Ch.3 Wall: DENZA Orange Surge Push/Pull Intersecting Strands (linePOP -> transformPOP -> copyPOP -> noisePOP)
w3_line = mk(P, linePOP, "line_w_ch3", 0, 800, divs=200)
w3_xf = mk(P, transformPOP, "transform_w_ch3", 180, 800, sx=16.0, tx=-8.0, ty=-3.6)
w3_xf.inputConnectors[0].connect(w3_line)
w3_copy = mk(P, copyPOP, "copy_w_ch3", 360, 800, ncy=26, ty=0.28, rz=0.6)
w3_copy.inputConnectors[0].connect(w3_xf)
w3_noise = mk(P, noisePOP, "noise_w_ch3", 540, 800,
              amp0=0.95, period=2.6, tx="=op('null_time')['chan1'] * 1.4")
w3_noise.inputConnectors[0].connect(w3_copy)
w3_null = mk(P, nullPOP, "null_w_ch3", 720, 800)
w3_null.inputConnectors[0].connect(w3_noise)

# Ch.4 Wall: Orange Light & Glitch Array (gridPOP -> noisePOP high-freq step)
w4_grid = mk(P, gridPOP, "grid_w_ch4", 0, 600, rows=38, cols=96, sizex=16.0, sizey=8.6)
w4_noise = mk(P, noisePOP, "noise_w_ch4", 220, 600,
              amp0="=0.45 + parent().par.Glitch * 1.15", period=0.25,
              tx="=op('null_time')['chan1'] * 2.5")
w4_noise.inputConnectors[0].connect(w4_grid)
w4_null = mk(P, nullPOP, "null_w_ch4", 720, 600)
w4_null.inputConnectors[0].connect(w4_noise)

# Ch.5 Wall: Ordered Intersecting Z-Shaped Configuration + Tether Wall Grid (gridPOP + Z-slash linePOPs)
w5_grid = mk(P, gridPOP, "grid_w_ch5_wall", 0, 400, rows=16, cols=48, sizex=16.0, sizey=8.6)
w5_zline = mk(P, linePOP, "line_w_ch5_z", 0, 280, divs=120)
w5_zxf = mk(P, transformPOP, "transform_w_ch5_z", 180, 280, sx=6.8, rz=48.0, tx=-6.2, ty=-2.6)
w5_zxf.inputConnectors[0].connect(w5_zline)
w5_zcopy = mk(P, copyPOP, "copy_w_ch5_z", 360, 280, ncy=3, tx=4.4)
w5_zcopy.inputConnectors[0].connect(w5_zxf)
w5_mrg = mk(P, mergePOP, "merge_w_ch5", 540, 350)
w5_mrg.inputConnectors[0].connect(w5_grid)
w5_mrg.inputConnectors[1].connect(w5_zcopy)
w5_null = mk(P, nullPOP, "null_w_ch5", 720, 350)
w5_null.inputConnectors[0].connect(w5_mrg)

# Ch.6 Wall: Tire Sequence Rolling Wave + Diagonal Cyber Beam (linePOP + copyPOP + noisePOP)
w6_bar = mk(P, linePOP, "line_w_ch6_tread", 0, 140, divs=48)
w6_bxf = mk(P, transformPOP, "transform_w_ch6_bar", 180, 140, rz=90.0, sx=5.2, tx=-7.6, ty=-2.6)
w6_bxf.inputConnectors[0].connect(w6_bar)
w6_copy = mk(P, copyPOP, "copy_w_ch6_tread", 360, 140, ncy=32, tx=0.49)
w6_copy.inputConnectors[0].connect(w6_bxf)
w6_wave = mk(P, noisePOP, "noise_w_ch6_wave", 540, 140,
             amp0=1.45, period=1.6, tx="=-op('null_time')['chan1'] * 1.8")
w6_wave.inputConnectors[0].connect(w6_copy)
w6_beam = mk(P, linePOP, "line_w_ch6_beam", 180, 20, divs=180)
w6_beam_xf = mk(P, transformPOP, "transform_w_ch6_beam", 360, 20, rz=26.5, sx=17.5, tx=-7.8, ty=-3.8)
w6_beam_xf.inputConnectors[0].connect(w6_beam)
w6_mrg = mk(P, mergePOP, "merge_w_ch6", 720, 100)
w6_mrg.inputConnectors[0].connect(w6_wave)
w6_mrg.inputConnectors[1].connect(w6_beam_xf)
w6_null = mk(P, nullPOP, "null_w_ch6", 900, 100)
w6_null.inputConnectors[0].connect(w6_mrg)

# Switch & Final Wall POP Null
sw_w_pop = mk(P, switchPOP, "switch_pop_wall", 1140, 680, index="=parent().par.Chapter.menuIndex")
for idx, n_op in enumerate((w1_null, w2_null, w3_null, w4_null, w5_null, w6_null)):
    sw_w_pop.inputConnectors[idx].connect(n_op)
null_pop_wall = mk(P, nullPOP, "null_pop_wall_geo", 1360, 680)
null_pop_wall.inputConnectors[0].connect(sw_w_pop)

mk_annotate(P, "annot_pops_wall", "WALL NATIVE POPs GENERATOR (Ch.1 - Ch.6, Zero SOPs)",
            "Projector #1 Combined V-Wall POPs chains (linePOP / gridPOP / copyPOP / noisePOP / transformPOP / mergePOP)\nAll Null POPs colored #2F59AD",
            -60, -40, 1600, 1380, SOP_BLUE_ANNOT)

# ---------------- 3. Native POPs Chains for FLOOR_STAGE (Stage Floor Separately) ----------------
# Ch.1 Floor: Dancer Ring + Rotating Axial Line (circlePOP + linePOP -> transformPOP -> mergePOP)
f1_ring = mk(P, circlePOP, "circle_f_ch1", 0, -240, divs=180, radx=3.2, rady=3.2)
f1_axis = mk(P, linePOP, "line_f_ch1_axis", 0, -360, divs=120)
f1_rot = mk(P, transformPOP, "transform_f_ch1_axis", 220, -360,
            tx=-3.4, sx=6.8, rz="=op('null_time')['chan1'] * 24.0")
f1_rot.inputConnectors[0].connect(f1_axis)
f1_mrg = mk(P, mergePOP, "merge_f_ch1", 440, -300)
f1_mrg.inputConnectors[0].connect(f1_ring)
f1_mrg.inputConnectors[1].connect(f1_rot)
f1_null = mk(P, nullPOP, "null_f_ch1", 660, -300)
f1_null.inputConnectors[0].connect(f1_mrg)

# Ch.2 Floor: Diamond Carbon Weave Floor Grid + Parallel Staggered Runway Lines
f2_grid = mk(P, gridPOP, "grid_f_ch2", 0, -500, rows=28, cols=28, sizex=8.5, sizey=8.5)
f2_xf = mk(P, transformPOP, "transform_f_ch2", 220, -500, rz=45.0)
f2_xf.inputConnectors[0].connect(f2_grid)
f2_null = mk(P, nullPOP, "null_f_ch2", 660, -500)
f2_null.inputConnectors[0].connect(f2_xf)

# Ch.3 Floor: Push/Pull Longitudinal Perspective Lines from V-Apex to Front Stage
f3_line = mk(P, linePOP, "line_f_ch3", 0, -680, divs=160)
f3_xf = mk(P, transformPOP, "transform_f_ch3", 180, -680, rz=90.0, sx=8.0, tx=-4.5, ty=-4.0)
f3_xf.inputConnectors[0].connect(f3_line)
f3_copy = mk(P, copyPOP, "copy_f_ch3", 360, -680, ncy=18, tx=0.52)
f3_copy.inputConnectors[0].connect(f3_xf)
f3_noise = mk(P, noisePOP, "noise_f_ch3", 540, -680,
              amp0=0.38, period=1.8, ty="=-op('null_time')['chan1'] * 1.4")
f3_noise.inputConnectors[0].connect(f3_copy)
f3_null = mk(P, nullPOP, "null_f_ch3", 720, -680)
f3_null.inputConnectors[0].connect(f3_noise)

# Ch.4 Floor: Orange Glitch Matrix on Stage Floor
f4_grid = mk(P, gridPOP, "grid_f_ch4", 0, -860, rows=32, cols=32, sizex=9.5, sizey=9.5)
f4_noise = mk(P, noisePOP, "noise_f_ch4", 220, -860,
              amp0="=0.25 + parent().par.Glitch * 0.75", period=0.25,
              tx="=op('null_time')['chan1'] * 2.2")
f4_noise.inputConnectors[0].connect(f4_grid)
f4_null = mk(P, nullPOP, "null_f_ch4", 660, -860)
f4_null.inputConnectors[0].connect(f4_noise)

# Ch.5 Floor: Giant Z-Formation Floor Tracks + Landing Grid
f5_grid = mk(P, gridPOP, "grid_f_ch5", 0, -1040, rows=16, cols=16, sizex=9.5, sizey=9.5)
f5_z = mk(P, linePOP, "line_f_ch5_z", 0, -1140, divs=150)
f5_zxf = mk(P, transformPOP, "transform_f_ch5_z", 220, -1140, rz=-38.0, sx=8.5, tx=-3.5, ty=2.5)
f5_zxf.inputConnectors[0].connect(f5_z)
f5_mrg = mk(P, mergePOP, "merge_f_ch5", 440, -1080)
f5_mrg.inputConnectors[0].connect(f5_grid)
f5_mrg.inputConnectors[1].connect(f5_zxf)
f5_null = mk(P, nullPOP, "null_f_ch5", 660, -1080)
f5_null.inputConnectors[0].connect(f5_mrg)

# Ch.6 Floor: Concentric Tire Rotation Rings + Diagonal Light Blade
f6_ring = mk(P, circlePOP, "circle_f_ch6", 0, -1300, divs=160, radx=1.8, rady=1.8)
f6_copy = mk(P, copyPOP, "copy_f_ch6", 220, -1300, ncy=5, sx=1.22, sy=1.22,
             rz="=op('null_time')['chan1'] * 30.0")
f6_copy.inputConnectors[0].connect(f6_ring)
f6_blade = mk(P, linePOP, "line_f_ch6_blade", 220, -1400, divs=160)
f6_bxf = mk(P, transformPOP, "transform_f_ch6_blade", 440, -1400, rz=35.0, sx=10.5, tx=-4.2, ty=-2.8)
f6_bxf.inputConnectors[0].connect(f6_blade)
f6_mrg = mk(P, mergePOP, "merge_f_ch6", 660, -1340)
f6_mrg.inputConnectors[0].connect(f6_copy)
f6_mrg.inputConnectors[1].connect(f6_bxf)
f6_null = mk(P, nullPOP, "null_f_ch6", 880, -1340)
f6_null.inputConnectors[0].connect(f6_mrg)

sw_f_pop = mk(P, switchPOP, "switch_pop_floor", 1140, -780, index="=parent().par.Chapter.menuIndex")
for idx, n_op in enumerate((f1_null, f2_null, f3_null, f4_null, f5_null, f6_null)):
    sw_f_pop.inputConnectors[idx].connect(n_op)
null_pop_floor = mk(P, nullPOP, "null_pop_floor_geo", 1360, -780)
null_pop_floor.inputConnectors[0].connect(sw_f_pop)

mk_annotate(P, "annot_pops_floor", "FLOOR NATIVE POPs GENERATOR (Ch.1 - Ch.6, Zero SOPs)",
            "Projector #2 Stage Floor POPs chains (circlePOP / gridPOP / linePOP / copyPOP / transformPOP / noisePOP)\nAll Null POPs colored #2F59AD",
            -60, -1480, 1600, 1340, SOP_BLUE_ANNOT)

# ---------------- 4. 3840x2160 (16:9) Render & Post-Process TOP Chains ----------------
cam_w = mk(P, cameraCOMP, "cam_ortho_wall", 1680, 780, projection="ortho", orthowidth=16.0, tz=10.0)
mat_w = mk(P, lineMAT, "linemat_wall", 1680, 640,
           widthnear="=parent().par.Linewidth", widthfar="=parent().par.Linewidth",
           linenearcolorr=1.0,
           linenearcolorg="=1.0 - parent().par.Orange * 0.52",
           linenearcolorb="=1.0 - parent().par.Orange * 0.88")
geo_w = mk(P, geometryCOMP, "geo_render_wall_pop", 1680, 500, material="linemat_wall")
for c in list(geo_w.children):
    c.destroy()
pin_w = mk(geo_w, inPOP, "in_pop_wall", 0, 0)
pin_w.render = pin_w.display = True
geo_w.inputConnectors[0].connect(null_pop_wall)

rnd_w = mk(P, renderTOP, "render_pops_wall", 1940, 680,
           camera="cam_ortho_wall", geometry="geo_render_wall_pop",
           outputresolution="custom", resolutionw="=parent().par.Res1", resolutionh="=parent().par.Res2",
           bgcolorr=0.015, bgcolorg=0.018, bgcolorb=0.024, bgcolora=1.0, antialias="aa4x")
null_top_w = mk(P, nullTOP, "null_pops_wall", 2180, 680)
null_top_w.inputConnectors[0].connect(rnd_w)

cam_f = mk(P, cameraCOMP, "cam_ortho_floor", 1680, -680, projection="ortho", orthowidth=11.0, tz=10.0)
mat_f = mk(P, lineMAT, "linemat_floor", 1680, -820,
           widthnear="=parent().par.Linewidth", widthfar="=parent().par.Linewidth",
           linenearcolorr="=0.85 + parent().par.Orange * 0.15",
           linenearcolorg="=0.92 - parent().par.Orange * 0.45",
           linenearcolorb="=1.0 - parent().par.Orange * 0.85")
geo_f = mk(P, geometryCOMP, "geo_render_floor_pop", 1680, -960, material="linemat_floor")
for c in list(geo_f.children):
    c.destroy()
pin_f = mk(geo_f, inPOP, "in_pop_floor", 0, 0)
pin_f.render = pin_f.display = True
geo_f.inputConnectors[0].connect(null_pop_floor)

rnd_f = mk(P, renderTOP, "render_pops_floor", 1940, -780,
           camera="cam_ortho_floor", geometry="geo_render_floor_pop",
           outputresolution="custom", resolutionw="=parent().par.Res1", resolutionh="=parent().par.Res2",
           bgcolorr=0.012, bgcolorg=0.014, bgcolorb=0.020, bgcolora=1.0, antialias="aa4x")
null_top_f = mk(P, nullTOP, "null_pops_floor", 2180, -780)
null_top_f.inputConnectors[0].connect(rnd_f)

report["comp"] = P.path
print(json.dumps(report, indent=2))
