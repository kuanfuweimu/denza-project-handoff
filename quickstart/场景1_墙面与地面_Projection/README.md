# 【场景一：墙面与地面 Projection】 (Scene 1 · Wall & Floor Dual Projection + Native POPs)

- **项目名称**：`场景一：墙面与地面 Projection` (`Scene 1 Wall & Floor Projection`)
- **TouchDesigner 工程文件**：`场景1_墙面与地面_Projection.toe`（同步含 `DENZA_Z_WallFloor_Mapping_POPs.toe` 与 `scene1.toe`）

本目录包含针对 **2026-11-14 最新双投影架构（1 台投影机合投左右两面折墙 + 1 台投影机单独投射舞台地面）** 与 **2026-11-13《Z dance concept:break down》舞蹈分镜** 的 TouchDesigner 完整工程文件（`DENZA_Z_WallFloor_Mapping_POPs.toe` / `scene1.toe`）及自动化构建脚本。

> **实机验证状态（2026-11-14）**：已通过 TDMCP 在 **TouchDesigner 2025.32460** 实例内实时生成、校验并保存（`par_fail: []`，全网 `get_errors: 0`）。完整实机截图位于 `td_live_previews/`。

---

## 0. 直接打开 `.toe` 工程

- **标准归档工程**：`DENZA_Z_WallFloor_Mapping_POPs.toe`（以及用户保存副本 `scene1.toe`）
- **顶层 `/project1` 信号监控与两个核心交互模块**：
  - `/project1/z_dance_pops`：100% 原生 POPs 6 章节墙地双路视觉生成器（自定义参数面板 `Z Dance Controls` 支持 `Auto Cycle 6 Chapters`、`Chapter (0-5)`、`Dancer X / Z`、`Pull Tension`、`Orange Burst`、`Z Grid Formation`、`Pulse Speed`）
  - `/project1/mapping_wall_floor`：墙地双投 3D 对位与物理阴影模拟系统（自定义参数面板支持 `Wall Source`、`Floor Source`、`Force UV Calibration Templates`、`Include 4 Foreground Slanted Columns` 以及 `Projector #1 Wall` / `Projector #2 Floor` 机位坐标与 FOV 实时微调）
  - 顶层蓝色（`#2F59AD`）监控输出：`null_MON_POPS_WALL`、`null_MON_POPS_FLOOR`、`null_MON_PROJ1_WALL_OUT`、`null_MON_PROJ2_FLOOR_OUT`、`null_MON_DUAL_OUTPUT`、`null_MON_3D_STAGE_SIM`

---

## 1. 脚本清单与功能

1. **`td_build_z_dance_pops.py`（构建 `/project1/z_dance_pops` 原生 POPs 视觉生成器）**
   - **100% 原生 POPs 架构（零 SOPs、零自定义 GLSL TOP）**：使用 `linePOP`、`gridPOP`、`circlePOP`、`copyPOP`、`transformPOP`、`noisePOP`、`mergePOP`、`switchPOP`、`nullPOP` 构建 6 大舞蹈章节的「双墙合投 (`null_pop_wall_geo`)」与「地面独投 (`null_pop_floor_geo`)」几何流。
   - **双通道 `3840×2160` (16:9) 渲染输出**：
     - `/project1/z_dance_pops/null_pops_wall`：送往投影机 #1（左右双墙合投画面）
     - `/project1/z_dance_pops/null_pops_floor`：送往投影机 #2（舞台地面独投画面）
   - **规范样式**：所有 `Null` 算子（`nullPOP` / `nullTOP`）统一设为 `#2F59AD`；POPs 区域 `Annotate` 框统一使用 SOP 蓝色 `(0.15, 0.38, 0.72)`。

2. **`td_build_wall_floor_mapping.py`（构建 `/project1/mapping_wall_floor` 墙地双投 3D 对位与光路模拟系统）**
   - 自动加载 `D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/td_assets_wall_floor/` 下的 SketchUp 精确导出模型：
     - `wall_combined.obj`（左右两面折墙合并展开 UV，`27.784m × 6.0m`）
     - `floor_stage.obj`（V 墙前方菱形舞台地面，`18.0m × 11.25m`）
     - `occluder.obj`（中央悬吊方盒遮挡体，`Z = 5.01..8.66m`）
     - `columns_fg.obj`（前景 4 根斜柱，`Z = 0..4.80m`，可通过 `Include_columns` 开关切换）
   - **双投影机独立相机与输出**：
     - `null_out_WALL`：投影机 #1（一机投双墙）变形校正输出
     - `null_out_FLOOR`：投影机 #2（一机投地面）变形校正输出
     - `null_output_dual`：双机左右拼接输出 (`7680×2160` / `7680×2400`)
     - `null_sim_preview`：`3840×2160` (16:9) 物理投影光锥 + 4096 阴影贴图 3D 舞台实时预览

---

## 2. 在 TouchDesigner 中一键运行方法

打开 TouchDesigner（推荐 **2025.30000+** 以支持原生 POPs），按 `Alt + T` 打开 Textport，依次执行：

```python
exec(open(r"D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/td_wall_floor_pops/td_build_z_dance_pops.py", encoding="utf-8").read())
exec(open(r"D:/Kuanfuweimu/2-Commission/VJ Commission/DENZA N/td_wall_floor_pops/td_build_wall_floor_mapping.py", encoding="utf-8").read())
```

---

## 3. 现场对位校准流程

1. 选中 `/project1/mapping_wall_floor`，在参数面板保持 `Force UV Templates = On`。
2. 将 `null_out_WALL` 送往墙面投影机，`null_out_FLOOR` 送往地面投影机。
3. 在 `Projector WALL` 与 `Projector FLOOR` 参数页填入现场实测的投影机坐标 `(tx, ty, tz)`，微调 `Rotate`、`Horizontal FOV` 与 `Lens Shift`，使：
   - 墙面青色中缝线严格落于 V 墙 `15.0m` 中央折角；
   - 地面橙色 V 界线严格贴合左右折墙底边，中心十字落于 `[15.0, 13.6, 0.0]` 舞者圆心。
4. 关闭 `Force UV Templates`，将 `Wall Source` 与 `Floor Source` 切换为 `POPs Generator`、`Video File`（加载 `strings-z-dance/out/` 下的 4K60 母带）或 `Spout In`。
