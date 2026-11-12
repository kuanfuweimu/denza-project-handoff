# 2026-11-12 工作状态 / Project status

## 最新进度摘要 / Latest progress summary

本次按用户要求更新当前进度记录；不新增渲染、不调整投影方案、不上传新的模型或成片。以下新增成果目前保存在公司电脑，原有交接资料仍以仓库和既有 Release 为准。

This update records current progress as requested. It does not create renders, revise projection plans or upload new models or finished videos. The new outputs listed below remain on the company workstation; existing handoff materials remain available through this repository and its existing Release.

| 项目 / Item | 当前进展 / Current progress | 待完成 / Remaining work |
| --- | --- | --- |
| 资料接管 / Material restoration | 12 个归档、787 个文件已恢复并校验；WEB、SPACE 既有测试各 7 项通过。 / Restored and verified 12 archives and 787 files; existing WEB and SPACE tests each passed 7 cases. | 浏览器/GPU、TD 实机及现场验证尚未完成。 / Browser/GPU, TouchDesigner runtime and on-site validation remain outstanding. |
| 场景 1 / Scene 1 | 历史方案 C 的 SKP 副本已添加俯视、空间机位、墙面覆盖视图，保存后重新打开验证成功。 / Added top, spatial and wall-coverage views to a copy of historical plan C; save/reopen validation succeeded. | 复核现场机位、镜头与遮挡；未重新计算光路。 / Confirm on-site positions, lenses and occlusion; optics have not been recalculated. |
| 场景 2 / Scene 2 | 从原 SKP 提取 24 层幕布；高 5 m，整体范围约 12.055 × 6.932 m；已输出俯视图及依据 JSON。 / Extracted 24 screens from the original SKP, 5 m high with overall bounds of about 12.055 × 6.932 m; generated a top view and provenance JSON. | 尺寸来自模型；现场投射面、幕料、机位及设备仍待确认，不能据此定镜头。 / Dimensions are model-derived; confirm physical target surfaces, screen material, positions and equipment before selecting lenses. |
| 场景 3 / Scene 3 | 已归档既有 LED 资料。 / Existing LED documents are archived. | 本次启用屏幕、像素画布、播放及同步规格尚未确认。 / Active screens, pixel canvas, playback and synchronization specifications remain unconfirmed. |

下一步优先取得设备型号、可用机位/吊点和现场尺寸，复核场景 1，再确定场景 2 的实际投距与镜头。SPACE → TD 仍暂停。下方保留各阶段证据与限制；模型提取和文件重开验证不代表现场验收。

Next, obtain equipment models, available projector/rigging positions and site measurements; review scene 1 before determining scene 2 throw distances and lenses. SPACE → TD remains paused. Evidence and limitations for each stage are retained below; model extraction and file reopen checks do not constitute on-site acceptance.

## 当前优先级

P0：让下一台电脑读到完整资料；投影设备方要安装距离/映射面积来计算镜头比。

P1：核实场景1模型版本与现场、补齐场景2投射面尺寸/高度和机位；确认设备清单后出可核对的安装方案。

P2：核对场景3本次启用LED屏、像素画布、输出与同步；继续内容制作/展示。

## 已完成和验收边界

- 三场景资料与客户文件归集；TD mapping引用资产可移植、解包一致，未现场测试。
- 共享Figma整理与静态快照，图片按比例；归档网页上下滚动。
- WEB/SPACE分别独立仓库；SPACE代码无未提交修改（创建交接包时）。
- 九个视觉合集、SPACE完整版与纯主体版、三条音乐版本均已保留；视频技术验证见归档报告。
- 新增交接文档、供应商待发稿、文件清单、去重附件与恢复工具。GitHub上传/恢复校验结果见根目录 `DELIVERY_STATUS.md`。

## 未完成/不能声称完成

