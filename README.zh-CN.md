# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

[![Tests](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml/badge.svg)](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml)

RoboPilot 是一个轻量、离线优先的 ROS 风格机器人开发辅助工具。

它可以帮助机器人学习者和开发者规划 ProjectSpec、生成 ROS 风格 Python 包、分析常见错误日志、生成 Mermaid 工作流图，并静态检查、预览、应用和回滚项目文件变更。默认工作流保持本地、可复现、硬件友好：不需要 ROS2、GPU、Docker、OpenAI API，也不引入重型框架。

## 核心能力

- `plan`：把自然语言机器人任务转换成可读的 `robopilot.yaml` ProjectSpec。
- `refine`：用离线规则或可选 LLM provider 细化已有 ProjectSpec，并写入新 spec。
- `diff`：静态比较两个 ProjectSpec 文件。
- `validate`：验证保存后的 ProjectSpec。
- `generate`：从任务或 ProjectSpec 生成 ROS 风格 Python 包。
- `apply-preview`：只读预览 ProjectSpec 会对现有项目产生哪些文件变化。
- `apply-plan`：导出和验证只读 apply plan。
- `apply`：默认 dry-run，只有显式 `--confirm` 才会按 plan 写文件，并在更新前创建备份。
- `rollback`：默认 dry-run，只有显式 `--confirm` 才会从 RoboPilot 备份目录恢复文件。
- `inspect`：静态检查生成项目或 ROS 风格项目目录。
- `repair-suggest`：根据检查结果给出安全修复建议，不自动修改文件。
- `report`：导出静态 Markdown 项目报告。
- `debug`：用离线规则分析机器人相关错误日志。
- `graph`：把箭头形式的软件流水线转换成 Mermaid 图。

## 快速开始

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd RoboPilot
python -m venv .venv
pip install -e ".[dev]"
robopilot --help
```

可选 LLM 规划和细化支持：

```bash
pip install -e ".[dev,llm]"
```

## 演示流程

生成 ROS 风格包：

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

Spec-first 工作流：

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner rule --output refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml
robopilot validate --spec refined.yaml
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
robopilot generate --spec refined.yaml
```

`refine` 默认写入新的 spec 文件，不会修改原始 `robopilot.yaml`。当前没有 `--in-place`。

可选 LLM 细化：

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner llm --model gpt-4.1-mini --output llm_refined.yaml
robopilot diff --old robopilot.yaml --new llm_refined.yaml
```

LLM 细化需要 `OPENAI_API_KEY`。LLM 只能返回 ProjectSpec 兼容的 JSON 或 YAML，RoboPilot 会在写入前验证 spec；LLM 不会直接生成项目文件或源代码。建议在从 LLM 细化后的 spec 生成前先运行 `robopilot diff`。

Apply preview 是只读的：

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector --json
```

Apply plan 也是只读的：

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.json --format json
```

Apply 默认只做 dry-run：

```bash
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
robopilot apply --plan apply_plan.yaml --confirm --json
```

`apply` 只有在提供 `--confirm` 时才会写文件。它会验证 apply plan，重新运行 apply-preview，拒绝过期 plan 和冲突，并在更新已有文件前把原文件备份到 `.robopilot_backups/<timestamp>/`。

Rollback 默认也只做 dry-run：

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm --json
```

`rollback` 只有在提供 `--confirm` 时才会恢复文件。它只恢复 RoboPilot 备份目录中存在的文件，保留相对路径，不会删除 apply 阶段新创建的文件，也不会执行 ROS2、launch 文件、colcon 或生成代码。

项目检查和报告：

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

错误日志分析：

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
robopilot debug --text "ModuleNotFoundError: No module named 'cv_bridge'"
```

工作流图：

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

完整演示流程见 [`docs/demo_script.md`](docs/demo_script.md)，发布记录见 [`CHANGELOG.md`](CHANGELOG.md)。

## 项目状态

RoboPilot 目前是早期 v0.15.0 MVP，默认保持离线、规则化、可测试的开发工作流。

已实现：

- MVP 0.1：离线 ROS 风格包生成器
- MVP 0.2：机器人错误日志调试器
- MVP 0.3：工作流图生成器
- MVP 0.4：基于任务描述的模板选择
- MVP 0.5：Spec-first 生成
- MVP 0.6：项目检查器
- v0.5.0：项目修复建议
- v0.6.0：项目报告导出
- v0.7.0：Planner 接口和可选 LLM Planner
- v0.8.0：OpenAI Provider 集成
- v0.9.0：规则化 ProjectSpec 细化
- v0.10.0：静态 ProjectSpec Diff
- v0.11.0：可选 LLM-assisted ProjectSpec 细化
- v0.12.0：只读 Apply Preview
- v0.13.0：只读 Apply Plan Export
- v0.14.0：Safe Apply from Plan
- v0.15.0：Safe Apply Rollback

暂不包含：

- 真实 ROS2 运行时执行
- LLM 直接生成项目文件或代码
- 未确认的自动 apply
- rollback 自动删除新创建文件
- RAG
- Streamlit 或 Gradio UI
- VSCode 扩展
- 机器人部署工具

## 开发说明

运行测试：

```bash
pytest
```

如果 Windows 默认临时目录权限受限，可以使用项目内临时目录：

```powershell
New-Item -ItemType Directory -Path .pytest_tmp -Force
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

生成项目默认写入 `outputs/`，该目录已被 Git 忽略。静态展示示例位于 `examples/`。

## License

MIT License.
