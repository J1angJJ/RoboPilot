# Codex Implementation Prompt Template

Use this after a research brief has been accepted and a small implementation scope is selected.

```txt
Please implement the accepted RoboPilot research brief:

Brief:
<path to docs/research/...>

Selected scoped item:
<one small accepted item>

Important:
- Do not browse the web for additional broad product requirements.
- Do not expand scope beyond the accepted brief without explicit approval.
- Do not add ROS runtime execution.
- Do not add ROS2 runtime execution.
- Do not run catkin_make.
- Do not run colcon.
- Do not execute launch files.
- Do not execute generated nodes.
- Do not add automatic migration apply.
- Do not add automatic source conversion.
- Do not move core logic into the VSCode extension.
- Preserve stable CLI behavior and documented JSON contracts.
- Prefer small, testable, documented improvements.

Implementation expectations:
1. Read AGENTS.md, roadmap.md, CHANGELOG.md, the accepted research brief, and relevant docs.
2. Inspect existing modules before editing.
3. Implement only the selected scoped item.
4. Add or update focused tests.
5. Update docs and CHANGELOG.md.
6. Run targeted tests and full checks appropriate to the change.
7. Summarize changed files, behavior, tests, and any remaining risks.

Do not commit, tag, push, publish to PyPI, or publish to VSCode Marketplace unless explicitly asked.
```

