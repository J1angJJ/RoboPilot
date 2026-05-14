# VSCode 扩展

RoboPilot 在 `vscode-extension/` 下提供轻量 VSCode extension。

它是 RoboPilot CLI 的薄 UI 包装：调用 CLI、读取 JSON 或 Markdown 输出，然后在 OutputChannel 和简单 TreeView 中展示结果。它不会在 TypeScript 中重新实现 RoboPilot 核心逻辑。

## 安装 CLI

扩展运行时需要能找到 RoboPilot CLI：

```bash
pip install robopilot
```

源码开发时：

```bash
python -m pip install -e ".[dev]"
```

如果 VSCode 找不到命令，配置：

```txt
robopilot.executablePath
```

## 设置

- `robopilot.executablePath`：RoboPilot CLI 路径，默认是 `robopilot`。
- `robopilot.outputDirectory`：扩展生成 migration plan、scaffold 和 report 的目录，默认是 `.robopilot_vscode`。

## Command Palette 命令

- `RoboPilot: Detect Workspace`
- `RoboPilot: Inspect ROS1 Package`
- `RoboPilot: Analyze Dependencies`
- `RoboPilot: Generate Migration Plan`
- `RoboPilot: Preview Migration`
- `RoboPilot: Preview Migration Scaffold`
- `RoboPilot: Generate Migration Scaffold`
- `RoboPilot: Validate Migration Scaffold`
- `RoboPilot: Generate Scaffold Report`
- `RoboPilot: Open Scaffold Report`
- `RoboPilot: Validate ProjectSpec`
- `RoboPilot: Show Output`

## 迁移 scaffold 工作流

典型顺序：

```txt
RoboPilot: Generate Migration Plan
  -> RoboPilot: Preview Migration Scaffold
  -> RoboPilot: Generate Migration Scaffold
  -> RoboPilot: Validate Migration Scaffold
  -> RoboPilot: Generate Scaffold Report
  -> RoboPilot: Open Scaffold Report
```

默认产物：

- `.robopilot_vscode/migration_plan.json`
- `.robopilot_vscode/ros2_scaffold/`
- `.robopilot_vscode/scaffold_report.md`

## 安全边界

扩展不需要 ROS 或 ROS2，不运行 `catkin_make`、`colcon`、launch 文件或生成节点，也不会调用外部 LLM API。

`Generate Migration Scaffold` 只写入配置的输出目录，并且默认不覆盖已有 scaffold 文件。

## Marketplace 状态

本地 VSIX 打包已经支持。Marketplace 发布说明见 [VSCode Marketplace 发布说明](vscode_marketplace.md)。在明确发布前，不要声称扩展已经上架 Marketplace。