- 尚无最终现场投影机位/镜头确认，旧模拟覆盖仍有约13.9%阴影。
- 场景二没有足够几何/安装信息，不能给确定镜头比。
- 场景三参数来自旧图，本次具体启用配置未确认。
- 纯主体视频已完成，但实时SPACE的“只显示主体”开关未新增。
- SPACE到TD实时接入尚未做，用户此前暂停了这方向。
- TD POPs试验没有新的满意验收结果。
- 接管包未包含个人全部聊天历史、账户密钥或全局AI配置。包含与本项目有关的决策、约束、文件和待办。

## 已放弃/被替代的方向

- 独立Vercel演示托管+denza子域名：被“现有主站隐藏路径”替代，不再问DNS。
- 网页翻页演示：改成上下滚动。
- 把素材当三份文件：应按三个空间场景，不是只有三个文件。
- C盘/D:\Codex新建渲染临时工作：用户要求统一在DENZA N，后续遵守。
- 只给localhost视频链接：用户明确要本地完整路径。
- 把SPACE说成真正光追：不准确，使用实时近似。
- 自动套用visual-taste/图像生成技能：用户明确要求移除，不恢复。

## 资料范围

纳入当前November三场景完整归档及DENZA N工程、备份、渲染工具、参考、成片。按内容SHA256去重传输但恢复全部原路径。`DENZA 2`根目录大量八九月份旧VJ文件只留元数据索引，未混入本次工程；若用户随后明确指定某个旧文件，按索引单独补充，不假定它是本次LED工程。

## 公司电脑接管：2026-11-12 / Company workstation handoff: 2026-11-12

作者：Codex。已克隆私有仓库，基准 commit 为 `9db41a4e0e428d482ecb0c28c5f351bb0bd35457`，本地 `main` 跟踪 `origin/main`。仓库位于 `E:/Codex/workspace/projects/denza-project-handoff`；全部资料恢复至 `E:/Codex/workspace/projects/denza`，保留 `DENZA N` 和 `DENZA 2/2026-11_DENZA Z` 的原目录关系。当前公司电脑的 E 盘规则优先于原电脑的 D 盘路径。

Author: Codex. Cloned the private repository at baseline commit `9db41a4e0e428d482ecb0c28c5f351bb0bd35457`, with local `main` tracking `origin/main`. The repository is at `E:/Codex/workspace/projects/denza-project-handoff`; all materials were restored under `E:/Codex/workspace/projects/denza`, preserving the original relationship between `DENZA N` and `DENZA 2/2026-11_DENZA Z`. Current workstation instructions selecting drive E take precedence over source-machine drive D paths.

Release `handoff-2026-11-12` 的12个附件（5,353,871,662字节）均通过 SHA256；原 `scripts/restore.py --scope all` 已恢复并校验全部787文件（5,964,436,403字节）。验证日志：`E:/Codex/workspace/2026-11-12/n-x20/outputs/denza-restore.log`。下载通过当前已授权 GitHub 凭据完成，未保存密钥。网络整包下载停滞后改用1 MiB分段并校验整包，未清理中断下载的残片。

All 12 Release assets (5,353,871,662 bytes) from `handoff-2026-11-12` passed SHA256 verification. The original `scripts/restore.py --scope all` restored and verified all 787 files (5,964,436,403 bytes). Log: `E:/Codex/workspace/2026-11-12/n-x20/outputs/denza-restore.log`. Downloads used existing authorized GitHub credentials without saving secrets. After whole-file transfers stalled, 1 MiB range requests completed the download, followed by whole-archive verification. Interrupted-download fragments were retained.

本机 Node v24.22.2、Python 3.12.14。仓库 WEB 快照的 `node --test tests/td-live.test.js` 7项通过；SPACE 快照的 `node --test tests/material-tracking.test.js` 7项通过。无 npm 依赖需要安装。恢复阶段没有操作屏幕、启动渲染、发送供应商消息或修改远程仓库；接管说明当时仅保存在本地，本次纳入进度更新。

