import sys
sys.path.insert(0, r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\denza-project-handoff\quickstart\projection-simulation")
import ctypes as C
import numpy as np
from su_api import api, H, Pt, Tr, chk, get_list, su_str

INCH = 0.0254
src = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\腾势空间结构.skp"
api.SUInitialize()
model = H()
status = C.c_int()
chk(api.SUModelCreateFromFileWithStatus(C.byref(model), src.encode("utf-8"), C.byref(status)), "open")
ents = H()
api.SUModelGetEntities(model, C.byref(ents))

chunks, path_ids = [], []
paths = {}

def idx(d, k):
    return d.setdefault(k, len(d))

def mat(t):
    return np.array(t.v).reshape(4, 4).T

def hidden(el):
    b = C.c_bool()
    api.SUDrawingElementGetHidden(el, C.byref(b))
    return b.value

def face_tris(f):
    mh = H()
    if api.SUMeshHelperCreate(C.byref(mh), f) != 0:
        return None
    nv, nt, got = C.c_size_t(), C.c_size_t(), C.c_size_t()
    api.SUMeshHelperGetNumVertices(mh, C.byref(nv))
    api.SUMeshHelperGetNumTriangles(mh, C.byref(nt))
    pts = (Pt * nv.value)()
    api.SUMeshHelperGetVertices(mh, nv.value, pts, C.byref(got))
    ind = (C.c_size_t * (nt.value * 3))()
    api.SUMeshHelperGetVertexIndices(mh, nt.value * 3, ind, C.byref(got))
    api.SUMeshHelperRelease(C.byref(mh))
    P = np.frombuffer(pts, dtype=np.float64).reshape(-1, 3)
    I = np.frombuffer(ind, dtype=np.uint64).astype(np.int64).reshape(-1, 3)
    return P, I

def walk(entities, M, path):
    if "BYD" in path or "SimLab" in path:
        return
    for f in get_list(api.SUEntitiesGetNumFaces, api.SUEntitiesGetFaces, entities):
        r = face_tris(f)
        if r is None or not len(r[1]):
            continue
        P, I = r
        W = (np.c_[P, np.ones(len(P))] @ M.T)[:, :3] * INCH
        T = W[I]
        chunks.append(T)
        path_ids.append(np.full(len(T), idx(paths, path)))
    for g in get_list(api.SUEntitiesGetNumGroups, api.SUEntitiesGetGroups, entities):
        if hidden(g):
            continue
        t, sub = Tr(), H()
        api.SUGroupGetTransform(g, C.byref(t))
        api.SUGroupGetEntities(g, C.byref(sub))
        nm = su_str(api.SUGroupGetName, g) or "G"
        walk(sub, M @ mat(t), path + "/" + nm)
    for ci in get_list(api.SUEntitiesGetNumInstances, api.SUEntitiesGetInstances, entities):
        if hidden(ci):
            continue
        t, d, sub = Tr(), H(), H()
        api.SUComponentInstanceGetTransform(ci, C.byref(t))
        api.SUComponentInstanceGetDefinition(ci, C.byref(d))
        api.SUComponentDefinitionGetEntities(d, C.byref(sub))
        nm = su_str(api.SUComponentDefinitionGetName, d) or "C"
        walk(sub, M @ mat(t), path + "/" + nm)

walk(ents, np.eye(4), "")
api.SUModelRelease(C.byref(model))
api.SUTerminate()

T = np.concatenate(chunks)
P = np.concatenate(path_ids)
inv_paths = {v: k for k, v in paths.items()}

out_npz = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\_work\wall_floor_projection\geom_new_skp.npz"
np.savez_compressed(out_npz, tris=T, path=P, paths=np.array([inv_paths[i] for i in range(len(inv_paths))], dtype=object))

print(f"Total non-car triangles in 腾势空间结构.skp: {len(T)}")
for pid, pname in inv_paths.items():
    m = P == pid
    t = T[m]
    c = t.mean(1)
    keep = (c[:, 0] < 35) & (c[:, 1] < 46)
    t = t[keep]
    if len(t) == 0:
        continue
    v = t.reshape(-1, 3)
    bmin = v.min(0).round(2)
    bmax = v.max(0).round(2)
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    area = 0.5 * np.linalg.norm(n, axis=1)
    nz = np.abs(n[:, 2]) / (2 * area + 1e-12)
    horiz_area = area[nz > 0.9].sum()
    vert_area = area[nz <= 0.9].sum()
    print(f"[{pid:2d}] {pname:28s} | tris={len(t):5d} | min={bmin} max={bmax} | vert={vert_area:6.1f}m2 horiz={horiz_area:6.1f}m2")
