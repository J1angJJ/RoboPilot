import * as vscode from "vscode";
import { ProjectTreeState } from "./types";

export class RoboPilotProjectTreeProvider implements vscode.TreeDataProvider<ProjectTreeItem> {
  private readonly changed = new vscode.EventEmitter<ProjectTreeItem | undefined>();
  readonly onDidChangeTreeData = this.changed.event;
  private state: ProjectTreeState = {};

  update(patch: ProjectTreeState): void {
    this.state = { ...this.state, ...patch };
    this.changed.fire(undefined);
  }

  getTreeItem(element: ProjectTreeItem): vscode.TreeItem {
    return element;
  }

  getChildren(): ProjectTreeItem[] {
    return [
      new ProjectTreeItem("Workspace", this.state.workspacePath ?? "not opened"),
      new ProjectTreeItem("Project type", this.state.projectType ?? "unknown"),
      new ProjectTreeItem("Package", this.state.packageName ?? "unknown"),
      new ProjectTreeItem("Issues", String(this.state.issuesCount ?? 0)),
      new ProjectTreeItem("Warnings", String(this.state.warningsCount ?? 0)),
      new ProjectTreeItem("Dependency warnings", String(this.state.dependencyWarningsCount ?? 0)),
      new ProjectTreeItem("Migration plan", this.state.migrationPlanStatus ?? "not generated"),
      new ProjectTreeItem("Scaffold preview", this.state.scaffoldPreviewStatus ?? "not previewed"),
      new ProjectTreeItem("Scaffold directory", this.state.scaffoldDirectoryStatus ?? "not generated"),
      new ProjectTreeItem("Scaffold validation", this.state.scaffoldValidationStatus ?? "not validated"),
      new ProjectTreeItem("Scaffold report", this.state.scaffoldReportStatus ?? "not generated")
    ];
  }
}

export class ProjectTreeItem extends vscode.TreeItem {
  constructor(label: string, description: string) {
    super(label, vscode.TreeItemCollapsibleState.None);
    this.description = description;
  }
}
