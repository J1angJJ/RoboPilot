# ROS1 Migration Demo

This is a tiny ROS1-style catkin package for RoboPilot tutorials.

It is intentionally small and illustrative. It is not a production ROS package, and the tutorial does not require ROS, `catkin_make`, launch execution, or node execution.

RoboPilot uses this directory for static inspection and migration planning examples:

```bash
robopilot detect examples/ros1_migration_demo
robopilot inspect-ros1 examples/ros1_migration_demo
robopilot deps examples/ros1_migration_demo
```

The package includes:

- `package.xml`
- `CMakeLists.txt`
- `launch/demo.launch`
- `scripts/talker.py` with `rospy`
- `src/listener.cpp` with `roscpp`
- `msg/Demo.msg`
- `srv/Demo.srv`
- `action/Demo.action`

RoboPilot should treat this as static input only. Passing static inspection does not mean this package builds or runs in ROS.
