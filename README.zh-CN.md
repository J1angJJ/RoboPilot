# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

面向 ROS 风格机器人开发流程的轻量级开发工具。

RoboPilot 帮助机器人学习者和开发者生成 ROS 风格 Python 包骨架、分析常见机器人开发错误日志、生成 Mermaid 工作流图，并静态检查项目结构。默认工作流仍然强调本地、可复现、硬件友好：不需要 ROS2、GPU、Docker、OpenAI API，也不引入重型框架。

## 核心能力

- `plan`：把机器人任务转换成可读的 `robopilot.yaml` ProjectSpec。
- `plan --planner llm`：为已配置环境提供可选的 ProjectSpec-only OpenAI planner。
- `validate`：在生成前检查保存的 ProjectSpec。
- `generate`：从任务描述或已保存的 ProjectSpec 生成 ROS 风格 Python 包。
- `inspect`：静态检查已生成项目或 ROS 风格项目目录。
- `repair-suggest`：根据检查结果给出安全修复建议，不会自动修改文件。
- `report`：导出结合项目检查和修复建议的静态 Markdown 报告。
- `debug`：使用离线规则分析机器人相关错误日志。
- `graph`：把箭头形式的机器人软件流水线转换为 Mermaid 图。

## 快速开始

克隆并安装：

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd RoboPilot
python -m venv .venv
```

激活环境。

Windows：

```bash
.venv\Scripts\activate
```

macOS/Linux：

```bash
source .venv/bin/activate
```

以 editable 模式安装：

```bash
pip install -e ".[dev]"
```

可选 LLM planner 支持：

```bash
pip install -e ".[dev,llm]"
```

检查 CLI：

```bash
robopilot --help
```

## 演示

生成 ROS 风格包：

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

Spec-first 工作流：

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
robopilot validate --spec robopilot.yaml
robopilot generate --spec robopilot.yaml
```

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

检查已生成项目：

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot inspect examples/generated_projects/demo_detector --json
```

生成安全修复建议，不会自动修改文件：

```bash
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector --json
```

导出静态 Markdown 报告：

```bash
robopilot report examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

报告生成是静态、只读的。RoboPilot 不会执行 ROS2、launch 文件、colcon 或生成的 Python 代码。

生成其他模板类型：

```bash
robopilot generate --name camera_reader --task "Create a camera subscriber for webcam frames."
robopilot generate --name base_controller --task "Create a velocity controller publishing cmd_vel motion commands."
robopilot generate --name perception_stack --task "Create a camera -> detector -> tracker perception workflow."
robopilot generate --name helper_node --task "Create a simple heartbeat node."
```

分析机器人错误日志：

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

生成 Mermaid 工作流图：

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

将 Mermaid 图写入文件：

```bash
robopilot graph --pipeline "camera -> detector -> tracker" --output examples/graphs/demo_pipeline.mmd
```

完整演示流程见 [`docs/demo_script.md`](docs/demo_script.md)。

## 示例输出

仓库中包含用于 GitHub 展示和演示的静态示例：

- 生成包示例：[`examples/generated_projects/demo_detector/`](examples/generated_projects/demo_detector/)
- 生成器 prompt：[`examples/prompts/demo_detector.txt`](examples/prompts/demo_detector.txt)
- 错误日志示例：[`examples/error_logs/`](examples/error_logs/)
- 流水线输入：[`examples/pipelines/demo_pipeline.txt`](examples/pipelines/demo_pipeline.txt)
- Mermaid 图：[`examples/graphs/demo_pipeline.mmd`](examples/graphs/demo_pipeline.mmd)

## 项目状态

RoboPilot 目前是早期 v0.8.0 MVP，重点是保持离线默认能力，同时提供可选的 OpenAI ProjectSpec planner。发布记录见 [`CHANGELOG.md`](CHANGELOG.md)。

已实现：

- 离线 ROS 风格包生成器
- 机器人错误日志分析器
- 工作流图生成器
- 基于 prompt 的模板选择
- Spec-first 生成流程
- 项目检查器
- 项目修复建议
- 项目报告导出
- Planner 接口与可选 ProjectSpec-only LLM planner
- OpenAI provider client for ProjectSpec planning

暂未实现：

- 真实 ROS2 运行时执行
- LLM 直接生成项目文件或代码
- RAG
- Streamlit 或 Gradio UI
- VSCode 扩展
- 机器人部署工具

## Roadmap 摘要

近期计划：

1. 继续加固 provider-backed ProjectSpec 规划
2. 改进静态报告和只读修复建议
3. 轻量级演示 UI

完整路线图见 [`roadmap.md`](roadmap.md)。

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
