# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

[![Tests](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml/badge.svg)](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml)

RoboPilot 是一个不依赖 ROS 环境的 ROS 风格项目静态工程工具链。

它帮助机器人学习者和开发者在不安装 ROS、ROS2、catkin、colcon、仿真器或机器人硬件的情况下，规划、校验、生成、检查、更新、回滚、分析和迁移 ROS/ROS2 风格项目结构。

## RoboPilot 能做什么

- 从任务描述创建并校验 `ProjectSpec`。
- 生成确定性的 ROS 风格 Python package 骨架。
- 在生成前 refine 和 diff spec。
- 通过 apply-preview、apply-plan、apply、rollback、history 形成安全更新闭环。
- 静态 inspect 项目并导出报告。
- 检测 RoboPilot、ROS1、ROS2、mixed、non-ROS 和 unknown 项目类型。
- 静态检查 ROS1 catkin 和 ROS2 ament package。
- 静态分析声明依赖和检测到的依赖使用。
- 生成、校验、diff 和 preview ROS1 到 ROS2 的迁移计划。
- 提供离线错误日志分析和 Mermaid workflow graph 工具。
- 可选使用 LLM，但只用于生成或 refine 已校验的 `ProjectSpec` 数据。
- 提供轻量 Python API 和 VSCode extension 源码，并支持 migration scaffold workflow。

RoboPilot 不会运行 ROS、ROS2、launch 文件、生成节点、`catkin_make` 或 `colcon`。

## Quick Start

当前支持 Python 3.10 和 3.11。包元数据声明 `>=3.10,<3.12`；Python 3.12 和 3.13 暂不声明支持。

从源码安装：

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -e ".[dev]"
robopilot --help
```

PyPI 发布后：

```bash
pip install robopilot
robopilot --help
```

Windows 下如果 pytest 临时目录有权限问题：

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

安全更新闭环：

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
robopilot history --project outputs/demo_detector
```

静态项目检查：

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

ROS 风格静态分析：

```bash
robopilot detect path/to/project
robopilot inspect-ros1 path/to/ros1_package
robopilot inspect-ros2 path/to/ros2_package
robopilot deps path/to/project
```

ROS1 到 ROS2 迁移规划：

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
robopilot migrate-plan-validate --plan migration_plan.yaml
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
robopilot migrate-scaffold-preview --plan migration_plan.yaml
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md
```

## 文档

- [Command Reference](docs/command_reference.md)
- [Workflows](docs/workflows.md)
- [Architecture](docs/architecture.md)
- [Python API](docs/api.md)
- [JSON Contracts](docs/json_contracts.md)
- [Integration Notes](docs/integration_notes.md)
- [VSCode Extension](docs/vscode_extension.md)
- [Developer Setup](docs/developer_setup.md)
- [Testing](docs/testing.md)
- [Release Process](docs/release_process.md)
- [PyPI Publishing](docs/pypi_publish.md)
- [Compatibility](docs/compatibility.md)
- [Known Limitations](docs/known_limitations.md)
- [Stability Policy](docs/stability_policy.md)
- [Demo Script](docs/demo_script.md)
- [v1.0.0 Scope](docs/v1_scope.md)
- [Changelog](CHANGELOG.md)
- [Roadmap](roadmap.md)

## 安全模型

- 默认的 plan、validate、diff、inspect、report、detect、deps 和 migration 命令都是静态或只读的。
- `apply` 默认 dry-run，只有显式传入 `--confirm` 才会写文件。
- confirmed apply 只写入 validated apply plan 中列出的文件。
- 更新已有文件前会创建备份。
- `rollback` 默认 dry-run，只从 RoboPilot backup 目录恢复文件。
- migration plan / validate / diff / preview 不会修改源项目。
- 可选 LLM 路径只能输出 `ProjectSpec`，并且必须通过校验。

## 示例输出

静态生成示例项目位于：

```txt
examples/generated_projects/demo_detector/
```

临时生成项目应放在 `outputs/` 下，该目录会被 git 忽略。

## 项目状态

当前版本线：`v1.11.0`。

RoboPilot 的 v1 基线仍然是不依赖 ROS 的静态工程工作流：

```txt
plan -> refine -> diff -> validate -> generate
      -> apply-preview -> apply-plan -> apply -> rollback -> history
      -> inspect -> repair-suggest -> report
      -> detect -> inspect-ros1 -> inspect-ros2 -> deps
      -> migrate-plan -> migrate-plan-validate -> migrate-plan-diff -> migrate-preview
      -> migrate-scaffold-preview -> migrate-scaffold -> migrate-scaffold-validate
      -> migrate-scaffold-report
```

CLI 仍是主要用户界面；Python API、JSON contracts、增强的依赖分析器和 VSCode extension 用于后续集成，并支持 migration scaffold workflow。

## 开发

运行测试：

```bash
python -m pytest
```

Windows fallback：

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

打包检查：

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

## License

MIT
