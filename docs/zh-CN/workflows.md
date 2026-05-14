# RoboPilot 主要工作流

RoboPilot 的默认工作流都不需要 ROS、ROS2、`catkin_make`、`colcon`、仿真器或机器人硬件。

## Spec-first 生成

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --output robopilot.yaml
robopilot validate --spec robopilot.yaml
robopilot generate --spec robopilot.yaml
```

`ProjectSpec` 是可审查的中间表示。先 validate，再 generate。

## 安全 apply / rollback

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
robopilot apply-plan-validate --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml
robopilot apply --plan apply_plan.yaml --confirm
robopilot history --project outputs/demo_detector
```

`apply` 默认是 dry-run，只有显式 `--confirm` 才写文件。

## 静态分析

```bash
robopilot detect path/to/project
robopilot inspect-ros1 path/to/ros1_package
robopilot inspect-ros2 path/to/ros2_package
robopilot deps path/to/project
```

这些命令只读取文件，不执行用户代码。

## ROS1 到 ROS2 迁移辅助

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
robopilot migrate-plan-validate --plan migration_plan.yaml
robopilot migrate-scaffold-preview --plan migration_plan.yaml
robopilot migrate-scaffold --plan migration_plan.yaml --output path/to/ros2_scaffold
robopilot migrate-scaffold-validate --plan migration_plan.yaml --scaffold path/to/ros2_scaffold
robopilot migrate-scaffold-report --plan migration_plan.yaml --scaffold path/to/ros2_scaffold --output scaffold_report.md
```

这是一条静态 review loop。它不会修改源 ROS1 项目，也不会自动迁移业务逻辑。v2.0.0-rc.1 期间已经进入 feature freeze；除 release-blocking 修复外，不应新增命令、migration apply、自动源码转换或 ROS/ROS2 runtime 执行。

详细教程见 [ROS1 到 ROS2 迁移脚手架教程](tutorial_ros1_to_ros2_migration.md)。

## VSCode 辅助流程

```txt
RoboPilot: Generate Migration Plan
  -> RoboPilot: Preview Migration Scaffold
  -> RoboPilot: Generate Migration Scaffold
  -> RoboPilot: Validate Migration Scaffold
  -> RoboPilot: Generate Scaffold Report
  -> RoboPilot: Open Scaffold Report
```

扩展默认把产物写入 `.robopilot_vscode/`。详细说明见 [VSCode 辅助迁移教程](tutorial_vscode_migration_workflow.md)。
