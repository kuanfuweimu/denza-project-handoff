# 上传与验证状态

2026-11-14（Asia/Shanghai）：**全部上传完成**。Release `handoff-2026-11-12` 已追加 `denza-assets-13.zip` 并更新 `SHA256SUMS.txt`。

- **2026-11-14 新增项目标注**：**【场景一：墙面与地面 Projection（Scene 1 Wall & Floor Projection）】**。
- 13个ZIP附件共5,766,845,064字节（约5.77GB），另附SHA256SUMS.txt。
- 可恢复981个原路径文件（约6.89GB），其中新增 `denza-assets-13.zip`（412,973,402字节，SHA256 `f6f2dae5d853c7ea0b394ce4bc1ffcd8755bd133b3628ef4d8f53a5ad0c89ec7`）包含2026-11-14全部新增成果（11/13舞蹈分镜21页PDF与逐页拆解、SketchUp提取墙地双投3D网格与UV校准图、TouchDesigner 2025.32460实机生成并零报错验证的 `场景1_墙面与地面_Projection.toe` / `DENZA_Z_WallFloor_Mapping_POPs.toe` / `scene1.toe`、WebGL2 `strings-z-dance` 实时系统及3条4K60 30秒母带）。
- 13个远程附件的GitHub SHA256 digest和字节数均与本地manifest一致；证据见 `inventory/remote-verification.json`。

- 本地981个原路径文件与manifest SHA256全部匹配（`restore.py --scope projection --verify-only` 验证330个文件通过，`--scope all --verify-only` 验证981个文件通过）。
- 随包新增可直接在GitHub浏览的工程目录：
  - `quickstart/场景1_墙面与地面_Projection/`（同内容同步于 `quickstart/projection-wall-floor-TD/`；含 `场景1_墙面与地面_Projection.toe`、`DENZA_Z_WallFloor_Mapping_POPs.toe`、`scene1.toe`、`td_build_*.py`、`td_assets_wall_floor/`、`td_live_previews/`）
  - `quickstart/dance-concept-1113/`（21页高清PNG、联系表、提取文本与墙地双投设计说明）
  - `code/strings-z-dance/`（WebGL2实时墙地双投系统与控制台源码）
  - `code/export-tools/wall_floor_projection/`（SketchUp几何提取与4K60离屏渲染脚本）

下一位agent先读 START_HERE.md；投影事项最高优先级。只需要设备沟通与【场景一：墙面与地面 Projection】工程时，先恢复projection范围（`denza-assets-01..03.zip` + `denza-assets-13.zip`）；其余工程和视频用all。
