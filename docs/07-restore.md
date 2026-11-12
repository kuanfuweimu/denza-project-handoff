# 换电脑恢复

需要Python3.10+、Git、GitHub CLI，登录 `kuanfuweimu` 或已授权的协作者。仓库和附件均为私有。不要把PAT写进文档或命令历史。

进入clone后的仓库执行：

```powershell
python scripts/restore.py --scope projection --destination 'D:\Kuanfuweimu\2-Commission\VJ Commission'
```

先恢复三场景资料、客户方案、投影/模型即可开始设备沟通。全部工程、视频和生成工具则：

```powershell
python scripts/restore.py --scope all --destination 'D:\Kuanfuweimu\2-Commission\VJ Commission'
```

- 默认下载缓存位于 `<destination>/DENZA N/_work/handoff-downloads`。
- 附件是去重ZIP，按需要下载；恢复每个文件时核对SHA256，恢复重复项到原目录。
- 已有相同文件跳过；如果同路径内容不同，拒绝覆盖并报错，避免把另一台电脑的新改动盖掉。
- `--archives-dir <现有附件目录>` 可离线恢复。
- `--list` 只列所需附件和容量，不下载、不写工程。
- `--scope projection` 包含00项目资料、01墙面、02吊顶、03LED、入口/清单及DENZA N根模型/工程；所有视频和工具用all。
- 约需附件大小+恢复大小的空余磁盘，all建议预留15GB。参考图库、客户Keynote和4K视频占主要容量。

验证单独执行：`python scripts/restore.py --scope all --destination '<父目录>' --verify-only`。

## 重建依赖

Node服务只依赖内置库；Python离屏工具需重新安装图形库，参见 `inventory/runtime-versions.json`。TOE/SKP/BLEND需要对应应用和许可；本包不附带安装器和许可证。不得盲目加载插件后假设工程兼容当前版本。

## 原路径与可移植性

restore目标是两个兄弟目录的父目录，不是DENZA N本身。默认恢复到原D盘父目录可满足现有导出脚本硬编码。改根目录后用 `scripts/rebase_export_paths.py` 调整导出工具副本，旧投影模型SDK/字体路径仍要人工核验。

接管仓库中code是代码快照；若继续开发WEB/SPACE，优先clone对应独立仓库并对照固定commit。不要把快照目录当成已经带完整Git历史的子仓库。
