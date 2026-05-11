# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

[![Tests](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml/badge.svg)](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml)

RoboPilot 是一个不依赖 ROS 环境的 ROS-style 静态工程工具链。

它面向机器人学习者和开发者，用于规划、细化、验证、生成、检查、更新、回滚、记录和迁移 ROS/ROS2-style 项目结构。默认工作流不需要安装 ROS、ROS2、catkin、colcon、仿真器或真实机器人硬件。

## RoboPilot 能做什么

- 从机器人任务创建并验证 `ProjectSpec`。
- 确定性生成 ROS-style Python 包骨架。
- 在生成前细化、比较和验证 spec。
- 预览、导出、应用、备份、回滚并记录安全的项目更新。
- 静态检查项目并导出 Markdown 报告。
- 检测 RoboPilot、ROS1、ROS2、混合、非 ROS 和未知项目类型。
- 静态检查 ROS1 catkin 包。
- 分析声明依赖和代码中检测到的依赖使用。
- 生成、验证、比较并预览 ROS1 到 ROS2 的静态迁移计划。
- 提供离线错误日志诊断和 Mermaid 工作流图生成工具。
- 可选使用 LLM，但仅用于生成或细化经过验证的 `ProjectSpec` 数据。

RoboPilot 不会运行 ROS、ROS2、launch 文件、生成代码、`catkin_make` 或 `colcon`。

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -e ".[dev]"
robopilot --help
```

如果 Windows 上 pytest 遇到临时目录权限问题，可以使用：

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## 核心工作流

Spec-first 生成：

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
robopilot validate --spec robopilot.yaml
robopilot generate --spec robopilot.yaml
```

迭代细化和审查：

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml
```

安全更新循环：

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
robopilot history --project outputs/demo_detector
```

静态项目审查：

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

ROS-style 静态分析：

```bash
robopilot detect path/to/project
robopilot inspect-ros1 path/to/ros1_package
robopilot deps path/to/project
```

ROS1 到 ROS2 迁移规划：

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
robopilot migrate-plan-validate --plan migration_plan.yaml
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
```

## 文档

- [Command Reference](docs/command_reference.md)
- [Workflows](docs/workflows.md)
- [Architecture](docs/architecture.md)
- [Testing](docs/testing.md)
- [Release Process](docs/release_process.md)
- [Compatibility](docs/compatibility.md)
- [Known Limitations](docs/known_limitations.md)
- [Stability Policy](docs/stability_policy.md)
- [Demo Script](docs/demo_script.md)
- [v1.0.0 Scope](docs/v1_scope.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](roadmap.md)

## 安全模型

RoboPilot 围绕静态分析和显式审查设计：

- 默认的 plan、validate、diff、inspect、report、detect、deps 和 migration 命令都是只读的。
- `apply` 默认是 dry-run，只有加上 `--confirm` 才会写文件。
- confirmed apply 只会写入已验证 apply plan 中列出的文件。
- 更新已有文件前会创建备份。
- `rollback` 默认是 dry-run，只会从 RoboPilot backup 目录恢复文件。
- migration plan / validate / diff / preview 不会修改源项目。
- 可选 LLM 路径仅限 `ProjectSpec` 规划和细化，生成或应用前必须通过验证。

## 示例输出

仓库中保留了一个静态生成示例：

```txt
examples/generated_projects/demo_detector/
```

临时生成项目应写入 `outputs/`，该目录已被 git 忽略。

## 项目状态

当前稳定版本：`v1.0.0`。

RoboPilot 的 no-ROS-required 静态工程工作流已作为 v1.0.0 稳定版发布：

```txt
plan -> refine -> diff -> validate -> generate
      -> apply-preview -> apply-plan -> apply -> rollback -> history
      -> inspect -> repair-suggest -> report
      -> detect -> inspect-ros1 -> deps
      -> migrate-plan -> migrate-plan-validate -> migrate-plan-diff -> migrate-preview
```

## 开发

运行测试：

```bash
python -m pytest
```

Windows fallback：

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## License

MIT
