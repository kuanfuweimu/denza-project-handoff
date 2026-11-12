"""Tiny numpy z-buffer rasterizer for quick orthographic views of geom.npz."""
import numpy as np
from PIL import Image


def raster(tris, colors, view, px=1600):
    """view: 3x3 rows = (right, up, toward-viewer). Returns RGB image + transform info."""
    R = np.asarray(view, float)
    P = tris @ R.T  # (n,3,3) -> screen x, y, depth
    lo = P[..., :2].reshape(-1, 2).min(0)
    hi = P[..., :2].reshape(-1, 2).max(0)
    s = (px - 40) / max(hi - lo)
    W = int((hi[0] - lo[0]) * s) + 40
    Hh = int((hi[1] - lo[1]) * s) + 40
    img = np.full((Hh, W, 3), 245, np.uint8)
    zb = np.full((Hh, W), -1e9)
    X = (P[..., 0] - lo[0]) * s + 20
    Y = Hh - ((P[..., 1] - lo[1]) * s + 20)
    Z = P[..., 2]
    for i in range(len(tris)):
        x, y, z = X[i], Y[i], Z[i]
        x0, x1 = int(max(x.min(), 0)), int(min(x.max() + 1, W))
        y0, y1 = int(max(y.min(), 0)), int(min(y.max() + 1, Hh))
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        d = (y[1] - y[2]) * (x[0] - x[2]) + (x[2] - x[1]) * (y[0] - y[2])
        if abs(d) < 1e-9:
            continue
        a = ((y[1] - y[2]) * (gx - x[2]) + (x[2] - x[1]) * (gy - y[2])) / d
        b = ((y[2] - y[0]) * (gx - x[2]) + (x[0] - x[2]) * (gy - y[2])) / d
        c = 1 - a - b
        m = (a >= -1e-6) & (b >= -1e-6) & (c >= -1e-6)
        zz = a * z[0] + b * z[1] + c * z[2]
        sub = zb[y0:y1, x0:x1]
        m &= zz > sub
        sub[m] = zz[m]
        img[y0:y1, x0:x1][m] = colors[i]
    return Image.fromarray(img), (lo, s, Hh)


def shade(tris, base, light=(0.3, -0.5, 0.8)):
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    L = np.asarray(light) / np.linalg.norm(light)
    k = 0.45 + 0.55 * np.abs(n @ L)
    return (np.asarray(base, float) * k[:, None]).clip(0, 255).astype(np.uint8)
