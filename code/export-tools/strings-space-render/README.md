# STRINGS SPACE 渲染工作目录

本项目的脚本、依赖、缓存、参考图和预览统一保存在：

`D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\_work\strings-space-render`

最终视频写入 `DENZA N\strings-space\out`。本次不向 C 盘或 Codex 默认工作目录写入工作文件。已安装的软件可沿用其安装位置；当前 Python 使用 `D:\Python\python.exe`，FFmpeg 使用已有安装。

## 参考亮度版 v2

- 输出：`strings-space_showcase_30s_4k60_reference_v2.mp4`
- 规格：3840×2160、60 fps、1800 帧、30 秒；9 个场景，段间 12 帧叠化。
- 基准参数：曝光 3.00、白色上限 1.00、柔光 0.51、线宽 0.40、密度 10、总亮度 1.00。
- 线宽在 0.40–0.48 间缓慢变化；生长与林冠片段使用平滑追踪。
- 环境反射、高光、自发光及镜头为参考画面校准。各段还附加曝光补偿，使不同形态的银白高光处于接近的亮度范围；这些补偿不是截图中直接读出的数值。
- 全部实际参数记录在 `reference-settings.json`。参考截图在 `references/`；预览在 `previews/`；渲染报告与编码日志也在本目录。

## 执行

在此目录使用 PowerShell：

```powershell
$env:PYTHONPATH = Join-Path $PWD 'python-libs'
$env:PYTHONPYCACHEPREFIX = Join-Path $PWD 'cache'
$env:TEMP = Join-Path $PWD 'temp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null
& 'D:\Python\python.exe' .\reference_showcase.py --preview
```

去掉 `--preview` 输出视频。脚本拒绝覆盖现有同名成片；重渲染前请先改输出名称。`calibrate_brightness.py` 仅用于从未补偿预览建立第一轮校准，不应对已补偿预览重复运行。

渲染调用项目实际 GLSL 与 GPU 模拟，以固定输出帧间隔推进，使用独立 OpenGL 与 FFmpeg NVENC 编码，不接管浏览器或桌面界面。

## 迁移记录

原 `D:\Codex\workspace\2026-11-11\new-chat\work\strings-space-check` 已迁入本目录，1615 个文件迁移前后逐一核对 SHA-256。

原 `D:\Codex\workspace\2026-11-11\new-chat\outputs\strings-space` 已迁至同级 `strings-space-previous-delivery`，5 个文件迁移前后逐一核对 SHA-256。第一版项目成片仍保存在 `strings-space\out`。
