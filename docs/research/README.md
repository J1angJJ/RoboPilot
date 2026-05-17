# Research Planning

This folder is for RoboPilot product and user-need research before larger 2.x work starts.

RoboPilot should remain a no-ROS-required static engineering toolchain for ROS-style projects and ROS1-to-ROS2 migration scaffolds. Research briefs help separate real user pain points from tempting but risky feature ideas.

## How To Use Research Briefs

1. Capture evidence in a research brief before implementing broad features.
2. Separate observed pain points from proposed RoboPilot behavior.
3. Classify each idea by safety and fit.
4. Mark the decision status before implementation begins.
5. Implement only accepted, scoped items.

Research briefs are planning inputs, not product specs by default. A feature should be treated as ready for implementation only when it is marked `accepted` and has a clear scope.

## Evidence Collection

Useful evidence can come from:

- official ROS / ROS2 migration guides
- package documentation
- repeated issue reports or forum posts
- repeated classroom or team questions
- RoboPilot author's own robotics projects
- direct user feedback

Record the source category and enough notes for a future maintainer to understand why the issue matters. Do not overfit RoboPilot to a single anecdote unless the change is tiny and safe.

## Scope Classification

Classify candidate work as one or more of:

- `static analysis suitable`: can be done by reading files without executing code
- `report/documentation suitable`: best handled as guidance, report wording, tutorials, or warnings
- `VSCode workflow suitable`: useful as command grouping, output display, TreeView state, or docs links
- `runtime / out of scope`: would require ROS, ROS2, catkin, colcon, launch execution, or generated code execution
- `future / experimental`: interesting but not ready for implementation

## Evidence Confidence

- Level 1: single anecdote
- Level 2: repeated posts/issues
- Level 3: official docs or migration guides mention it
- Level 4: observed in RoboPilot author's own robotics projects
- Level 5: validated by real users / classmates / teams

Prioritize Level 3-5 evidence for implementation. Level 1-2 evidence can justify documentation, watchlist items, or small low-risk experiments.

## Safety Boundary

Research should not turn RoboPilot into a runtime ROS automation tool. For 2.x, avoid:

- automatic migration apply
- automatic ROS1-to-ROS2 business logic conversion
- source patching without explicit reviewed plans
- running ROS, ROS2, `catkin_make`, `colcon`, launch files, or generated nodes
- moving core logic into the VSCode extension

