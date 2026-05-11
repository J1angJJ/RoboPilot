
# Roadmap

RoboPilot is developed as a no-ROS-required static engineering toolchain for ROS-style projects.

The project started as a lightweight ROS-style project generator, but its long-term direction is now clearer:

```txt
RoboPilot should help users plan, inspect, update, analyze, and migrate ROS/ROS2-style projects without requiring a local ROS installation.
```

RoboPilot is not intended to compete directly with general-purpose coding agents or runtime ROS automation tools. Its niche is:

- static project structure analysis
- ProjectSpec-based planning
- safe file update workflows
- ROS1 / ROS2 project inspection
- dependency analysis
- ROS1-to-ROS2 migration assistance
- optional LLM-assisted spec workflows

## Core Design Direction

RoboPilot follows a spec-first and safety-first architecture:

```txt
natural language task
        ↓
planner
        ↓
ProjectSpec
        ↓
refine
        ↓
diff
        ↓
validate
        ↓
apply-preview
        ↓
apply-plan
        ↓
apply
        ↓
rollback
        ↓
inspect
        ↓
repair-suggest
        ↓
report
```

The long-term goal is to evolve RoboPilot into a practical static engineering assistant for ROS/ROS2 projects.

The default workflow should remain offline, deterministic, testable, and usable without ROS, ROS2, catkin, colcon, robot hardware, or simulator runtime.

## Completed: v0.1.0 Basic Offline MVP

Status: Completed

Goal:

Build the first runnable offline MVP.

Completed features:

- Offline ROS-style package generator
- Robotics error log debugger
- Pipeline-to-Mermaid workflow graph generator
- English README
- Chinese README
- Demo script
- Static generated example project
- Pytest tests
- GitHub Actions CI
- GitHub Release

Core commands:

```bash
robopilot generate --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes."
```

```bash
robopilot debug --log examples/error_logs/cv_bridge_missing.txt
```

```bash
robopilot graph --pipeline "camera -> detector -> tracker -> planner -> controller"
```

## Completed: v0.2.0 Prompt-driven Template Selection

Status: Completed

Goal:

Upgrade the generator from a fixed template generator to a prompt-driven template selection system.

Completed features:

- Rule-based task classifier
- Multiple ROS-style generation templates
- Template registry
- `ProjectSpec` intermediate structure
- Generated `robopilot.yaml` metadata
- Refreshed static generated demo project
- Expanded tests
- Updated documentation

Supported template types:

- `camera_subscriber`
- `object_detection`
- `velocity_controller`
- `perception_pipeline`
- `generic_node`

Example commands:

```bash
robopilot generate --name camera_reader --task "Create a camera subscriber for webcam frames."
```

```bash
robopilot generate --name base_controller --task "Create a velocity controller publishing cmd_vel motion commands."
```

```bash
robopilot generate --name perception_stack --task "Create a camera -> detector -> tracker perception workflow."
```

## Completed: v0.3.0 Spec-first Generation

Status: Completed

Goal:

Upgrade RoboPilot from prompt-driven direct generation into a spec-first generation workflow.

Completed features:

- `robopilot plan`
- `robopilot validate`
- `robopilot generate --spec`
- Spec serialization and loading
- Spec validation before generation
- Generation from `robopilot.yaml`
- Backward compatibility with `generate --name --task`
- Expanded tests
- Updated documentation

Core workflow:

```bash
robopilot plan --name demo_detector --task "Create an object detection node subscribing to camera images and publishing bounding boxes." --output robopilot.yaml
```

```bash
robopilot validate --spec robopilot.yaml
```

```bash
robopilot generate --spec robopilot.yaml
```

## Completed: v0.4.0 Project Inspector

Status: Completed

Goal:

Add a lightweight offline project inspector that analyzes existing RoboPilot-generated or ROS-style project directories.

Completed features:

