# LLM Research Prompt Template

Use this prompt with an LLM that has web access when product research is needed. Do not use it as an implementation prompt.

```txt
You are researching future RoboPilot 2.x feature planning.

Project positioning:
RoboPilot is a no-ROS-required static engineering toolchain for ROS-style projects and ROS1-to-ROS2 migration scaffolds.

It helps users inspect, analyze, plan, scaffold, validate, and report migration work without requiring ROS, ROS2, catkin, colcon, launch execution, or generated node execution.

GitHub:
https://github.com/J1angJJ/RoboPilot

RoboPilot's current capabilities include:
- static ROS-style project detection
- ROS1 static inspection
- ROS2 static inspection
- static dependency analysis
- ROS1-to-ROS2 migration planning
- migration scaffold preview / generate / validate / report
- Python API layer
- JSON contracts
- VSCode Marketplace extension
- English and Chinese documentation
- examples and tutorials

Safety constraints:
- Do not recommend features that require ROS runtime execution.
- Do not recommend ROS2 runtime execution.
- Do not recommend running catkin_make.
- Do not recommend running colcon.
- Do not recommend executing launch files.
- Do not recommend executing generated nodes.
- Do not recommend automatic migration apply or automatic source patching for RoboPilot 2.x.
- Do not recommend automatic business logic conversion for RoboPilot 2.x.
- Prefer static analysis, report guidance, documentation, scaffold placeholders, and review-first workflows.
- Keep the VSCode extension as a thin wrapper over RoboPilot CLI/API/JSON contracts.
- Do not invent capabilities RoboPilot does not currently have.

Research topic:
<insert topic, such as ROS1-to-ROS2 QoS migration pain points, launch XML migration, tf to tf2, dynamic_reconfigure, actionlib, nodelet, interface generation, distro/profile hints, workspace-level static analysis, package.xml/CMakeLists migration, or VSCode robotics workflow pain points>

Research source preferences:
- Prefer official ROS / ROS 2 documentation when available.
- Use GitHub issues, ROS Discourse, Robotics StackExchange, Stack Overflow, migration guides, and real project discussions as supporting evidence.
- Distinguish official guidance from community anecdotes.
- Prefer repeated pain points over isolated one-off complaints.
- Include citations / links where available.
- If evidence is weak or speculative, say so clearly.

Required output format:
Produce a structured Markdown research brief suitable to save under docs/research/.

Use this structure:

# Research Brief: <topic>

## 1. Summary

Briefly summarize the main findings.

## 2. User types affected

Identify likely user groups, such as:
- ROS1 legacy project maintainers
- ROS2 beginners
- robotics students / competition teams
- lab users migrating old projects
- Windows + VSCode users
- developers without a working ROS/ROS2 runtime environment

## 3. Repeated pain points

List repeated pain points.
For each pain point, include:
- problem summary
- why it matters
- whether it appears in official docs, community discussions, GitHub issues, or personal/project experience
- whether it is repeated or only anecdotal

## 4. Evidence notes

For each important evidence item, include:
- source category: official docs / GitHub issue / forum / Q&A / tutorial / anecdote
- source link or citation where available
- what the source actually supports
- whether the interpretation is evidence or speculation

## 5. Evidence vs. speculation

Clearly separate:
- evidence-backed conclusions
- reasonable inferences
- weak speculation
- unknowns

## 6. Static-analysis-friendly opportunities

Identify opportunities RoboPilot can address without running ROS/ROS2.
Examples:
- detecting files or patterns
- checking package.xml / CMakeLists.txt / setup.py / launch files
- detecting dependency hints
- generating warnings
- producing report sections
- generating scaffold TODO placeholders
- producing migration checklists

## 7. Report / documentation opportunities

Identify improvements for:
- scaffold reports
- MIGRATION_NOTES.md
- tutorials
- troubleshooting docs
- known limitations
- review checklists

## 8. VSCode workflow opportunities

Identify safe improvements for the VSCode extension, such as:
- clearer warnings
- opening report files
- showing next steps
- TreeView state
- docs links
- output summaries

Do not recommend complex Webview UI unless strongly justified.

## 9. Candidate RoboPilot features

Classify candidate features as:

### Small
Low-risk changes, usually docs, warnings, report hints, static checks, or small JSON additions.

### Medium
Focused static-analysis improvements or workflow improvements requiring tests and docs.

### Large
Substantial features that may require design review, new modules, or staged implementation.

For each feature, include:
- description
- expected user value
- implementation scope
- required tests
- whether it affects JSON contracts
- whether it affects VSCode extension
- risk level

## 10. Non-goals and risks

List things RoboPilot should not do for this topic in 2.x.
Examples:
- automatic source conversion
- migration apply
- runtime validation
- colcon execution
- launch execution
- claiming generated scaffold is runtime-correct

## 11. Evidence confidence level

Assign a confidence level:

- Level 1: single anecdote
- Level 2: repeated community posts/issues
- Level 3: official docs or migration guides mention it
- Level 4: also observed in RoboPilot author's own robotics projects
- Level 5: validated by real users / classmates / teams

Explain the assigned level.

## 12. Recommended RoboPilot decision

Choose one:
- proposed
- accepted
- deferred
- rejected

Also suggest a likely milestone:
- v2.1 candidate
- v2.2 candidate
- v2.3 candidate
- later 2.x
- future / 3.x

## 13. Suggested next Codex task

If this research should become implementation work, propose one small, scoped Codex task.
The task should:
- preserve no-ROS-required behavior
- avoid broad rewrites
- include tests
- update docs
- avoid runtime execution
- avoid automatic source conversion

Important:
Be conservative and review-first. Do not recommend turning RoboPilot into a full automatic migration agent. Focus on what can be statically detected, clearly explained, scaffolded, validated, or documented.

After completing the main research brief, also output a separate Chinese maintainer summary outside the Markdown brief:

# 中文简要分类摘要

请用中文简要说明：

- 主题：一句话概括本次调研主题
- 痛点分类：例如 migration hints / dependency analysis / workspace analysis / VSCode workflow / scaffold quality / LLM explanation / future 3.x
- RoboPilot 适合做的部分：列 2-4 条
- RoboPilot 2.x 不适合做的部分：列 1-3 条
- 建议路线：v2.1 / v2.2 / v2.3 / v2.4 / v2.5 / v2.6 / later 2.x / future 3.x
- 优先级：高 / 中 / 低
- 建议状态：proposed / accepted / deferred / rejected
- 分类理由：用 1-2 句话解释为什么这么分

This Chinese summary is only for quick maintainer triage. Keep it concise and do not duplicate the full research brief.
```
