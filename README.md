# DENZA Z · 项目接管入口

更新：2026-11-12（Asia/Shanghai）。这是三场景制作、投影沟通、参考资料和生成视觉的**私有完整交接仓库**。原件和已输出视频保持不变。

**下一步优先处理投影安装距离、投射尺寸和镜头比。** 设备方已经询问这三项。已有场景一模型模拟，但没有现场实测安装确认；不能把模拟值直接说成定案。先读 [投影交接](docs/02-projection.md) 和 [可转发沟通稿](docs/03-vendor-message.md)。

## 给另一台电脑的 agent

把下段直接交给它：

> 请接管 https://github.com/kuanfuweimu/denza-project-handoff 。这是私有仓库，使用我已授权的 GitHub 账号。先读 AGENTS.md、START_HERE.md 和 docs/02-projection.md，再检查 inventory/manifest.json。当前优先解决三个场景尤其墙面双投影与吊顶投影的机位、投射尺寸及镜头比；不要把历史模拟当实测。按 scripts/restore.py 下载 Release 素材并校验 SHA256。先恢复 projection 范围即可开始，随后按需恢复全部工程与视频。不要控制我的屏幕，不要修改个人主站，不要把资料公开。所有工作文件放 D 盘项目目录。接管后报告你确认了什么、还缺哪几项现场数据，再继续推进。

## 先看这些

| 内容 | 入口 |
|---|---|
| 下一位 agent 的工作顺序 | [START_HERE.md](START_HERE.md) |
| 三场景定位、已知与未知 | [docs/01-scenes.md](docs/01-scenes.md) |
| 投影参数、历史模型、镜头比 | [docs/02-projection.md](docs/02-projection.md) |
| 可直接转发给设备方的文字 | [docs/03-vendor-message.md](docs/03-vendor-message.md) |
| 五条参考、补充作品、Figma、网页 | [docs/04-references.md](docs/04-references.md) |
| 工程、视频、运行和重渲染 | [docs/05-engineering.md](docs/05-engineering.md) |
| 当前状态、待办与已否决方向 | [docs/06-status.md](docs/06-status.md) |
| 搬电脑与恢复 | [docs/07-restore.md](docs/07-restore.md) |
| 全部纳入文件、哈希、附件对应 | [inventory/manifest.json](inventory/manifest.json) |

## 工程和大型资料在哪

仓库直接提供交接文档、代码快照、轻量投影 TD 工程及其模型纹理、历史模拟脚本与预览。客户 PDF/Keynote、SketchUp、Blender、参考视频、所有本次输出视频等存放在本仓库的 [Release 附件](https://github.com/kuanfuweimu/denza-project-handoff/releases/tag/handoff-2026-11-12)。

**只 git clone 不等于拿到了全部素材。** Release 包已去重，需用恢复脚本重建重复路径，并核对 SHA256。原始文件名、目录关系和 provenance 保留。运行库、浏览器会话、缓存、Git 内部历史不打包；排除清单在 manifest。八九月份旧 `DENZA 2` 项目不冒充此次 LED 工程，只列旧档索引。

```powershell
gh auth status
gh repo clone kuanfuweimu/denza-project-handoff 'D:\Kuanfuweimu\2-Commission\VJ Commission\DENZA N\denza-project-handoff'
```

进入仓库后运行（Python 3.10+、GitHub CLI）：

```powershell
python scripts/restore.py --scope projection --destination 'D:\Kuanfuweimu\2-Commission\VJ Commission'
# 如需所有资料与所有视频：
python scripts/restore.py --scope all --destination 'D:\Kuanfuweimu\2-Commission\VJ Commission'
```

仓库是项目资料备份及交接；其中参考作品仅供方案研究，不代表获得外部作品的再发布或商用授权。没有附带账号密钥，私有仓库在另一台电脑需登录有访问权限的账号。
