# 已知限制

RoboPilot 是静态工程工具链，不替代真实 ROS 或 ROS2 运行环境。

当前限制：

- 不做 ROS runtime validation。
- 不做 ROS2 runtime validation。
- 不运行 `catkin_make`。
- 不运行 `colcon`。
- 不执行 launch 文件。
- 不执行生成节点。
- 依赖推断可能不完整。
- CMake 解析是保守的字符串/正则分析。
- launch 解析只覆盖简单静态引用。
- 项目类型检测是启发式的。
- ROS1 到 ROS2 migration plan 是 advisory。
- migration preview 不生成已迁移业务代码。
- migration apply 未实现。
- scaffold validation 不是 build 或 runtime validation。
- LLM 输出即使通过验证，也可能不完整或不正确。
- VSCode extension 可以源码使用和本地 VSIX 打包，但 Marketplace 是否可用取决于未来明确发布。

这些限制是安全模型的一部分。RoboPilot 的目标是帮助用户审查结构和计划，再由用户在真实 ROS/ROS2 环境中完成运行时验证。
