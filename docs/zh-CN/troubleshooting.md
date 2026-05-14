# 常见问题排查

RoboPilot 默认不需要 ROS、ROS2、`catkin_make`、`colcon`、launch 执行、生成节点执行或机器人硬件。

## 找不到 `robopilot` 命令

先在当前 Python 环境安装：

```bash
pip install robopilot
```

源码开发时使用：

```bash
python -m pip install -e ".[dev]"
```

然后检查：

```bash
robopilot --help
```

如果机器上有多个 Python，检查安装位置：

```bash
python -m pip show robopilot
```

## Python 版本支持

当前声明支持 Python 3.10 和 3.11。包元数据为：

```txt
>=3.10,<3.12
```

Python 3.12 暂不声明支持。Python 3.13 暂不支持。

## VSCode 找不到 RoboPilot

VSCode 可能没有继承你的 shell 或 conda PATH。

可以尝试：

- 从已激活 conda 环境的终端启动 VSCode。
- 设置 `robopilot.executablePath` 为 `robopilot` 可执行文件的完整路径。
- 在 Windows 上用同一个终端 profile 检查路径。

conda 示例：

```powershell
conda activate robopilot
where robopilot
```

把输出路径填入 `robopilot.executablePath`。

## Windows PowerShell / CMD 编码或 mojibake

某些 Windows PowerShell 或 CMD 会把 Rich 表格边框、中文或符号显示成 mojibake。这通常是显示问题，JSON 输出和写入的 Markdown 文件仍然有效。

可以尝试：

```powershell
$env:PYTHONIOENCODING='utf-8'
robopilot --help
```

也可以使用 Windows Terminal 或 PowerShell 7。

自动化场景建议优先使用支持的 `--json` 输出，不要解析 Rich 人类可读输出。

## `.pytest_tmp` 访问被拒绝

Windows 上如果 pytest 无法访问默认临时目录，可以使用仓库内临时目录：

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

如果旧目录被占用，换一个新名字：

```bash
python -m pytest --basetemp=".pytest_tmp_v2" -p no:cacheprovider
```

删除临时目录前，先关闭可能占用文件的编辑器或终端。

## scaffold 输出冲突

`migrate-scaffold` 默认拒绝覆盖已有文件。

建议使用新的输出目录：

```bash
robopilot migrate-scaffold --plan migration_plan.yaml --output .pytest_tmp_v116_manual/ros2_scaffold
```

只有在审查过目标目录后，才使用：

```bash
robopilot migrate-scaffold --plan migration_plan.yaml --output .pytest_tmp_v116_manual/ros2_scaffold --overwrite
```

RoboPilot 只覆盖预期 scaffold 文件，不会任意修改源项目。

## VSCode 缺少 `migration_plan.json`

先运行：

```txt
RoboPilot: Generate Migration Plan
```

默认路径是：

```txt
.robopilot_vscode/migration_plan.json
```

## VSCode 缺少 `.robopilot_vscode/ros2_scaffold`

先运行：

```txt
RoboPilot: Generate Migration Scaffold
```

然后再运行：

```txt
RoboPilot: Validate Migration Scaffold
RoboPilot: Generate Scaffold Report
```

## 缺少 `scaffold_report.md`

先运行：

```txt
RoboPilot: Generate Scaffold Report
```

默认报告路径是：

```txt
.robopilot_vscode/scaffold_report.md
```

## 不需要 ROS / ROS2

RoboPilot 的迁移工作流是静态辅助。它可以帮助你 plan、scaffold、validate 和 report，但不会证明 ROS2 运行时正确性。

完成人工迁移后，请在真实 ROS2 环境中进行 build、launch 和运行测试。