Local runtimes are Node v24.22.2 and Python 3.12.14. The WEB snapshot passed all 7 tests in `node --test tests/td-live.test.js`; the SPACE snapshot passed all 7 tests in `node --test tests/material-tracking.test.js`. No npm dependency installation was required. During restoration, no screen interaction, rendering, vendor messaging or remote repository mutation was performed. Handoff notes were local at that stage and are included in this progress update.

未验证：浏览器/GPU实时画面、TD实机、现场校准、两个SKP的几何差异；未安装离屏渲染依赖或重定位遗留导出脚本。恢复文件保持原始校验值，后续运行导出前需按 `docs/05-engineering.md` 处理本机路径和依赖。P1仍为墙面机位/镜头、吊顶投射面与高度、设备清单；LED本次启用配置仍待确认。

Not verified: browser/GPU live visuals, TouchDesigner runtime, on-site calibration or geometry differences between the two SKP versions. Offline-render dependencies were not installed and legacy export scripts were not rebased. Restored files retain their original checksums; before exporting, follow `docs/05-engineering.md` to adapt local paths and dependencies. P1 remains wall projector positions/lenses, ceiling target geometry/heights and equipment inventory; the active LED configuration also remains unconfirmed.

### 场景2幕布俯视图 / Scene 2 curtain top view

2026-11-12：用户明确本次要的是“场景2，有幕布的那个”，不再按墙面双投影图回复。通过本机 SketchUp C API 从恢复的原始腾势空间结构.skp 提取组件 #80：三组共24层竖直幕布，高5m；中间8层宽7m、纵深1.512m；左右各8层（4层宽5.04m、4层宽3.36m），每组纵深1.35m。两侧组前后错开，整体宽12.054916m、纵深6.932407m。按真实坐标输出正投影PNG/SVG及来源JSON至 E:/Codex/workspace/2026-11-12/n-x20/outputs/场景2-多层幕布-*。未新增投影机位或镜头假设，无屏幕操作、Blender渲染或现场验证。

2026-11-12: The user clarified that this request concerns scene 2 with curtains, not the wall-projection layout. Extracted component #80 from the restored original SKP through the local SketchUp C API: 24 vertical screens in three groups, all 5 m high. The center has eight 7 m screens over 1.512 m depth; each side has four 5.04 m screens and four 3.36 m screens over 1.35 m depth. Side groups are staggered; total bounds are 12.054916 m wide by 6.932407 m deep. Orthographic PNG/SVG and provenance JSON were saved under E:/Codex/workspace/2026-11-12/n-x20/outputs/场景2-多层幕布-*. No projector positions or lens assumptions were added, and no screen interaction, Blender render or on-site validation was performed.

### 方案 C 的 SU 视图 / Plan C SketchUp views

2026-11-12：通过 SketchUp 26.2.243 原生 Ruby API 在方案 C 副本中新增俯视机位、空间机位、墙面覆盖三个 Scenes，以及机位/高度/参数标注和分类 Tags。原模型及原六个 Scenes 保留。输出：E:/Codex/workspace/2026-11-12/n-x20/outputs/场景1-方案C-机位与视图.skp，默认俯视。用户随后明确要求后台运行，已关闭本次启动的 SketchUp 进程，此后只用无窗口 C API 调整标注对比度并保存、重新打开验证成功。原生 PNG 导出早于文字对比度调整，不代表最终标注颜色；最终 SKP 为浅色标注配原深色样式。未重新计算光路或现场验收，机位仍为历史方案 C。

2026-11-12: Used the native SketchUp 26.2.243 Ruby API to add three scenes (top layout, spatial layout and wall coverage), projector/height/parameter annotations and categorized tags to a copy of plan C. Preserved the source model and its six original scenes. Output: E:/Codex/workspace/2026-11-12/n-x20/outputs/场景1-方案C-机位与视图.skp, opening on the top view. After the user explicitly required background-only work, closed the launched SketchUp process; subsequent contrast edits, saving and successful reopen validation used only the windowless C API. Native PNG exports precede the annotation contrast adjustment; the final SKP uses light annotations with the original dark style. No optical recalculation or on-site validation; positions remain historical plan C.