- `robopilot inspect`
- Static project directory inspection
- Optional JSON output
- Detection of missing project files
- Detection of missing or invalid `robopilot.yaml`
- Reuse of existing spec loader and validator
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot inspect examples/generated_projects/demo_detector
```

```bash
robopilot inspect examples/generated_projects/demo_detector --json
```

## Completed: v0.5.0 Project Repair Suggestions

Status: Completed

Goal:

Use project inspection results to generate read-only repair suggestions.

Completed features:

- `robopilot repair-suggest`
- Optional JSON output
- Read-only repair suggestion layer
- Deterministic mapping from inspection issues to repair suggestions
- Suggested follow-up commands
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot repair-suggest examples/generated_projects/demo_detector
```

```bash
robopilot repair-suggest examples/generated_projects/demo_detector --json
```

## Completed: v0.6.0 Project Report Export

Status: Completed

Goal:

Combine project inspection and repair suggestions into a Markdown report.

Completed features:

- `robopilot report`
- Terminal Markdown report output
- Markdown report file export
- Reuse of inspector and repair suggester
- Deterministic report sections
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot report examples/generated_projects/demo_detector
```

```bash
robopilot report examples/generated_projects/demo_detector --output report.md
```

## Completed: v0.7.0 Planner Interface and Optional LLM Planner

Status: Completed

Goal:

Add a planner abstraction and prepare RoboPilot for optional LLM-assisted planning.

Completed features:

- `Planner` interface
- `RuleBasedPlanner`
- `LLMPlanner` with injectable client support
- Planner selection for `robopilot plan`
- Offline rule-based planner as default
- LLM planner path constrained to `ProjectSpec`
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner rule
```

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm
```

## Completed: v0.8.0 Real LLM Provider Integration

Status: Completed

Goal:

Make the optional LLM planner usable with a real provider while preserving the spec-first architecture.

Completed features:

- Optional OpenAI-compatible planner client
- Environment-based provider configuration
- `OPENAI_API_KEY`
- `ROBOPILOT_LLM_MODEL`
- Optional `llm` dependency extra
- Model selection for LLM planning
- Structured ProjectSpec-compatible LLM output
- Spec validation before returning LLM-generated specs
- Expanded tests
- Updated documentation

Core command:

```bash
robopilot plan --name demo_detector --task "Create an object detection pipeline" --planner llm --model gpt-4.1-mini
```

## Completed: v0.9.0 Spec Refinement

Status: Completed

Goal:

Allow users to refine existing `robopilot.yaml` / `ProjectSpec` files with deterministic rule-based instructions.

Completed features:

- `robopilot refine`
- Rule-based spec refinement
- Add tracker node
- Add camera node
- Add controller node
- Add explicit topics
- Avoid duplicate nodes and topics
- Preserve original spec by writing to a new output file
- Validate refined specs before saving
- Expanded tests
- Updated documentation

Core command:

```bash
robopilot refine --spec base.yaml --instruction "Add a tracker node after the detector" --output refined.yaml
```

## Completed: v0.10.0 Spec Diff

Status: Completed

Goal:

Compare two ProjectSpec files and report deterministic differences.

Completed features:

- `robopilot diff`
- Optional JSON output
- Comparison of scalar fields
- Comparison of nodes
- Comparison of topics
- Comparison of config files
- Comparison of launch files
- Comparison of notes
- Validation of both specs before diffing
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot diff --old base.yaml --new refined.yaml
```

```bash
robopilot diff --old base.yaml --new refined.yaml --json
```

## Completed: v0.11.0 LLM-assisted Spec Refinement

Status: Completed

Goal:

Enable the existing refine workflow to use the optional LLM provider path safely.

Completed features:

- `LLMRefiner`
- `robopilot refine --planner llm`
- Model selection for LLM-assisted refinement
- Reuse of existing provider config and OpenAI client
- Reuse of ProjectSpec parsing and validation
- Guardrails against unrequested package name and task changes
- Original spec remains unchanged
- Expanded tests
- Updated documentation

