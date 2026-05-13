# RoboPilot Migration Scaffold Report

## Summary

- Valid: true
- Issues: 0
- Warnings: 3
- Migration notes present: true

## Source and Target

- Plan path: examples/migration_outputs/migration_plan.yaml
- Scaffold path: examples/ros2_scaffold_demo
- Source path: examples/ros1_migration_demo
- Target: ros2

## Package

- Package name: ros1_migration_demo

## Target Style

- Target style: mixed_review_required

## Validation Result

- Valid: true
- Migration notes present: true

## Expected Files

- MIGRATION_NOTES.md
- config/params.yaml
- launch/demo.launch.py
- package.xml

## Present Files

- MIGRATION_NOTES.md
- config/params.yaml
- launch/demo.launch.py
- package.xml

## Missing Files

- No missing files.

## Unexpected Files

- No unexpected files in the generated minimal scaffold.
- The checked-in `examples/ros2_scaffold_demo/` directory intentionally includes extra illustrative source and interface placeholders for tutorial reading.

## Placeholder Checks

- MIGRATION_NOTES.md: passed; missing concepts: none
- config/params.yaml: passed; missing concepts: none
- launch/demo.launch.py: passed; missing concepts: none

## ROS2 Static Inspection Summary

- Exists: true
- Package name: ros1_migration_demo
- Detected project type: unknown
- Build system: ament_cmake=false, ament_package=false, ament_python=false, resource_marker=false, setup_cfg=false, setup_py=false
- Launch files: launch/demo.launch.py
- Config files: config/params.yaml
- Python node candidates: none
- C++ node candidates: none
- ROS2 inspection issues: detector classified this project as unknown; ROS2 structure may be partial, unknown or partial ROS2 project structure, no obvious ROS2 node files detected

## Manual Migration Items

- CMakeLists.txt
- launch/demo.launch
- scripts/talker.py
- src/listener.cpp

## Interface Files to Review

- action/Demo.action
- msg/Demo.msg
- srv/Demo.srv

## Dependency Items to Review

- ros2_equivalent_hints: message_generation -> rosidl_default_generators
- ros2_equivalent_hints: message_runtime -> rosidl_default_runtime
- ros2_equivalent_hints: roscpp -> rclcpp
- ros2_equivalent_hints: rospy -> rclpy
- ros2_equivalent_hints: std_msgs -> check ROS2 package availability and API differences

## Issues

- No validation issues.

## Warnings

- ros2_inspection: detector classified this project as unknown; ROS2 structure may be partial
- ros2_inspection: no obvious ROS2 node files detected
- ros2_inspection: unknown or partial ROS2 project structure

## Suggested Next Steps

- Review MIGRATION_NOTES.md before manual migration work.
- Run robopilot inspect-ros2 on the scaffold after manual edits.
- Run robopilot deps on the scaffold after adding real ROS2 dependencies.
- Review unexpected files and ROS2 inspection warnings before treating the scaffold as ready.

## Safety Note

This report is generated from static validation only. RoboPilot did not run ROS. RoboPilot did not run ROS2. RoboPilot did not run catkin_make. RoboPilot did not run colcon. RoboPilot did not execute launch files. RoboPilot did not execute generated code or import generated scaffold modules. Passing validation does not mean the scaffold builds, launches, or behaves correctly at runtime.
