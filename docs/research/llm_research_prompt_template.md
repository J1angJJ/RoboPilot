# LLM Research Prompt Template

Use this prompt with an LLM that has web access when product research is needed. Do not use it as an implementation prompt.

```txt
You are researching future RoboPilot 2.x feature planning.

Project positioning:
RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects and ROS1-to-ROS2 migration scaffolds. It helps users inspect, analyze, plan, scaffold, validate, and report migration work without requiring ROS, ROS2, catkin, colcon, launch execution, or generated node execution.

Safety constraints:
- Do not recommend features that require ROS runtime execution.
- Do not recommend ROS2 runtime execution.
- Do not recommend running catkin_make.
- Do not recommend running colcon.
- Do not recommend executing launch files.
- Do not recommend executing generated nodes.
- Do not recommend automatic migration apply or automatic source patching for 2.x.
- Do not recommend automatic business logic conversion for 2.x.
- Prefer static analysis, report guidance, documentation, and review-first workflows.
- Keep the VSCode extension as a thin wrapper over RoboPilot CLI/API/JSON contracts.

Research topic:
<insert topic, such as ROS1-to-ROS2 QoS migration pain points, launch XML migration, tf to tf2, dynamic_reconfigure, actionlib, nodelet, interface generation, distro/profile hints, or workspace-level static analysis>

Required output:
1. Summary
2. User types affected
3. Repeated pain points
4. Evidence notes with source categories and citations where available
5. What is evidence vs. speculation
6. Static-analysis-friendly opportunities
7. Report/documentation opportunities
8. VSCode workflow opportunities
9. Candidate features classified as small / medium / large
10. Non-goals and risks
11. Suggested evidence confidence level from 1 to 5
12. Recommended next RoboPilot research brief decision: proposed / accepted / deferred / rejected

Important:
Distinguish official guidance from community anecdotes. Prefer conservative, review-first recommendations. Do not invent capabilities RoboPilot does not have.
```

