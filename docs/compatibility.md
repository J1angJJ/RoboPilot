# Compatibility

RoboPilot is designed to be lightweight, static, and no-ROS-required.

## Python Versions

Supported and tested in CI:

- Python 3.10
- Python 3.11

RoboPilot may work on newer Python versions, but support should be confirmed with the test suite before release claims are updated.

## Operating Systems

Expected to work on:

- Windows
- Linux
- macOS

Current development and manual checks include Windows. CI runs on Ubuntu. Path handling uses `pathlib` to keep behavior portable.

## ROS Runtime Compatibility

RoboPilot does not require:

- ROS
- ROS2
- catkin
- colcon
- robot hardware
- simulator runtimes

Generated files are ROS-style skeletons and pseudocode where runtime dependencies are unavailable.

## Supported Project Categories

Static detection supports these categories:

- RoboPilot-generated project
- ROS1 catkin package
- ROS2 ament Python package detection
- ROS2 ament C++ package detection
- mixed ROS-style project
- non-ROS project
- unknown project

## Best-Effort Areas

The following areas are heuristic and conservative:

- project type detection
- dependency inference
- CMake parsing
- launch file package reference detection
- ROS1-to-ROS2 migration planning
- migration preview classifications

RoboPilot should report uncertainty instead of pretending static analysis is runtime validation.

## Compatibility Boundaries

RoboPilot does not validate:

- whether a ROS package builds
- whether launch files run
- whether generated nodes execute
- whether migrated code is runtime-correct
- whether dependencies are installed in a real ROS environment
