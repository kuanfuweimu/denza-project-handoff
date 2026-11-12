"""Flatten every visible face of a .skp into world-space triangles (metres)."""
import ctypes as C
import json
import sys
import numpy as np
from su_api import api, H, Pt, Tr, chk, get_list, su_str

INCH = 0.0254
src, out = sys.argv[1], sys.argv[2]
api.SUInitialize()
model = H()
status = C.c_int()
chk(api.SUModelCreateFromFileWithStatus(C.byref(model), src.encode("utf-8"), C.byref(status)), "open")
ents = H()
api.SUModelGetEntities(model, C.byref(ents))

chunks, tag_ids, path_ids = [], [], []
tags, paths = {}, {}
stats = {"faces": 0, "groups": 0, "instances": 0}


def idx(d, k):
    return d.setdefault(k, len(d))


def mat(t):
    return np.array(t.v).reshape(4, 4).T


def tag_name(el):
    lay = H()
    if api.SUDrawingElementGetLayer(el, C.byref(lay)) != 0 or not lay.value:
        return ""
    return su_str(api.SULayerGetName, lay)


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


def walk(entities, M, path, inh_tag):
    for f in get_list(api.SUEntitiesGetNumFaces, api.SUEntitiesGetFaces, entities):
        stats["faces"] += 1
        r = face_tris(f)
        if r is None or not len(r[1]):
            continue
        P, I = r
        W = (np.c_[P, np.ones(len(P))] @ M.T)[:, :3] * INCH
        T = W[I]
        t = tag_name(f) or inh_tag
        chunks.append(T)
        tag_ids.append(np.full(len(T), idx(tags, t)))
        path_ids.append(np.full(len(T), idx(paths, path)))
    for g in get_list(api.SUEntitiesGetNumGroups, api.SUEntitiesGetGroups, entities):
        stats["groups"] += 1
        if hidden(g):
            continue
        t, sub = Tr(), H()
        api.SUGroupGetTransform(g, C.byref(t))
        api.SUGroupGetEntities(g, C.byref(sub))
        nm = su_str(api.SUGroupGetName, g) or "G"
        walk(sub, M @ mat(t), path + "/" + nm, tag_name(g) or inh_tag)
    for ci in get_list(api.SUEntitiesGetNumInstances, api.SUEntitiesGetInstances, entities):
        stats["instances"] += 1
        if hidden(ci):
            continue
        t, d, sub = Tr(), H(), H()
        api.SUComponentInstanceGetTransform(ci, C.byref(t))
        api.SUComponentInstanceGetDefinition(ci, C.byref(d))
        api.SUComponentDefinitionGetEntities(d, C.byref(sub))
        nm = su_str(api.SUComponentDefinitionGetName, d) or "C"
        walk(sub, M @ mat(t), path + "/" + nm, tag_name(ci) or inh_tag)


walk(ents, np.eye(4), "", "")
T = np.concatenate(chunks)
np.savez_compressed(out, tris=T, tag=np.concatenate(tag_ids), path=np.concatenate(path_ids))
with open(out + ".json", "w", encoding="utf-8") as fh:
    json.dump({"tags": list(tags), "paths": list(paths), "stats": stats, "load_status": status.value}, fh, ensure_ascii=False, indent=1)
V = T.reshape(-1, 3)
print(stats, "triangles", len(T), "load_status", status.value)
print("bbox min", V.min(0).round(2), "max", V.max(0).round(2), "size", (V.max(0) - V.min(0)).round(2))
api.SUModelRelease(C.byref(model))
api.SUTerminate()
