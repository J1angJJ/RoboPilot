# ROS2 Scaffold Demo

This directory is a static example of a conservative ROS2 migration scaffold for `examples/ros1_migration_demo`.

It is scaffold-only. It is not runtime-validated, not build-validated, and not a complete ROS1-to-ROS2 migration.

RoboPilot did not run ROS, ROS2, `catkin_make`, `colcon`, launch files, generated nodes, or generated code to create this example.

This checked-in demo is intentionally a little more illustrative than the minimal `mixed_review_required` scaffold that RoboPilot may generate for a mixed Python/C++ ROS1 package. The generated scaffold remains the source of truth for command behavior; this directory is for reading and tutorial context.

Use it to understand the shape of a migration scaffold and the kind of TODO/manual review notes RoboPilot expects:

```bash
robopilot inspect-ros2 examples/ros2_scaffold_demo
```

For the full tutorial, see:

```txt
docs/tutorial_ros1_to_ros2_migration.md
```
