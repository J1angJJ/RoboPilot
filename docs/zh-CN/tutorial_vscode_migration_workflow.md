# 教程：VSCode 辅助迁移工作流

RoboPilot VSCode extension 是 RoboPilot CLI 的轻量 UI 包装。它通过 Command Palette 调用 CLI 和 JSON 输出，不在 TypeScript 中重新实现迁移逻辑。

## 准备

先安装 RoboPilot CLI：

```bash
pip install robopilot
```

源码开发时使用：

```bash
python -m pip install -e ".[dev]"
```

如果 VSCode 找不到 `robopilot`，在设置中配置：

```txt
robopilot.executablePath
```

Windows + conda 用户通常需要把它指向 conda 环境里的 `robopilot.exe`。

## 打开工作区

可以打开整个 RoboPilot 仓库，也可以打开示例目录：

```txt
examples/ros1_migration_demo/
```

扩展默认把集成产物写入：

```txt
.robopilot_vscode/
```

你可以通过 `robopilot.outputDirectory` 修改这个目录。

## Command Palette 流程

按顺序运行：

```txt
RoboPilot: Detect Workspace
RoboPilot: Generate Migration Plan
RoboPilot: Preview Migration Scaffold
RoboPilot: Generate Migration Scaffold
RoboPilot: Validate Migration Scaffold
RoboPilot: Generate Scaffold Report
RoboPilot: Open Scaffold Report
```

典型产物是：

```txt
.robopilot_vscode/migration_plan.json
.robopilot_vscode/ros2_scaffold/
.robopilot_vscode/scaffold_report.md
```

OutputChannel 会显示 target style、预计文件、生成文件、验证状态、issues、warnings 和 report path。

## 安全边界

扩展不会运行 ROS、ROS2、`catkin_make`、`colcon`、launch 文件或生成节点。它也不会修改源 ROS1 项目。

`Generate Migration Scaffold` 只写入 `.robopilot_vscode/ros2_scaffold/` 或你配置的输出目录，并且默认不会传递 `--overwrite`。

## 结果解读

`Generate Scaffold Report` 后，打开 `scaffold_report.md`，重点看：

- validation status
- missing files
- placeholder checks
- manual migration items
- `MIGRATION_NOTES.md`
- safety note

通过验证不代表运行时正确。它只说明 scaffold 符合 RoboPilot 的静态预期。

## 常见问题

- 找不到 `robopilot`：安装 CLI，或配置 `robopilot.executablePath`。
- VSCode 看不到 conda PATH：从已激活 conda 的终端启动 VSCode，或使用绝对路径。
- `.robopilot_vscode/ros2_scaffold` 已存在：先审查旧输出，再选择新输出目录或手动清理 demo 输出。
- 报告不存在：先运行 `RoboPilot: Generate Scaffold Report`。

更多信息见 [常见问题排查](troubleshooting.md)。
