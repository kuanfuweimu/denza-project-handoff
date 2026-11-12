# 参考、资料板与演示页

## 用户给定的五条链接

| 链接 | 对应方向 |
|---|---|
| https://www.youtube.com/c/monocolor | MONOCOLOR，线束、点云、穹顶空间；图库选用了 Entangled Structures |
| https://ouchhh.tv/ | Ouchhh，建筑表面数据影像；图库选用了 POETIC AI |
| https://www.youtube.com/watch?v=eXduT_mdbQc | HOMEOMORPHISM，穹顶视听/数据结构 |
| https://www.youtube.com/watch?v=CknHVdMZ5xg | Cinématique，舞者与数字图形/空间形变 |
| https://www.youtube.com/watch?v=xvJNia3z11I | Hakanaï，舞者与立体投影/变形网格 |

用户特别指定的线条作品：https://mnclr.com/entangled-structures 。需要借鉴柔和、流动、生长和脉冲生长的结构语言，制作数字投影内容。舞者由现场完成，数字视频里不添加人。

现有演示稿给五个链接配了22张官方参考图，并记录作者/来源。归档 `00_项目资料/外部参考作品` 与 `04_演示稿/denza-deck`；来源数据见 `quickstart/presentation-source/media-provenance.json`、`reference-galleries.json` 和 `research-assets/reference_sources.json`。链接与作品对应沿用既有归档，本次没有重新观看全部YouTube视频。

## Figma

- 当前三场景文件：https://www.figma.com/design/OELjIHAEngjsSxtuGQSAec/Untitled?node-id=2-2
- 早期文件：https://www.figma.com/design/HFmCr96pJNOfJL0d3Ykt56/Video-Projects?node-id=0-1
- 早期文件曾出现连接账号权限问题，后改用当前文件。换电脑后需重新验证Figma连接账号，不能把旧连接状态当作可用凭据。
- 本次不依赖云端权限才能读资料：现有图片、视频、Figma整理前后截图已在素材包中。
- 归档快照不等于可编辑 `.fig` 文件；本次未导出原生Figma文档。新云端修改若不在已归档快照中，需要恢复访问后再拉取。

## 分享演示页

- https://www.kuanfuweimu.com/presentations/denza/
- 参考段落：https://www.kuanfuweimu.com/presentations/denza/#reference-links

最终选择是个人主站下的隐藏直达页面：上下滚动、黑底白字、图片保留比例可放大、没有主站导航入口、不进站点地图。**不要再做独立托管或要求阿里云DNS。** 旧Vercel独立地址只是历史方案，不是交接主入口。本次链接状态未重新远程验收，以归档静态页面为离线保底。

恢复后 `04_演示稿/denza-deck/dist/index.html` 与 `dist/assets` 是完整静态页面。可用 `python -m http.server 8790 --bind 127.0.0.1 --directory <dist完整路径>` 本地提供服务。外站YouTube/Vimeo播放仍依赖外网访问；本地参考图/四条归档参考视频可离线使用。
