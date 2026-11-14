import sys
sys.path.insert(0, r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\_work\strings-space-render\python-libs")
import os
import re
import math
import subprocess
import numpy as np
import moderngl as m
from PIL import Image, ImageDraw, ImageFont

PROJECT_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\strings-z-dance"
SHOTS_DIR = os.path.join(PROJECT_DIR, "shots")
OUT_DIR = os.path.join(PROJECT_DIR, "out")
ARCHIVE_DIR = r"D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA 2\2026-11_DENZA Z\01_场景1_墙面双投影\墙地双投方案_1114"
FFMPEG_BIN = "ffmpeg"

os.makedirs(SHOTS_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Extract shaders from index.html so offscreen GPU render is 100% identical to live WebGL2
html_text = open(os.path.join(PROJECT_DIR, "index.html"), encoding="utf-8").read()
vs_quad = re.search(r"const VS_QUAD = `(#version 300 es[\s\S]*?)`;", html_text).group(1)
fs_canvas = re.search(r"const FS_CANVAS = `(#version 300 es[\s\S]*?)`;", html_text).group(1)
fs_present = re.search(r"const FS_PRESENT = `(#version 300 es[\s\S]*?)`;", html_text).group(1)

def to_gl330(src):
    s = src.replace("#version 300 es", "#version 330")
    return re.sub(r"precision\s+(?:highp|mediump|lowp)\s+\w+\s*;", "", s)

ctx = m.create_standalone_context(require=330)
print("GPU:", ctx.info["GL_RENDERER"], flush=True)

prog_canvas = ctx.program(vertex_shader=to_gl330(vs_quad), fragment_shader=to_gl330(fs_canvas))
prog_present = ctx.program(vertex_shader=to_gl330(vs_quad), fragment_shader=to_gl330(fs_present))
vao_canvas = ctx.vertex_array(prog_canvas, [])
vao_present = ctx.vertex_array(prog_present, [])

SCENES = [
    {"id": 0, "title": "Ch.1 单线握持 · 轴向旋转与圆环对接 (P12–P13)", "orange": 0.05, "glitch": 0.0,  "density": 0.35, "speed": 0.85, "weave": 0.15},
    {"id": 1, "title": "Ch.2 碳纤维致密编织 · 平行交错张力线阵 (P3, P14)", "orange": 0.12, "glitch": 0.0,  "density": 0.72, "speed": 1.00, "weave": 0.85},
    {"id": 2, "title": "Ch.3 腾势橙光影引入 · Push/Pull 穿插织网 (P10, P15)", "orange": 0.88, "glitch": 0.08, "density": 0.78, "speed": 1.15, "weave": 0.55},
    {"id": 3, "title": "Ch.4 橙光故障线阵 · Orange Light & Glitch (P16)", "orange": 0.95, "glitch": 0.85, "density": 0.90, "speed": 1.45, "weave": 0.65},
    {"id": 4, "title": "Ch.5 Z字交错几何构图 · 威亚网格墙空间 (P17–P18)", "orange": 0.68, "glitch": 0.15, "density": 0.82, "speed": 1.00, "weave": 0.90},
    {"id": 5, "title": "Ch.6 轮胎滚动序列波 · 破雾光刃与终章爆发 (P19–P21)", "orange": 0.75, "glitch": 0.22, "density": 0.95, "speed": 1.35, "weave": 0.75},
]

def make_target(w, h):
    tex = ctx.texture((w, h), 4, dtype="f1")
    tex.filter = (m.LINEAR, m.LINEAR)
    fbo = ctx.framebuffer([tex])
    return tex, fbo

def render_pass(sc, t_sec, w, h, fbo_w, tex_w, fbo_f, tex_f, fbo_out, view_mode, yaw=0.0, pitch=0.30, dist=15.5):
    for tgt_id, fbo in [(0, fbo_w), (1, fbo_f)]:
        fbo.use()
        ctx.viewport = (0, 0, w, h)
        prog_canvas["uRes"].value = (float(w), float(h))
        prog_canvas["uTime"].value = float(t_sec)
        prog_canvas["uTarget"].value = int(tgt_id)
        prog_canvas["uScene"].value = int(sc["id"])
        prog_canvas["uOrange"].value = float(sc["orange"])
        prog_canvas["uGlitch"].value = float(sc["glitch"])
        prog_canvas["uDensity"].value = float(sc["density"])
        prog_canvas["uWeave"].value = float(sc["weave"])
        prog_canvas["uExposure"].value = 1.2
        prog_canvas["uCalGrid"].value = 0.0
        prog_canvas["uOccMask"].value = 1.0
        vao_canvas.render(m.TRIANGLES, vertices=3)

    fbo_out.use()
    ctx.viewport = (0, 0, w, h)
    tex_w.use(0)
    tex_f.use(1)
    prog_present["uTexWall"].value = 0
    prog_present["uTexFloor"].value = 1
    prog_present["uRes"].value = (float(w), float(h))
    prog_present["uViewMode"].value = int(view_mode)
    prog_present["uBlackout"].value = 0.0
    prog_present["uCamOrbit"].value = (float(yaw), float(pitch), float(dist))
    vao_present.render(m.TRIANGLES, vertices=3)

# 1. Render 6 Chapter Stills (1920x1080) + Contact Sheet
tex_w_hd, fbo_w_hd = make_target(1920, 1080)
tex_f_hd, fbo_f_hd = make_target(1920, 1080)
tex_out_hd, fbo_out_hd = make_target(1920, 1080)

font_md = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 26)
font_sm = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
stills = []

for sc in SCENES:
    ch_num = sc["id"] + 1
    t_sample = 2.4 + ch_num * 0.7
    yaw_sample = math.sin(ch_num * 0.9) * 0.22
    render_pass(sc, t_sample, 1920, 1080, fbo_w_hd, tex_w_hd, fbo_f_hd, tex_f_hd, fbo_out_hd, view_mode=0, yaw=yaw_sample)
    raw = tex_out_hd.read()
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(1080, 1920, 4)[::-1, :, :3]
    im = Image.fromarray(arr)
    dr = ImageDraw.Draw(im)
    dr.rectangle([16, 16, 860, 62], fill=(10, 12, 18))
    dr.text((28, 22), sc["title"], fill=(255, 255, 255), font=font_md)
    dr.text((28, 500), "▲ 投影机 #1：左右双墙合投画面 (WALL_COMBINED)", fill=(255, 130, 50), font=font_sm)
    dr.text((28, 1040), "▲ 投影机 #2：舞台地面独投画面 (FLOOR_STAGE)", fill=(40, 220, 255), font=font_sm)
    dr.text((910, 1040), "▲ SketchUp 3D 现场双投影模拟（双墙合投 + 地面独投 + 吊顶结构）", fill=(255, 210, 90), font=font_sm)
    s_path = os.path.join(SHOTS_DIR, f"ch{ch_num}_split.jpg")
    im.save(s_path, quality=90)
    stills.append(s_path)
    print("Saved still:", s_path, flush=True)

cs_w, cs_h = 960, 540
sheet = Image.new("RGB", (cs_w * 2, cs_h * 3), (12, 14, 18))
for idx, p in enumerate(stills):
    im_s = Image.open(p).resize((cs_w, cs_h), Image.Resampling.LANCZOS)
    sheet.paste(im_s, ((idx % 2) * cs_w, (idx // 2) * cs_h))
cs_path = os.path.join(SHOTS_DIR, "z_dance_contact_sheet.jpg")
sheet.save(cs_path, quality=90)
sheet.save(os.path.join(ARCHIVE_DIR, "z_dance_contact_sheet.jpg"), quality=90)
print("Saved contact sheet:", cs_path, flush=True)

# 2. Render 3 x 30-second 4K60 (3840x2160 @ 60fps) Showcase Videos Simultaneous Stream!
# Since Pass 1 renders Wall (3840x2160), Pass 2 renders Floor (3840x2160), and Pass 3 renders Split+3D Stage (3840x2160),
# we can pipe all 3 streams in a SINGLE GPU pass per frame so 1800 frames take only ~25 seconds!
W4K, H4K = 3840, 2160
FPS = 60
DURATION = 30
TOTAL_FRAMES = FPS * DURATION

tex_w_4k, fbo_w_4k = make_target(W4K, H4K)
tex_f_4k, fbo_f_4k = make_target(W4K, H4K)
tex_s_4k, fbo_s_4k = make_target(W4K, H4K)

mp4_wall = os.path.join(OUT_DIR, "z-dance_wall_combined_30s_4k60.mp4")
mp4_floor = os.path.join(OUT_DIR, "z-dance_floor_stage_30s_4k60.mp4")
mp4_split = os.path.join(OUT_DIR, "z-dance_stage3d_split_30s_4k60.mp4")

def open_ffmpeg(out_path):
    cmd = [
        FFMPEG_BIN, "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-pix_fmt", "rgba",
        "-s", f"{W4K}x{H4K}",
        "-r", str(FPS),
        "-i", "-",
        "-vf", "vflip",
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-b:v", "28M",
        "-pix_fmt", "yuv420p",
        out_path
    ]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print("Starting 4K60 x 3 simultaneous NVENC streams (1800 frames = 30s)...", flush=True)
p_wall = open_ffmpeg(mp4_wall)
p_floor = open_ffmpeg(mp4_floor)
p_split = open_ffmpeg(mp4_split)

sim_time = 0.0
for frame in range(TOTAL_FRAMES):
    t_sec = frame / float(FPS)
    sc_idx = min(5, int(t_sec // 5.0))
    sc = SCENES[sc_idx]
    sim_time += (1.0 / FPS) * sc["speed"]
    yaw = math.sin(t_sec * 0.45) * 0.28
    pitch = 0.28 + 0.05 * math.cos(t_sec * 0.35)

    render_pass(sc, sim_time, W4K, H4K, fbo_w_4k, tex_w_4k, fbo_f_4k, tex_f_4k, fbo_s_4k, view_mode=0, yaw=yaw, pitch=pitch, dist=15.5)

    p_wall.stdin.write(tex_w_4k.read())
    p_floor.stdin.write(tex_f_4k.read())
    p_split.stdin.write(tex_s_4k.read())

    if (frame + 1) % 300 == 0:
        print(f"  Rendered {frame + 1}/{TOTAL_FRAMES} frames ({(frame+1)//FPS}s / {DURATION}s)...", flush=True)

for p in (p_wall, p_floor, p_split):
    p.stdin.close()
    p.wait()

print("Finished 4K60 renders:", mp4_wall, mp4_floor, mp4_split, flush=True)
