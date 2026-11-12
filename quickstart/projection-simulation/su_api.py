"""Minimal ctypes binding to the SketchUp C API shipped with SketchUp 2025 (headless, no UI)."""
import ctypes as C
import os

SU_DIR = r"D:\SketchUp 2025\SketchUp"
os.add_dll_directory(SU_DIR)
api = C.CDLL(os.path.join(SU_DIR, "SketchUpAPI.dll"))
H = C.c_void_p


class Pt(C.Structure):
    _fields_ = [("x", C.c_double), ("y", C.c_double), ("z", C.c_double)]


class Tr(C.Structure):
    _fields_ = [("v", C.c_double * 16)]


def chk(r, what=""):
    if r != 0:
        raise RuntimeError(f"SU error {r} {what}")


def su_str(fn, ref):
    s = H()
    api.SUStringCreate(C.byref(s))
    try:
        if fn(ref, C.byref(s)) != 0:
            return ""
        n = C.c_size_t()
        api.SUStringGetUTF8Length(s, C.byref(n))
        buf = C.create_string_buffer(n.value + 1)
        api.SUStringGetUTF8(s, n.value + 1, buf, C.byref(n))
        return buf.value.decode("utf-8", "replace")
    finally:
        api.SUStringRelease(C.byref(s))


def get_list(count_fn, get_fn, parent):
    n = C.c_size_t()
    chk(count_fn(parent, C.byref(n)))
    if not n.value:
        return []
    arr = (H * n.value)()
    got = C.c_size_t()
    chk(get_fn(parent, n.value, arr, C.byref(got)))
    return [H(arr[i]) for i in range(got.value)]
