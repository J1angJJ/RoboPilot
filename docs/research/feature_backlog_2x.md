# RoboPilot 2.x Feature Backlog

This backlog is a planning input, not a product commitment. Items should move toward implementation only after research briefs are accepted and scope is narrowed.

## Accepted

- None yet. Accepted items should reference a research brief and a decision-log entry.

## Candidate

- Research-backed migration hints for common ROS1-to-ROS2 pain points:
  - launch XML review
  - parameter migration review
  - QoS review
  - `tf` / `tf2`
  - `dynamic_reconfigure`
  - `actionlib`
  - `nodelet`
  - interface generation
- ROS distro / profile hints for common ecosystems such as Noetic, Humble, Jazzy, or other relevant distros.
- Workspace-level static analysis for catkin-style and colcon-style source workspaces.
- VSCode extension UX polish:
  - clearer TreeView grouping
  - command discoverability
  - report opening
  - documentation links
  - clearer warnings
- Scaffold quality upgrades:
  - better TODO comments
  - clearer `package.xml`, `setup.py`, `CMakeLists.txt` placeholders
  - better launch placeholders
  - improved `params.yaml`
  - richer `MIGRATION_NOTES.md`
- Optional LLM explanation layer for reports, risks, dependency hints, and review checklists.

## Deferred

- Complex VSCode Webview UI unless a future brief shows strong need and a low-risk scope.
- Large API refactors unless required for a focused accepted feature.
- New package manager or distro metadata models until profile-hint research is accepted.

## Rejected / Non-goals

These are rejected for 2.x unless explicitly revisited:

- automatic full ROS1-to-ROS2 source conversion
- migration apply / patching source projects
- running `colcon`
- running `catkin_make`
- runtime launch validation
- executing generated nodes
- requiring ROS or ROS2 for default workflows
- moving RoboPilot core logic into the VSCode extension

## Needs Research

- Which ROS1-to-ROS2 migration warnings are most useful to beginners?
- Which distro/profile hints can be expressed statically without pretending to validate environments?
- How should workspace-level package graphs handle incomplete or mixed workspaces?
- Which VSCode workflow friction points appear repeatedly for users?
- Which scaffold placeholders most reduce manual migration confusion?
- Whether LLM explanations provide enough value without creating trust or safety risks.