Core command:

```bash
robopilot refine --spec base.yaml --instruction "Add a tracker node after the detector" --planner llm --output refined.yaml
```

Recommended review step:

```bash
robopilot diff --old base.yaml --new refined.yaml
```

## Completed: v0.12.0 Apply Preview

Status: Completed

Goal:

Add a safe, read-only preview workflow that compares a validated spec against an existing project directory.

Completed features:

- `robopilot apply-preview`
- Optional JSON output
- In-memory expected project rendering
- Classification of files to create, update, keep, or flag
- Refactored generator rendering into reusable deterministic rendering
- Multi-node expected Python file rendering
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector
```

```bash
robopilot apply-preview --spec refined.yaml --project outputs/demo_detector --json
```

## Completed: v0.13.0 Apply Plan Export

Status: Completed

Goal:

Export apply-preview results into a reviewable and validatable apply plan file.

Completed features:

- `robopilot apply-plan`
- `robopilot apply-plan-validate`
- YAML-like apply plan export
- JSON apply plan export
- Stable apply plan fields
- Apply plan validation
- Reuse of apply-preview logic
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.yaml
```

```bash
robopilot apply-plan --spec refined.yaml --project outputs/demo_detector --output apply_plan.json --format json
```

```bash
robopilot apply-plan-validate --plan apply_plan.yaml
```

## Completed: v0.14.0 Apply from Plan

Status: Completed

Goal:

Add the first safe file-writing workflow based on a validated apply plan.

Completed features:

