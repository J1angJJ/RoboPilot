# RoboPilot

[English](README.md) | [中文](README.zh-CN.md)

[![Tests](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml/badge.svg)](https://github.com/J1angJJ/RoboPilot/actions/workflows/tests.yml)

RoboPilot 是一个不需要 ROS/ROS2 环境的静态工程工具链，用于 ROS 风格项目的规划、生成、检查、安全更新、回滚和记录。

默认工作流保持离线、可复现、可测试：不需要 ROS、ROS2、GPU、Docker、OpenAI API、catkin、colcon 或机器人硬件。

## 核心能力

- `plan`：把自然语言任务转换为 `robopilot.yaml` ProjectSpec。
- `refine`：用离线规则或可选 LLM provider 细化 ProjectSpec。
- `diff`：静态比较两个 ProjectSpec。
- `validate`：验证 ProjectSpec。
- `generate`：生成 ROS 风格 Python 包。
- `apply-preview`：只读预览 ProjectSpec 会产生哪些文件变化。
- `apply-plan`：导出和验证只读 apply plan。
- `apply`：默认 dry-run，只有 `--confirm` 才会按 plan 写文件。
- `rollback`：默认 dry-run，只有 `--confirm` 才会从 RoboPilot 备份恢复文件。
- `history`：查看项目本地 confirmed apply / rollback 历史记录。
- `inspect`：静态检查项目结构。
- `repair-suggest`：给出只读修复建议。
- `report`：导出 Markdown 项目报告。
- `debug`：用离线规则分析机器人错误日志。
- `graph`：生成 Mermaid 工作流图。

## 快速开始

```bash
git clone https://github.com/J1angJJ/RoboPilot.git
cd RoboPilot
python -m venv .venv
pip install -e ".[dev]"
robopilot --help
```

可选 LLM 支持：

```bash
pip install -e ".[dev,llm]"
```

## 演示流程

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner rule --output refined.yaml
robopilot diff --old robopilot.yaml --new refined.yaml
robopilot validate --spec refined.yaml
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
robopilot history --project outputs/demo_detector
robopilot history --project outputs/demo_detector --json
```

`apply` 和 `rollback` 都是 dry-run 优先。只有显式传入 `--confirm` 时才会写文件。confirmed apply 会在更新已有文件前创建 `.robopilot_backups/<timestamp>/` 备份；confirmed apply 和 confirmed rollback 会在项目本地 `.robopilot_history/` 下写入历史元数据。

`history` 只读取项目本地历史记录。它记录操作类型、时间、路径列表和摘要，不记录文件内容、密钥或环境变量。dry-run apply / rollback 不会写入成功修改历史。

生成项目：

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
robopilot generate --spec refined.yaml
```

检查、修复建议和报告：

```bash
robopilot inspect examples/generated_projects/demo_detector
robopilot repair-suggest examples/generated_projects/demo_detector
robopilot report examples/generated_projects/demo_detector --output report.md
```

错误日志和工作流图：

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

可选 LLM 细化：

```bash
robopilot refine --spec robopilot.yaml --instruction "Add a tracker node after the detector" --planner llm --model gpt-4.1-mini --output llm_refined.yaml
robopilot diff --old robopilot.yaml --new llm_refined.yaml
```

LLM 功能是可选的，需要 `OPENAI_API_KEY`。LLM 只能产生 ProjectSpec 兼容的 JSON 或 YAML；RoboPilot 会验证结果，LLM 不会直接写项目文件或生成代码。

完整演示流程见 [`docs/demo_script.md`](docs/demo_script.md)，发布记录见 [`CHANGELOG.md`](CHANGELOG.md)。

## 项目状态

RoboPilot 目前是早期 v0.16.0 MVP，默认保持离线、静态、可测试的工作流。

已实现：

- v0.1.0：离线 ROS 风格包生成、错误日志调试、Mermaid 图生成
- v0.2.0：Prompt-driven Template Selection
- v0.3.0：Spec-first Generation
- v0.4.0：Project Inspector
- v0.5.0：Project Repair Suggestions
- v0.6.0：Project Report Export
- v0.7.0：Planner Interface and Optional LLM Planner
- v0.8.0：Real LLM Provider Integration
- v0.9.0：Spec Refinement
- v0.10.0：Spec Diff
- v0.11.0：LLM-assisted Spec Refinement
- v0.12.0：Apply Preview
- v0.13.0：Apply Plan Export
- v0.14.0：Apply from Plan
- v0.15.0：Apply Rollback
- v0.16.0：Apply History / Workspace Journal

暂不包含：

- 真实 ROS/ROS2 运行
- catkin_make 或 colcon 执行
- launch 文件执行
- 生成代码执行
- LLM 直接写文件或代码
- RAG、Streamlit、Gradio、VSCode 扩展

## 开发说明

运行测试：

```bash
python -m pytest
```

Windows 临时目录权限受限时：

```powershell
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

生成项目默认写入 `outputs/`，该目录已被 Git 忽略。示例项目位于 `examples/`。

## License

MIT License.
