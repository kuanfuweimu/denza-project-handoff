# 工程与视频

## 本机原位置

- 当前工作：`D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N`
- 三场景归档：`D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA 2\2026-11_DENZA Z`
- 接管仓库：`D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\denza-project-handoff`

## WEB 与 SPACE

| 工程 | 独立仓库 | 已核对commit | 启动 |
|---|---|---|---|
| strings-web | https://github.com/kuanfuweimu/strings-web | acc360cb1ae772fe019c0ac9848c021b2087d978 | `node server.js`，8787 |
| strings-space | https://github.com/kuanfuweimu/strings-space | aaafc247462fe1c046a8daec45f2db9df0384e92 | `node server.js`，8788 |

代码快照在本仓库 `code/strings-web`、`code/strings-space`；原独立仓库继续维护。GitHub登录、MIDI设备授权、浏览器localStorage自定义预设不会随代码自动迁移；未导出的个人运行时参数不在本包。

SPACE有材质调节、约0.2秒参数平滑、生长线头跟踪开关、九段视觉和控制器。不是硬件光追，使用GPU纹理模拟、实例化线片、材质着色和地面镜像。WEB有TD WebRender接入说明；SPACE当前没有完成TD桥接，用户要求先别管TD。

浏览器运行需要Node、支持WebGL2/EXT_color_buffer_float的Chrome或Edge。`node server.js`不需要npm安装。localhost与127.0.0.1不要混用，同源BroadcastChannel连接画面与control.html。不要为验证而接管用户界面。

## 三条最终带音乐版

均为30秒、3840×2160、60fps、1800帧、H.264/AAC立体声48kHz。全片解码通过，每片抽取90帧均不同。原无声版及原九条短片都保留。

```text
D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\strings-web\out\strings-web_showcase_30s_4k60_music.mp4
D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\strings-space\out\strings-space_showcase_30s_4k60_reference_v2_music.mp4
D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\strings-space\out\strings-space_showcase_30s_4k60_subject_only_music.mp4
```

WEB合集从原九条10秒4K60的第3秒开始取段，0.2秒交叉过渡，总30秒。SPACE独立离屏重渲染，九段固定步长，保留参考曝光与柔光。纯主体版去掉地面、镜像、静态环境结构和可见灯点，仍用不可见光源照亮主体；**没有把实时SPACE界面中的环境删掉**。

配乐为原创程序合成的电子氛围草稿：72BPM、九小节、稀疏低频/共鸣音/空气质感，三种疏密；不是外部商业歌曲，也不是用户正式确认的最终配乐。音乐与视频分别保留，合并时复制视频流不二次压画质。技术验收和生成脚本见 `_work/showcase-music`；未声称做过人工听音或舞者排练验收。

## 离屏导出工具

原工作目录 `DENZA N/_work` 已归档；可浏览脚本快照在 `code/export-tools`：

- `strings-space-render/reference_showcase.py`：亮度参考完整版。
- `strings-space-render/clean_showcase.py`：纯主体版。
- `strings-space-render/render_check.py`、`scene.json`：实际项目GLSL与原生OpenGL离屏渲染。
- `strings-web-edit/edit_showcase.py`：九段剪辑。
- `showcase-music/score_and_mux.py`：合成音乐及合并；`validate.py`验收。

当前脚本有硬编码的原D盘路径；默认按原目录恢复可直接找到工程。若换根目录，用 `scripts/rebase_export_paths.py --base <新父目录>` 仅修改恢复副本中的导出工具路径。历史投影脚本仍需逐项检查工作目录、SketchUp SDK和字体位置。不要直接执行遗留 `export.ps1`，它可能使用Chrome自动化和C盘临时目录。

渲染环境：Python3.12、moderngl、glcontext、numpy、Pillow，FFmpeg/ffprobe；原机RTX4080 Laptop，使用h264_nvenc。新的电脑若无NVIDIA/NVENC必须替换编码器并重新验收，不可静默降分辨率/fps。离屏渲染不是浏览器实时帧率证明。

依赖安装（先将TEMP/TMP/PYTHONPYCACHEPREFIX设到项目 `_work` 下）示例：

```powershell
python -m pip install --target '<项目根>\_work\strings-space-render\python-libs' --cache-dir '<项目根>\_work\pip-cache' moderngl==5.13.0 glcontext==3.1.0 numpy==2.5.4 Pillow==13.0.0
# 原机实际安装版本，见 inventory/runtime-versions.json。
```

不要盲目用示例版本覆盖已有环境；优先按runtime-versions中的真实版本安装。工具默认拒绝覆盖已存在视频，重导出要改新文件名。

## TD遗留内容

`05_线条生长_POPS` 与 `DENZA N/strings-td` 已保留，包括失败/试验的代码、toe和预览。此前本地TD API曾失去响应，用户否定过实现；这些不标记为“交付合格”。原生POPs路线如重启，需要从当前运行网络检查再做，禁止SOP的新实现要求仍有效。