- `robopilot apply`
- Dry-run apply by default
- Confirmed apply with `--confirm`
- JSON summary output
- Apply plan validation before applying
- Re-run apply-preview before applying
- Stale plan rejection
- Conflict rejection
- Restricted writes based on plan contents
- Backup creation before updates
- Unsafe relative path rejection
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot apply --plan apply_plan.yaml
```

```bash
robopilot apply --plan apply_plan.yaml --confirm
```

```bash
robopilot apply --plan apply_plan.yaml --confirm --json
```

## Completed: v0.15.0 Apply Rollback

Status: Completed

Goal:

Add a safe rollback workflow for files backed up during `robopilot apply --confirm`.

Completed features:

- `robopilot rollback`
- Dry-run rollback by default
- Confirmed rollback with `--confirm`
- JSON summary output
- Restore files from RoboPilot backup directories
- Project path validation
- Backup path validation
- Path traversal protection
- Symlink protection
- No deletion of newly created files in this version
- Expanded tests
- Updated documentation

Core commands:

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp>
```

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --confirm
```

```bash
robopilot rollback --project outputs/demo_detector --backup outputs/demo_detector/.robopilot_backups/<timestamp> --json
```

## Completed: v0.16.0 Apply History / Workspace Journal

Status: Completed

Goal:

Add a project-local history system that records confirmed apply and rollback operations.

This feature should make file-writing workflows easier to audit, inspect, and eventually roll back from without manually searching backup directories.

Planned commands:

```bash
robopilot history --project outputs/demo_detector
```

```bash
robopilot history --project outputs/demo_detector --json
```

Expected history directory:

```txt
.robopilot_history/
```

Expected journal entry fields:

- operation type
- timestamp
- project path
- plan path if applicable
- backup path if applicable
- files created
- files updated
- files restored
- files kept
- conflicts
- dry-run status
- success status
- summary message

Expected behavior:

- Record confirmed apply operations.
- Record confirmed rollback operations.
- Do not record dry-runs as successful modifications.
- Store journal entries under the target project.
- List history entries in chronological order.
- Provide deterministic JSON output.
- Do not execute ROS, ROS2, launch files, colcon, or generated code.
- Do not modify project files except for RoboPilot history metadata.

Suggested implementation files:

```txt
src/robopilot/history/
├─ __init__.py
└─ journal.py
```

Suggested tests:

```txt
tests/test_history.py
```

Suggested test cases:

- Confirmed apply records a history entry.
- Confirmed rollback records a history entry.
- Dry-run apply does not create a successful modification entry.
- History command handles projects with no history.
- History command handles missing project path.
- History JSON output has stable keys.
- History entries are sorted deterministically.
- Existing apply and rollback tests still pass.

## Completed: v0.17.0 ROS Project Detector

Status: Completed

Goal:

Introduce static project type detection for existing ROS-style projects.

This is the first step toward expanding RoboPilot beyond RoboPilot-generated projects.

Core commands:

```bash
robopilot detect path/to/project
```

```bash
robopilot detect path/to/project --json
```

Expected project categories:

- RoboPilot-generated project
- ROS1 catkin package
- ROS2 ament Python package
- ROS2 ament C++ package
- Mixed ROS-style project
- Non-ROS project
- Unknown project

Detection signals:

- `robopilot.yaml`
- `package.xml`
- `CMakeLists.txt`
- `setup.py`
- `setup.cfg`
- `launch/`
- `msg/`
- `srv/`
- `action/`
- `catkin_package`
- `ament_package`
- `ament_python`
- `rospy`
- `roscpp`
- `rclpy`
- `rclcpp`

This feature should remain static and should not require ROS, ROS2, catkin, or colcon.

## Completed: v0.18.0 ROS1 Static Inspector

Status: Completed

Goal:

Extend RoboPilot's inspection capability to ROS1 catkin packages.

Core commands:

```bash
robopilot inspect-ros1 path/to/ros1_package
```

```bash
robopilot inspect-ros1 path/to/ros1_package --json
```

Expected analysis:

- `package.xml`
- `CMakeLists.txt`
- catkin dependencies
- `catkin_package`
- `find_package(catkin REQUIRED COMPONENTS ...)`
- `scripts/`
- `src/`
- `launch/`
- `msg/`
- `srv/`
- `action/`
- Python ROS1 nodes using `rospy`
- C++ ROS1 nodes using `roscpp`
- Potential ROS1 package structure issues

This feature should remain static and should not require ROS, run `catkin_make`,
run colcon, import user modules, execute launch files, or execute ROS1 code.

## Completed: v0.19.0 Dependency Analyzer

Status: Completed

Goal:

Analyze declared and used dependencies in ROS-style projects.

Core commands:

```bash
robopilot deps path/to/project
```

```bash
robopilot deps path/to/project --json
```

Expected output:

- declared dependencies
- detected imports/includes
- CMake find_package dependencies
- catkin components
- launch file package references
- possibly missing dependencies
- possibly unused dependencies
- ROS1 dependency hints
- ROS2 dependency hints
- migration-related dependency hints

Possible sources:

- `package.xml`
- `CMakeLists.txt`
- `setup.py`
- Python imports
- C++ includes
- launch files
- msg/srv/action files

The analyzer should be conservative and should report uncertainty clearly.

## Completed: v0.20.0 ROS1 to ROS2 Migration Plan

Status: Completed

Goal:

Generate a static migration plan for ROS1 packages moving toward ROS2-style structure.

Core commands:

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.yaml
```

```bash
robopilot migrate-plan --from path/to/ros1_package --to ros2 --output migration_plan.json --format json
```

Expected migration plan sections:

- package metadata migration
- `package.xml` format migration
- catkin to ament migration
- CMake migration hints
- Python node migration hints
- C++ node migration hints
- launch file migration hints
- msg/srv/action migration notes
- dependency mapping suggestions
- manual review items

Important:

This version should only generate a migration plan. It should not automatically rewrite the project, generate migrated files, run ROS, run catkin, or run colcon.

## Current: v0.21.0 Migration Apply Preview

Status: Current work

Goal:

Preview what a ROS1-to-ROS2 migration plan would create or update.

Core commands:

```bash
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package
```

