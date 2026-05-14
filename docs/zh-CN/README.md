# RoboPilot 中文文档

这里是 RoboPilot 的中文文档入口。RoboPilot 是一个不依赖 ROS 的 ROS 风格项目静态工程工具链，适合用来学习、检查、规划、生成、验证和迁移项目结构。

RoboPilot 默认不会运行 ROS、ROS2、`catkin_make`、`colcon`、launch 文件或生成的节点代码。

## 快速入口

- [中文 README](../../README.zh-CN.md)
- [ROS1 到 ROS2 迁移脚手架教程](tutorial_ros1_to_ros2_migration.md)
- [VSCode 辅助迁移教程](tutorial_vscode_migration_workflow.md)
- [常见问题排查](troubleshooting.md)
- [VSCode 扩展说明](vscode_extension.md)
- [VSCode 本地 VSIX 打包](vscode_packaging.md)
- [VSCode Marketplace 发布说明](vscode_marketplace.md)
- [主要工作流](workflows.md)
- [已知限制](known_limitations.md)
- [演示讲稿](demo_walkthrough.md)

## 建议阅读顺序

1. 先阅读 [中文 README](../../README.zh-CN.md)，了解 RoboPilot 的定位和安全边界。
2. 如果你想体验迁移流程，阅读 [ROS1 到 ROS2 迁移脚手架教程](tutorial_ros1_to_ros2_migration.md)。
3. 如果你使用 VSCode，阅读 [VSCode 辅助迁移教程](tutorial_vscode_migration_workflow.md)。
4. 遇到安装、编码、路径或输出目录问题时，查看 [常见问题排查](troubleshooting.md)。

## 重要边界

RoboPilot 的迁移能力是静态辅助流程。它可以生成 migration plan、预览 scaffold、生成保守的 ROS2 scaffold、验证 scaffold，并导出 Markdown report，但它不会自动完成业务逻辑迁移，也不会证明 ROS2 运行时正确性。
