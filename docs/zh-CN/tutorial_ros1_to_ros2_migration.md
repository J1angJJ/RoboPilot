# 教程：ROS1 到 ROS2 迁移脚手架工作流

本教程使用仓库内的 `examples/ros1_migration_demo/` 演示 RoboPilot 的静态迁移辅助流程。

不需要安装 ROS 或 ROS2。RoboPilot 不会运行 `catkin_make`、`colcon`、launch 文件或生成的节点代码。

## 准备

安装 RoboPilot：

```bash
pip install robopilot
```

如果你在源码仓库中开发：

```bash
python -m pip install -e ".[dev]"
```

确认命令可用：

```bash
robopilot --help
```

## 示例项目

示例 ROS1 风格 package 位于：

```txt
examples/ros1_migration_demo/
```

它包含 `package.xml`、`CMakeLists.txt`、launch、Python、C++、msg、srv 和 action 文件。这个示例只用于静态分析，不是生产级 ROS package。

## 1. 检测项目类型

```bash
robopilot detect examples/ros1_migration_demo
```

期望结果是 RoboPilot 将目录识别为 ROS1 catkin 风格 package。

## 2. 静态检查 ROS1 结构

```bash
robopilot inspect-ros1 examples/ros1_migration_demo
```

这个命令只读取文件内容，静态分析 package metadata、launch 文件、接口文件、Python 文件和 C++ 文件。

## 3. 分析依赖

```bash
robopilot deps examples/ros1_migration_demo
```

重点查看声明依赖、检测到的 import/include，以及 ROS1 到 ROS2 的依赖迁移提示。

## 4. 生成 migration plan

```bash
robopilot migrate-plan --from examples/ros1_migration_demo --to ros2 --output .pytest_tmp_v116_manual/migration_plan.yaml
```

`migration_plan.yaml` 是一个可审查的计划文件。它不会修改源项目。

## 5. 验证 migration plan

```bash
robopilot migrate-plan-validate --plan .pytest_tmp_v116_manual/migration_plan.yaml
```

验证通过只表示计划结构符合 RoboPilot 的静态要求，不表示迁移已经完成。

## 6. 预览 ROS2 scaffold

```bash
robopilot migrate-scaffold-preview --plan .pytest_tmp_v116_manual/migration_plan.yaml
```

这个命令是只读的。它会显示目标 scaffold 风格、预计创建的文件、placeholder、风险、冲突和下一步建议。

## 7. 生成 ROS2 scaffold

```bash
robopilot migrate-scaffold --plan .pytest_tmp_v116_manual/migration_plan.yaml --output .pytest_tmp_v116_manual/ros2_scaffold
```

生成结果是保守的 ROS2 scaffold。它只写入显式指定的 `--output` 目录，默认不会覆盖已有文件。

这不是完整自动迁移。业务逻辑、QoS、参数、生命周期、launch 行为、接口和依赖仍然需要人工审查。

## 8. 验证 scaffold

```bash
robopilot migrate-scaffold-validate --plan .pytest_tmp_v116_manual/migration_plan.yaml --scaffold .pytest_tmp_v116_manual/ros2_scaffold
```

验证会检查预期文件、`MIGRATION_NOTES.md`、placeholder 安全提示、静态 ROS2 检查摘要、issues、warnings 和下一步建议。RoboPilot 不会 import 或执行 scaffold 中的代码。

## 9. 导出 scaffold report

```bash
robopilot migrate-scaffold-report --plan .pytest_tmp_v116_manual/migration_plan.yaml --scaffold .pytest_tmp_v116_manual/ros2_scaffold --output .pytest_tmp_v116_manual/scaffold_report.md
```

如果省略 `--output`，报告会打印到终端。建议优先阅读：

- `Summary`
- `Validation Result`
- `What To Do Next`
- `Manual Migration Items`
- `Safety Note`

## 常见产物

- `.pytest_tmp_v116_manual/migration_plan.yaml`
- `.pytest_tmp_v116_manual/ros2_scaffold/`
- `.pytest_tmp_v116_manual/scaffold_report.md`

仓库中也包含示例产物：

- `examples/migration_outputs/`
- `examples/ros2_scaffold_demo/`

## 迁移边界

RoboPilot 可以帮助你把迁移工作拆成可审查的计划、scaffold、验证结果和报告。它不会自动迁移业务逻辑，也不会证明 ROS2 package 能 build、launch 或正常运行。

完成人工迁移后，请在你自己的 ROS2 环境中使用真实 ROS2 工具验证。
