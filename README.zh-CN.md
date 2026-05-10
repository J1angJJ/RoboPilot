# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

面向 ROS 风格机器人开发流程的轻量级开发工具。

RoboPilot 帮助机器人学习者和开发者生成 ROS 风格 Python 包、规划和细化 ProjectSpec、分析常见错误日志、生成 Mermaid 工作流图，并静态检查项目结构。默认工作流保持本地、可复现、硬件友好：不需要 ROS2、GPU、Docker、OpenAI API，也不引入重型框架。

## 核心能力

- `plan`：把机器人任务转换成可读的 `robopilot.yaml` ProjectSpec。
- `refine`：基于离线规则把已有 ProjectSpec 细化成一个新的 spec 文件。
- `plan --planner llm`：为已配置环境提供可选的 ProjectSpec-only OpenAI planner。
- `validate`：在生成前检查保存的 ProjectSpec。
- `generate`：从任务描述或已保存的 ProjectSpec 生成 ROS 风格 Python 包。
- `inspect`：静态检查已生成项目或 ROS 风格项目目录。
- `repair-suggest`：根据检查结果给出安全修复建议，不会自动修改文件。
- `report`：导出结合项目检查和修复建议的静态 Markdown 报告。
- `debug`：使用离线规则分析机器人相关错误日志。
- `graph`：把箭头形式的机器人软件流水线转换为 Mermaid 图。

## 快速开始

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd RoboPilot
python -m venv .venv
pip install -e ".[dev]"
robopilot --help
```

可选 LLM planner 支持：

```bash
pip install -e ".[dev,llm]"
```

## 演示

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
robopilot generate --spec refined.yaml
```

Optional LLM refinement:

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner llm --model gpt-4.1-mini --output llm_refined.yaml
robopilot diff --old robopilot.yaml --new llm_refined.yaml
```

LLM refinement requires `OPENAI_API_KEY`. It writes a new ProjectSpec, not project files or source code. Run `robopilot diff` before generating from an LLM-refined spec.

`diff` is static and read-only:

```bash
robopilot diff --old robopilot.yaml --new refined.yaml --json
```

Apply preview is also read-only:

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector --json
```

`apply-preview` only reports files to create, update, keep, or review as conflicts. It does not modify project files.

Apply plan is read-only too:

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.json --format json
```

`apply-plan` exports the apply-preview result for review or sharing. It does not modify project files and does not implement real apply.

`refine` 默认会写入新的 spec 文件，不会修改原始 `robopilot.yaml`。本版本没有 `--in-place`。

选择 planner：

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner rule
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm --model gpt-4.1-mini
```

默认 planner 是 `rule`，保持完全离线。可选的 `llm` planner 从环境变量读取 `OPENAI_API_KEY`，并使用 `ROBOPILOT_LLM_MODEL` 或 `--model` 指定模型。它只能产生 ProjectSpec 结构化 JSON 或 YAML，不能直接生成项目文件或代码；RoboPilot 会在生成前验证 ProjectSpec。

示例环境文件：

```bash
OPENAI_API_KEY=
ROBOPILOT_LLM_MODEL=gpt-4.1-mini
```

检查、修复建议与报告：

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

分析错误日志：

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

生成 Mermaid 工作流图：

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

完整演示流程见 [`docs/demo_script.md`](docs/demo_script.md)。

## 项目状态

RoboPilot 目前是早期 v0.13.0 MVP，默认仍然保持离线工作流，并新增 read-only apply plan export。发布记录见 [`CHANGELOG.md`](CHANGELOG.md)。

已实现：

- 离线 ROS 风格包生成器
- ProjectSpec 规划、验证、细化与生成
- 机器人错误日志分析器
- 工作流图生成器
- 项目检查器
- 项目修复建议
- 项目报告导出
- 可选 OpenAI provider client for ProjectSpec planning

暂未实现：

- 真实 ROS2 运行时执行
- LLM 直接生成项目文件或代码
- RAG
- Streamlit 或 Gradio UI
- VSCode 扩展
- 机器人部署工具

## 开发说明

运行测试：

```bash
pytest
```

部分 Windows 环境中，pytest 可能无法访问默认用户临时目录。此时可以使用项目内临时目录：

```powershell
New-Item -ItemType Directory -Path .pytest_tmp -Force
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

默认生成项目会写入 `outputs/`，该目录已被 Git 忽略。用于展示的静态示例位于 `examples/`。

## License

MIT License.
