STRINGS SPACE 现独立维护于 `kuanfuweimu/strings-space`，默认分支为 `main`。原版继续保留在 `kuanfuweimu/strings-web`。

- 空间线条结构、移动灯光、金属材质与地面镜像反射。
- 生长镜头追踪，支持按钮或 T 开关、跟随强度与缓动。
- 材质预设、可保存的自定义材质、MIDI 与手柄控制。
- 参数与黑场约 0.2 秒平滑过渡。
- 默认端口 8788，支持 WebM 和 4K60 离线导出。
- 参考 showcase 的亮度参数和逐场景曝光补偿保存在 `presets/showcase-reference.json`。

本版本使用实时着色和反射近似，未实现硬件光线追踪。TouchDesigner 接入口尚未集成到 SPACE。

下载下方 Source code ZIP，解压后运行 `node server.js`，或在 Windows 双击 `start.bat`。本地视频仍保存在 `out/`，不随源码上传。

验证：7 项 Node 测试通过；7 组着色器通过独立 OpenGL 编译与渲染检查。
