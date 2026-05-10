# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

面向 ROS 风格机器人开发流程的轻量级离线开发工具。

RoboPilot 帮助机器人学习者和开发者生成 ROS 风格 Python 包骨架、分析常见机器人开发错误日志，并把简单的软件流水线转换成 Mermaid 工作流图。当前 MVP 强调本地、可复现、硬件友好：不需要 ROS2、GPU、Docker、OpenAI API，也不引入重型框架。

## 核心能力

- `plan`：把机器人任务转换成可读的 `robopilot.yaml` ProjectSpec。
- `validate`：在生成前检查保存的 ProjectSpec。
- `generate`：从任务描述或已保存的 ProjectSpec 生成 ROS 风格 Python 包。
- `inspect`：静态检查已生成项目或 ROS 风格项目目录。
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

检查已生成项目：

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot inspect examples/generated_projects/demo_detector --json
```

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

生成包结构：

```txt
examples/generated_projects/demo_detector/
|-- package.xml
|-- setup.py
|-- setup.cfg
|-- README.md
|-- robopilot.yaml
|-- launch/
|   `-- demo_detector.launch.py
|-- config/
|   `-- params.yaml
`-- demo_detector/
    |-- __init__.py
    `-- detector_node.py
```

Mermaid 图输出：

```mermaid
graph LR
    camera --> detector
    detector --> tracker
```

## 项目状态

RoboPilot 目前是早期 v0.4.0 MVP，重点是离线、轻量的机器人开发辅助流程。发布记录见 [`CHANGELOG.md`](CHANGELOG.md)。

已实现：

- MVP 0.1：离线 ROS 风格包生成器
- MVP 0.2：机器人错误日志分析器
- MVP 0.3：工作流图生成器
- MVP 0.4：基于 prompt 的模板选择
- MVP 0.5：Spec-first 生成流程
- MVP 0.6：项目检查器

暂未实现：

- 真实 ROS2 运行时执行
- LLM 生成
- RAG
- Streamlit 或 Gradio UI
- VSCode 扩展
- 机器人部署工具

## Roadmap 摘要

近期计划：

1. 保留离线模式的可选 LLM 辅助生成
2. 轻量级演示 UI
3. ROS 风格工作区项目检查

长期方向：

- ROS 风格工作区项目检查
- 面向机器人学习者的更好调试建议
- AI 辅助补丁生成
- 工作流可视化与解释

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

## 项目结构

```txt
robopilot/
|-- README.md
|-- README.zh-CN.md
|-- roadmap.md
|-- pyproject.toml
|-- src/
|   `-- robopilot/
|       |-- main.py
|       |-- generator/
|       |-- debugger/
|       |-- graph/
|       |-- inspector/
|       `-- utils/
|-- examples/
|-- tests/
`-- docs/
```

## License

MIT License.
