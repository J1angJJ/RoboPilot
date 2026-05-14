# 演示讲稿

这个页面适合用来做一个简短的 RoboPilot 演示，重点展示不安装 ROS 也能完成静态迁移辅助流程。

## 5 分钟 CLI 演示

从静态 ROS1 示例项目开始：

```bash
robopilot detect examples/ros1_migration_demo
robopilot inspect-ros1 examples/ros1_migration_demo
robopilot deps examples/ros1_migration_demo
```

讲解要点：

- RoboPilot 只读取文件，不运行 ROS。
- 依赖提示是静态、保守的。
- 示例 package 很小，只用于演示。

生成并审查迁移产物：

```bash
robopilot migrate-plan --from examples/ros1_migration_demo --to ros2 --output .pytest_tmp_v116_manual/migration_plan.yaml
robopilot migrate-plan-validate --plan .pytest_tmp_v116_manual/migration_plan.yaml
robopilot migrate-scaffold-preview --plan .pytest_tmp_v116_manual/migration_plan.yaml
robopilot migrate-scaffold --plan .pytest_tmp_v116_manual/migration_plan.yaml --output .pytest_tmp_v116_manual/ros2_scaffold
robopilot migrate-scaffold-validate --plan .pytest_tmp_v116_manual/migration_plan.yaml --scaffold .pytest_tmp_v116_manual/ros2_scaffold
robopilot migrate-scaffold-report --plan .pytest_tmp_v116_manual/migration_plan.yaml --scaffold .pytest_tmp_v116_manual/ros2_scaffold --output .pytest_tmp_v116_manual/scaffold_report.md
```

预期产物：

- `.pytest_tmp_v116_manual/migration_plan.yaml`
- `.pytest_tmp_v116_manual/ros2_scaffold/`
- `.pytest_tmp_v116_manual/scaffold_report.md`

安全提醒：

- 源项目不会被修改。
- scaffold 只写入显式 output 目录。
- RoboPilot 不运行 ROS、ROS2、`catkin_make`、`colcon`、launch 文件或生成代码。
- scaffold validation 不是 runtime validation。

## 5 分钟 VSCode 演示

打开仓库后，在 Command Palette 中运行：

```txt
RoboPilot: Detect Workspace
RoboPilot: Generate Migration Plan
RoboPilot: Preview Migration Scaffold
RoboPilot: Generate Migration Scaffold
RoboPilot: Validate Migration Scaffold
RoboPilot: Generate Scaffold Report
RoboPilot: Open Scaffold Report
```

讲解要点：

- VSCode extension 是 CLI 的薄包装。
- 产物默认写入 `.robopilot_vscode/`。
- OutputChannel 是主要审查界面。
- 用户仍然需要人工处理 ROS2 业务逻辑、QoS、依赖和 launch 细节。

## 结尾

一句话总结：RoboPilot 帮你规划、生成 scaffold、验证和报告迁移工作，但不会自动移植或运行 ROS 项目。
