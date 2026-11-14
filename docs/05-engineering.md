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

## TD 2026-11-14 墙地双投实机工程与遗留内容

### 1. 2026-11-14 【场景一：墙面与地面 Projection】实机验证工程 (`quickstart/场景1_墙面与地面_Projection`)

- 本机路径：`D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\td_wall_floor_pops`（同步归档于 `DENZA 2\2026-11_DENZA Z\01_场景1_墙面双投影\墙地双投方案_1114` 与仓库 `quickstart/projection-wall-floor-TD`）
- 工程文件：`场景1_墙面与地面_Projection.toe`、`DENZA_Z_WallFloor_Mapping_POPs.toe` 与 `scene1.toe`（已在 **TouchDesigner 2025.32460** 中通过 TDMCP 实机生成并零报错验证，`get_errors: 0`）
- 两个核心交互模块：
  1. `/project1/z_dance_pops`：100% 原生 POPs 视觉生成器（零 SOP、零 GLSL TOP，所有 Null 算子 `#2F59AD`，POPs Annotate 框 SOP 蓝），含 `Z Dance Controls` 交互面板（6 大章节切换/自动循环、舞者 X/Z 坐标、拉扯张力、腾势橙爆发、Z 字网格、脉冲速度），双路输出 `3840×2160` (`null_pops_wall` / `null_pops_floor`)。
  2. `/project1/mapping_wall_floor`：墙地双投 3D 对位与物理光锥阴影模拟系统，加载 `td_assets_wall_floor` 下的 `wall_combined.obj`、`floor_stage.obj`、`occluder.obj`、`columns_fg.obj` 及对位网格贴图，支持信号源切换（POPs 实时生成 / 4K60 母带视频 / Spout）、UV 校准网格一键开关、前景斜柱遮挡开关及双投影机 3D 坐标/FOV 实时微调。
- 配套 WebGL2 实时墙地双投系统：`code/strings-z-dance`（端口 `8789`），已离屏渲染 3 条 `3840×2160 @ 60fps` 30 秒母带（`z-dance_wall_combined_30s_4k60.mp4`、`z-dance_floor_stage_30s_4k60.mp4`、`z-dance_stage3d_split_30s_4k60.mp4`）。

### 2. 早期 TD 遗留内容

`05_线条生长_POPS` 与 `DENZA N/strings-td` 已保留，包括早期试验代码、toe和预览。