```bash
robopilot migrate-preview --plan migration_plan.yaml --project path/to/ros1_package --json
```

Expected behavior:

- load and validate a generated migration plan
- re-inspect the source project statically
- preview files to create
- preview files to update
- preview files to keep
- preview files requiring manual migration
- preview interface files and dependency items that need review
- preview conflicts and risks
- remain fully read-only

This should reuse migration planning, static project detection, ROS1 inspection, and dependency analysis. It must not modify source files, generate migrated files, run ROS, run `catkin_make`, or run colcon.

## Future: v0.22.0 LLM-assisted Report Explanation

Status: Planned

Goal:

Add optional LLM explanation for inspection, dependency, and migration reports.

Possible command:

```bash
robopilot explain --report report.md --planner llm
```

LLM rules:

- explain existing reports
- clarify warnings
- summarize risks
- suggest next manual steps
- do not modify files
- do not generate project files directly
- do not execute commands

This feature should remain optional and should require explicit LLM configuration.

## Future: v1.0.0 First Stable Release

Status: Planned

Goal:

Release the first stable version of RoboPilot as a no-ROS-required static engineering toolchain for ROS-style projects.

Suggested v1.0.0 scope:

- Stable ProjectSpec workflow
- Stable apply / rollback safety loop
- Stable history / journal
- Stable inspect / report workflow
- Optional LLM planner and refiner
- ROS project detection
- ROS1 static inspection
- Dependency analyzer
- Basic ROS1-to-ROS2 migration plan
- Clear documentation
- CI passing
- Backward-compatible core CLI behavior

v1.0.0 positioning:

```txt
RoboPilot is a no-ROS-required static engineering toolchain for planning, inspecting, updating, analyzing, and migrating ROS-style projects.
```

## Future: VSCode Lightweight Extension

Status: Long-term idea

Goal:

Create a lightweight VSCode integration that wraps the stable RoboPilot CLI.

The extension should not duplicate core logic. It should call the CLI.

Possible features:

- Validate `robopilot.yaml`
- Run `robopilot inspect` on current workspace
- Show project report
- Show spec diff
- Show apply-preview results
- Show dependency analysis
- Show migration plan
- Provide quick actions for common RoboPilot commands

This should only be considered after the CLI workflow is stable.

## Non-goals for Early Versions

RoboPilot will not focus on the following before the core static toolchain is stable:

- Real robot deployment
- Heavy model training
- Full ROS runtime execution
- Automatic `catkin_make`
- Automatic `colcon build`
- SLAM implementation
- Reinforcement learning training
- Large-scale VLA model inference
- Embedded low-level driver development
- Complex multi-agent orchestration
- RAG system before the core static workflow is stable
- Replacing general-purpose coding agents

## Development Priorities

Priority order:

1. Keep the CLI runnable.
2. Keep no-ROS-required usage as a core principle.
3. Keep the spec-first workflow stable.
4. Keep behavior deterministic and testable.
5. Avoid unnecessary dependencies.
6. Reuse existing validation, rendering, preview, and apply logic.
7. Make generated, inspected, and migrated outputs easy to understand.
8. Keep file-writing workflows dry-run-first and recoverable.
9. Keep documentation concise and current.
10. Add optional AI features only when they preserve deterministic safety boundaries.

## Current Recommended Development Path

```txt
v0.16.0 Apply History / Workspace Journal
        ↓
v0.17.0 ROS Project Detector
        ↓
v0.18.0 ROS1 Static Inspector
        ↓
v0.19.0 Dependency Analyzer
        ↓
v0.20.0 ROS1 to ROS2 Migration Plan
        ↓
v0.21.0 Migration Apply Preview
        ↓
v0.22.0 Optional LLM Report Explanation
        ↓
v1.0.0 First Stable Release
```

RoboPilot should grow as a practical no-ROS-required ROS engineering toolchain, not as a one-time demo script and not as a general-purpose coding agent.
