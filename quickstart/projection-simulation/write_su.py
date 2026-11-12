"""Write virtual projectors + coverage overlay into a COPY of the skp (headless SketchUp API)."""
import ctypes as C
import json
import sys
import numpy as np
from su_api import api, H, Pt, chk

INCH = 0.0254
src, dst = sys.argv[1], sys.argv[2]
plan = json.load(open("plan_result.json", encoding="utf-8"))
cov = np.load("coverage_cells.npz")  # quads (n,4,3) in metres, cls (n,) 0=none 1=L 2=R


class Color(C.Structure):
    _fields_ = [("r", C.c_ubyte), ("g", C.c_ubyte), ("b", C.c_ubyte), ("a", C.c_ubyte)]


def P3(p):
    return Pt(p[0] / INCH, p[1] / INCH, p[2] / INCH)


api.SUInitialize()
model = H()
st = C.c_int()
chk(api.SUModelCreateFromFileWithStatus(C.byref(model), src.encode("utf-8"), C.byref(st)), "open")
root = H()
api.SUModelGetEntities(model, C.byref(root))


def material(name, rgb, alpha=1.0):
    m = H()
    chk(api.SUMaterialCreate(C.byref(m)))
    api.SUMaterialSetName(m, name.encode("utf-8"))
    api.SUMaterialSetColor(m, C.byref(Color(*rgb, 255)))
    if alpha < 1:
        api.SUMaterialSetOpacity(m, C.c_double(alpha))
        api.SUMaterialSetUseOpacity(m, True)
    arr = (H * 1)(m)
    chk(api.SUModelAddMaterials(model, 1, arr))
    return m


def new_group(parent, name):
    g = H()
    chk(api.SUGroupCreate(C.byref(g)))
    chk(api.SUEntitiesAddGroup(parent, g))
    api.SUGroupSetName(g, name.encode("utf-8"))
    ents = H()
    api.SUGroupGetEntities(g, C.byref(ents))
    return ents


def add_faces(ents, polys, mat):
    gi = H()
    chk(api.SUGeometryInputCreate(C.byref(gi)))
    vi = 0
    for poly in polys:
        loop = H()
        api.SULoopInputCreate(C.byref(loop))
        for p in poly:
            api.SUGeometryInputAddVertex(gi, C.byref(P3(p)))
            api.SULoopInputAddVertexIndex(loop, vi)
            vi += 1
        fi = C.c_size_t()
        chk(api.SUGeometryInputAddFace(gi, C.byref(loop), C.byref(fi)), "addface")
    chk(api.SUEntitiesFill(ents, gi, True), "fill")
    api.SUGeometryInputRelease(C.byref(gi))


def paint_all_faces(ents, mat):
    from su_api import get_list
    for f in get_list(api.SUEntitiesGetNumFaces, api.SUEntitiesGetFaces, ents):
        api.SUFaceSetFrontMaterial(f, mat)
        api.SUFaceSetBackMaterial(f, mat)


def add_edges(ents, segs):
    arr = (H * len(segs))()
    for i, (a, b) in enumerate(segs):
        e = H()
        chk(api.SUEdgeCreate(C.byref(e), C.byref(P3(a)), C.byref(P3(b))))
        arr[i] = e
    chk(api.SUEntitiesAddEdges(ents, len(segs), arr))


top = new_group(root, "PROJECTION_SIM 投影模拟")
mats = {
    0: material("SIM_打不到", (210, 40, 50)),
    1: material("SIM_投影L覆盖", (64, 120, 210)),
    2: material("SIM_投影R覆盖", (214, 140, 60)),
}
body_mat = material("SIM_投影机机身", (30, 30, 30))
cone_mat = {"L": material("SIM_L光锥", (64, 120, 210), 0.12), "R": material("SIM_R光锥", (214, 140, 60), 0.12)}

# coverage overlay, one group per class so they can be toggled
for k, nm in ((0, "覆盖图_打不到"), (1, "覆盖图_L"), (2, "覆盖图_R")):
    q = cov["quads"][cov["cls"] == k]
    if not len(q):
        continue
    g = new_group(top, nm)
    add_faces(g, list(q), None)
    paint_all_faces(g, mats[k])

for key in ("L", "R"):
    pr = plan["projectors"][key]
    pos = np.array(pr["pos"])
    f, r, u = (np.array(pr[k]) for k in ("aim", "right", "up"))
    g = new_group(top, f"投影机_{key}  h={pos[2]:.1f}m  TR={pr['throw_ratio']}")
    # body 0.9 x 0.75 x 0.4 m, lens at pos
    bx = [pos - f * 0.9 + sx * r * 0.375 + sy * u * 0.2 for sx in (-1, 1) for sy in (-1, 1)]
    fr = [pos + sx * r * 0.375 + sy * u * 0.2 for sx in (-1, 1) for sy in (-1, 1)]
    o = [0, 1, 3, 2]
    quads = [[bx[i] for i in o], [fr[i] for i in o]] + [[bx[o[i]], bx[o[(i + 1) % 4]], fr[o[(i + 1) % 4]], fr[o[i]]] for i in range(4)]
    add_faces(g, quads, None)
    paint_all_faces(g, body_mat)
    # frustum to the far plane at mean distance * 1.15
    L = pr["mean_dist_m"] * 1.15
    corners = [pos + L * (f + sx * pr["hw"] * r + sy * pr["hh"] * u) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    cg = new_group(top, f"光锥_{key}")
    add_edges(cg, [(pos, c) for c in corners] + [(corners[i], corners[(i + 1) % 4]) for i in range(4)])
    add_faces(cg, [[pos, corners[i], corners[(i + 1) % 4]] for i in range(4)], None)
    paint_all_faces(cg, cone_mat[key])

chk(api.SUModelSaveToFile(model, dst.encode("utf-8")), "save")
api.SUModelRelease(C.byref(model))
api.SUTerminate()
print("saved", dst)
