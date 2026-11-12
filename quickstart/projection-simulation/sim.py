"""Projector coverage simulation for the Denza V-wall.

Units: metres, Z up. Geometry from geom.npz (extract.py).
"""
import json
import numpy as np

ASPECT = 16 / 10
LUMENS = 46200.0
RES = {"WUXGA 1920x1200": (1920, 1200), "4K+ 5120x3200": (5120, 3200)}
AUD = np.array([15.0, 22.0, 1.7])  # audience reference eye point

d = np.load("geom.npz")
TRIS, PATH = d["tris"], d["path"]
NAMES = json.load(open("geom.json", encoding="utf-8"))["paths"]


def comp(*names):
    ids = [NAMES.index(n) for n in names]
    return np.isin(PATH, ids)


TARGET_MASK = comp("/组件#56/G", "/组件#56/G/G", "/组件#57", "/组件#56/G/组件#15")
OCC_FULL = comp("/组件#56/G", "/组件#56/G/G", "/组件#57", "/组件#56/G/组件#15",
         "/组件#46", "/组件#47", "/组件#56/G/组件#55", "/组件#56/G/组件#53")
OCC_FAST = comp("/组件#56/G", "/组件#56/G/G", "/组件#57", "/组件#46", "/组件#47")


def normals(T):
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    a = np.linalg.norm(n, axis=1)
    return n / (a[:, None] + 1e-12), 0.5 * a


def hits(P, S, O, eps=1e-3):
    """True where segment P->S is blocked by any triangle in O. P:(3,), S:(N,3)."""
    D = S - P
    v0, e1, e2 = O[:, 0], O[:, 1] - O[:, 0], O[:, 2] - O[:, 0]
    out = np.zeros(len(S), bool)
    for i in range(0, len(S), 256):
        Dc = D[i:i + 256][:, None, :]
        h = np.cross(Dc, e2[None])
        a = np.einsum("nmk,mk->nm", h, e1)
        ok = np.abs(a) > 1e-12
        f = np.where(ok, 1.0 / np.where(ok, a, 1), 0)
        s = (P - v0)[None]
        u = f * np.einsum("nmk,nmk->nm", np.broadcast_to(s, h.shape), h)
        q = np.cross(np.broadcast_to(s, h.shape), e1[None])
        v = f * np.einsum("nmk,nmk->nm", np.broadcast_to(Dc, q.shape), q)
        t = f * np.einsum("mk,nmk->nm", e2, q)
        blk = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > eps) & (t < 1 - eps)
        out[i:i + 256] = blk.any(1)
    return out


def samples(cell):
    """Sample points on target faces that the audience can see; returns pts, normals(toward aud), area."""
    T = TRIS[TARGET_MASK]
    n, A = normals(T)
    c = T.mean(1)
    keep = (A > 1e-4) & (np.abs(n[:, 2]) < 0.9)
    T, n, A, c = T[keep], n[keep], A[keep], c[keep]
    flip = np.einsum("ij,ij->i", AUD - c, n) < 0
    n[flip] *= -1
    pts, nrm, ar = [], [], []
    for tri, nn, a in zip(T, n, A):
        L = max(np.linalg.norm(tri[1] - tri[0]), np.linalg.norm(tri[2] - tri[1]), np.linalg.norm(tri[0] - tri[2]))
        k = max(1, int(np.ceil(L / cell)))
        uu, vv = np.meshgrid(np.arange(k) + 1 / 3, np.arange(k) + 1 / 3)
        m = uu + vv < k
        uu, vv = uu[m] / k, vv[m] / k
        p = tri[0] + uu[:, None] * (tri[1] - tri[0]) + vv[:, None] * (tri[2] - tri[0])
        pts.append(p)
        nrm.append(np.repeat(nn[None], len(p), 0))
        ar.append(np.full(len(p), a / len(p)))
    P, N, A = np.concatenate(pts), np.concatenate(nrm), np.concatenate(ar)
    P = P + N * 0.01
    vis = ~hits(AUD, P, TRIS[OCC_FAST]) & (np.einsum("ij,ij->i", AUD - P, N) > 0)
    return P[vis], N[vis], A[vis]


def frame(pos, target):
    f = target - pos
    f /= np.linalg.norm(f)
    r = np.cross(f, [0, 0, 1.0])
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return f, r, u


def fit(pos, pts):
    """Aim at bbox centre of pts in angular space; return (fwd,right,up,tr,half_w,half_h)."""
    f, r, u = frame(pos, pts.mean(0))
    for _ in range(3):
        v = pts - pos
        z = v @ f
        x, y = (v @ r) / z, (v @ u) / z
        cx, cy = (x.max() + x.min()) / 2, (y.max() + y.min()) / 2
        aim = f + cx * r + cy * u
        f, r, u = frame(pos, pos + aim)
    v = pts - pos
    z = v @ f
    x, y = (v @ r) / z, (v @ u) / z
    hw = max(np.abs(x).max(), np.abs(y).max() * ASPECT) * 1.02
    return f, r, u, 1 / (2 * hw), hw, hw / ASPECT


def evaluate(pos, pts, nrm, area, occ, max_inc=65):
    f, r, u, tr, hw, hh = fit(pos, pts)
    v = pts - pos
    dist = np.linalg.norm(v, axis=1)
    cosi = np.einsum("ij,ij->i", -v / dist[:, None], nrm)
    lit = (cosi > np.cos(np.radians(max_inc))) & ~hits(pos, pts, occ)
    return dict(f=f, r=r, u=u, tr=tr, hw=hw, hh=hh, dist=dist, cosi=cosi, lit=lit,
                cover=area[lit].sum() / area.sum())


def metrics(pos, ev, nrm, area, res):
    W, Hh = res
    zf = ev["dist"] * 0  # placeholder for clarity
    v_dist = ev["dist"]
    pix_ang = 2 * ev["hw"] / W  # radians per pixel (small-angle)
    pix_lin = v_dist * pix_ang / np.sqrt(np.clip(ev["cosi"], 0.05, 1))
    # illuminance: lumens spread evenly over image solid angle
    omega = (2 * ev["hw"]) * (2 * ev["hh"])
    E = LUMENS / omega * np.clip(ev["cosi"], 0, 1) / v_dist ** 2 * 0.9
    return pix_lin, E
