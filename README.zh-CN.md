# RoboPilot

[English](README.md) | [简体中文](README.zh-CN.md)

[![Tests](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml/badge.svg)](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml)

RoboPilot 是一个不需要安装 ROS 的 ROS 风格项目静态工程工具链。

它帮助机器人学习者和开发者规划、细化、验证、生成、检查、更新、回滚、记录和审查 ROS/ROS2 风格项目结构，而不需要本地安装 ROS、ROS2、catkin、colcon、仿真器运行时或机器人硬件。

## RoboPilot 能做什么

- 从机器人任务创建并验证 `ProjectSpec`。
- 生成确定性的 ROS 风格 Python 包骨架。
- 在生成前细化、比较和验证规格文件。
- 预览、导出、应用、备份、回滚并记录安全的项目更新。
- 静态检查项目并导出只读报告。
- 检测 RoboPilot、ROS1、ROS2、混合 ROS 风格、非 ROS 和未知项目类型。
- 静态检查 ROS1 catkin 包。
- 分析声明依赖和代码中检测到的依赖。
- 构建、验证、比较并预览 ROS1 到 ROS2 的静态迁移计划。
- 提供离线规则化的机器人错误日志分析和 Mermaid 工作流图生成。
- 可选使用 LLM，但只用于生成或细化经过验证的 `ProjectSpec` 数据。

RoboPilot 不会运行 ROS、ROS2、launch 文件、生成的代码、`catkin_make` 或 `colcon`。

## 快速开始

当前版本线支持 Python 3.10 和 3.11。包元数据声明为 `>=3.10,<3.12`；在测试套件通过之前，暂不声明支持 Python 3.12 和 3.13。

当前可从源码安装：

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -U pip
pip install -e ".[dev]"
robopilot --help
```

PyPI 发布后可使用：

```bash
pip install robopilot
robopilot --help
```

Windows 上如果 pytest 临时目录权限有问题，可以使用：

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

## 核心工作流

Spec-first 项目生成：

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
robopilot validate --spec robopilot.yaml
robopilot generate --spec robopilot.yaml
```

迭代式规格审查：

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml
```

安全项目更新：

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

ROS 风格静态分析：

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

- [命令参考](docs/command_reference.md)
- [工作流](docs/workflows.md)
- [架构](docs/architecture.md)
- [Python API](docs/api.md)
- [开发者设置](docs/developer_setup.md)
- [测试](docs/testing.md)
- [发布流程](docs/release_process.md)
- [PyPI 发布](docs/pypi_publish.md)
- [兼容性](docs/compatibility.md)
- [已知限制](docs/known_limitations.md)
- [稳定性策略](docs/stability_policy.md)
- [演示脚本](docs/demo_script.md)
- [v1.0.0 范围](docs/v1_scope.md)
- [更新日志](CHANGELOG.md)
- [路线图](roadmap.md)

## 安全模型

RoboPilot 围绕静态分析和显式审查设计：

- 默认的规划、验证、比较、检查、报告、检测、依赖分析和迁移命令都是只读的。
- `apply` 默认是 dry-run，只有加上 `--confirm` 才会写文件。
- 确认后的更新只会写入经过验证的 apply plan 中列出的文件。
- 更新已有文件前会先备份。
- `rollback` 默认是 dry-run，并且只从 RoboPilot 备份目录恢复文件。
- 迁移规划、验证、比较和预览不会修改源项目。
- 可选 LLM 路径只限于 `ProjectSpec` 规划/细化，并且必须通过验证后才能进入生成或 apply 工作流。

## 示例输出

仓库中包含一个静态生成示例项目：

```txt
examples/generated_projects/demo_detector/
```

临时生成项目应放在 `outputs/` 下，该目录会被 git 忽略。

## 项目状态

当前稳定版本：`v1.2.0`。

RoboPilot 的 v1 基线是一个不需要 ROS 的静态工程工作流：

```txt
plan -> refine -> diff -> validate -> generate
      -> apply-preview -> apply-plan -> apply -> rollback -> history
      -> inspect -> repair-suggest -> report
      -> detect -> inspect-ros1 -> deps
      -> migrate-plan -> migrate-plan-validate -> migrate-plan-diff -> migrate-preview
```

Python API 层可用于脚本和后续集成；CLI 仍然是主要用户界面。

## 开发

运行测试：

```bash
python -m pytest
```

Windows fallback：

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

本地打包检查：

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

## License

MIT
