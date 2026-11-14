"""One-shot builder for DENZA Z Scene 1 inside TouchDesigner:
1. Enables Perform on Minimize so TDMCP WebServer DAT never freezes when TD is minimized
2. Disables TDMCP Followactive / Animatenodes so agent work never hijacks viewport
3. Builds /project1/z_dance_pops (100% Native POPs 6-Chapter Dance Concept Generator)
4. Builds /project1/mapping_wall_floor (1-Wall + 1-Floor 3D Mapping & Physical Light-Cone Simulation)
5. Connects z_dance_pops outputs (null_pops_wall / null_pops_floor) directly into mapping_wall_floor
6. Creates top-level /project1 monitor Null TOPs (#2F59AD) so all key outputs are immediately visible in /project1
"""
import os

HERE = r"D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/td_wall_floor_pops"
NULL_BLUE = (0.1843137255, 0.3490196078, 0.6784313725)  # #2F59AD

# 1. Ensure TD keeps cooking when minimized so MCP stays responsive
try:
    if hasattr(root.par, "performonminimize"):
        root.par.performonminimize = True
except Exception:
    pass

# 2. Respect user rule: disable TDMCP viewport follow / camera hijack
try:
    for mcp_op in root.findChildren(name="TDMCP"):
        for pname in ("Followactive", "Animatenodes"):
            if hasattr(mcp_op.par, pname):
                getattr(mcp_op.par, pname).val = False
except Exception:
    pass

# 3. Build Deliverable #1 in TD: /project1/z_dance_pops (Native POPs Generator)
exec(open(os.path.join(HERE, "td_build_z_dance_pops.py"), encoding="utf-8").read())

# 4. Build Deliverable #2 in TD: /project1/mapping_wall_floor (Wall+Floor 3D Mapping & Sim)
exec(open(os.path.join(HERE, "td_build_wall_floor_mapping.py"), encoding="utf-8").read())

# 5. Link POPs generator live into the 3D Wall+Floor mapping COMP
P = op("/project1/z_dance_pops")
M = op("/project1/mapping_wall_floor")
if P is not None:
    P.par.Chapter.menuIndex = 4  # Default to Ch.5 Z-Matrix & Tether Wall Grid
if M is not None:
    M.par.Wallsource = "pops"
    M.par.Floorsource = "pops"
    M.par.Testpattern = False

# 6. Top-level /project1 monitor Null TOPs (#2F59AD)
proj = op("/project1")
if proj is not None:
    monitors = [
        ("sel_pops_wall",   "null_MON_POPS_WALL",   "z_dance_pops/null_pops_wall",         320,  320),
        ("sel_pops_floor",  "null_MON_POPS_FLOOR",  "z_dance_pops/null_pops_floor",        320,  140),
        ("sel_proj1_wall",  "null_OUT_PROJ1_WALL",  "mapping_wall_floor/null_out_WALL",    320, -180),
        ("sel_proj2_floor", "null_OUT_PROJ2_FLOOR", "mapping_wall_floor/null_out_FLOOR",   320, -360),
        ("sel_dual_out",    "null_OUT_DUAL_7680",   "mapping_wall_floor/null_output_dual", 320, -540),
        ("sel_sim_3d",      "null_SIM_STAGE_3D",    "mapping_wall_floor/null_sim_preview", 320, -720),
    ]
    for sel_name, null_name, target_top, x, y in monitors:
        for old_n in (sel_name, null_name):
            if proj.op(old_n):
                proj.op(old_n).destroy()
        s = proj.create(selectTOP, sel_name)
        s.nodeX, s.nodeY = x, y
        s.par.top = target_top
        s.viewer = True
        n = proj.create(nullTOP, null_name)
        n.nodeX, n.nodeY = x + 220, y
        n.color = NULL_BLUE
        n.viewer = True
        n.inputConnectors[0].connect(s)

    if proj.op("annot_denza_overview"):
        proj.op("annot_denza_overview").destroy()
    ann = proj.create(annotateCOMP, "annot_denza_overview")
    ann.nodeX, ann.nodeY = -80, -820
    ann.nodeWidth, ann.nodeHeight = 820, 1320
    ann.par.Titletext = "场景一：墙面与地面 Projection (DENZA Z · Scene 1 Wall & Floor Dual Projection + Native POPs)"
    ann.par.Bodytext = (
        "项目名称：场景一 · 墙面与地面 Projection (Scene 1 Wall & Floor Projection)\n"
        "1. /project1/z_dance_pops : 6章节 100% 原生 POPs 墙地双路视觉生成器 (Zero SOPs)\n"
        "2. /project1/mapping_wall_floor : 投影机#1 (左右双墙合一幅画面) + 投影机#2 (舞台地面独投) + 3D物理光路遮挡模拟"
    )
    ann.par.Backcolorr, ann.par.Backcolorg, ann.par.Backcolorb, ann.par.Backcoloralpha = 0.15, 0.38, 0.72, 0.28

print("[DENZA Z] Successfully built /project1/z_dance_pops, /project1/mapping_wall_floor, and top-level monitors!")
