# Research Decision Log

This log records product-direction decisions for RoboPilot 2.x. It is a planning aid, not a changelog.

## Template

```md
## YYYY-MM-DD - Decision Title

Status: proposed / accepted / deferred / rejected

Context:
- Why this decision is being considered.

Decision:
- What was decided.

Consequences:
- Expected benefits, tradeoffs, and follow-up work.

Related:
- Research brief:
- Backlog item:
```

## 2026-05-17 - RoboPilot Remains No-ROS-Required In 2.x

Status: accepted

Context:
- RoboPilot v2.0.0 completed a static no-ROS-required engineering workflow.
- The project is useful because it works without ROS, ROS2, catkin, colcon, launch execution, or generated node execution.

Decision:
- RoboPilot 2.x should preserve the no-ROS-required default behavior.

Consequences:
- Feature ideas that require runtime ROS tooling should be classified as out of scope or future major-version candidates.

## 2026-05-17 - Migration Assistance Stays Static And Review-First

Status: accepted

Context:
- ROS1-to-ROS2 migration is high-risk and project-specific.
- RoboPilot currently provides plans, previews, scaffolds, validation, and reports.

Decision:
- RoboPilot 2.x should focus on static, conservative, review-first migration assistance.

Consequences:
- Better hints, reports, tutorials, and scaffold quality are preferred over automatic source conversion.

## 2026-05-17 - VSCode Extension Remains A Thin CLI Wrapper

Status: accepted

Context:
- The VSCode extension consumes RoboPilot CLI/API/JSON contracts.
- Duplicating core logic in TypeScript would increase maintenance risk.

Decision:
- The VSCode extension should remain a thin UI wrapper over CLI/API/JSON contracts.

Consequences:
- VSCode improvements should focus on command discoverability, output display, TreeView state, warnings, and docs links.

## 2026-05-17 - Automatic Migration Apply Is Deferred

Status: accepted

Context:
- Applying migration edits to source projects would cross a major safety boundary.
- v2.0.0 intentionally completed a scaffold/review loop instead.

Decision:
- Automatic migration apply and source patching are deferred beyond 2.x unless explicitly revisited.

Consequences:
- 2.x planning should avoid features that imply automatic source modification for migration.

## 2026-05-17 - Research Briefs Before Large Features

Status: accepted

Context:
- RoboPilot should not grow through speculative feature expansion.
- Future work should be research-backed and scoped.

Decision:
- Broad 2.x features should first be captured in `docs/research/` as research briefs and backlog items.

Consequences:
- Implementation tasks should reference accepted briefs and avoid browsing or inventing broad requirements during coding.

