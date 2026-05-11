import * as fs from "fs/promises";
import * as path from "path";
import * as vscode from "vscode";
import {
  analyzeDependenciesArgs,
  detectWorkspaceArgs,
  formatCliError,
  generateMigrationPlanArgs,
  inspectRos1Args,
  migrationPlanPath,
  parseJsonOutput,
  previewMigrationArgs,
  resolveOutputDirectory,
  runRobopilot,
  validateProjectSpecArgs
} from "./robopilotCli";
import { RoboPilotOutput } from "./output";
import { RoboPilotProjectTreeProvider } from "./projectTree";
import {
  DependencyAnalysisResult,
  DetectResult,
  MigrationPlanResult,
  MigrationPreviewResult,
  Ros1InspectionResult
} from "./types";

let output: RoboPilotOutput;
let tree: RoboPilotProjectTreeProvider;

export function activate(context: vscode.ExtensionContext): void {
  output = new RoboPilotOutput();
  tree = new RoboPilotProjectTreeProvider();

  context.subscriptions.push(output);
  context.subscriptions.push(vscode.window.registerTreeDataProvider("robopilot.projectView", tree));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.detectWorkspace", detectWorkspace));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.inspectRos1", inspectRos1));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.analyzeDependencies", analyzeDependencies));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.generateMigrationPlan", generateMigrationPlan));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.previewMigration", previewMigration));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.validateProjectSpec", validateProjectSpec));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.showOutput", () => output.show()));
}

export function deactivate(): void {
  // VSCode disposes registered subscriptions.
}

async function detectWorkspace(): Promise<void> {
  await runJsonCommand<DetectResult>(
    "Detect Workspace",
    (workspacePath) => detectWorkspaceArgs(workspacePath),
    (result) => {
      output.appendSection("Detection", [
        `Project type: ${result.project_type}`,
        `Confidence: ${result.confidence}`,
        `Signals: ${result.detected_signals.length}`
      ]);
      output.appendSection("Next Steps", result.suggested_next_steps);
      tree.update({ projectType: result.project_type });
    }
  );
}

async function inspectRos1(): Promise<void> {
  await runJsonCommand<Ros1InspectionResult>(
    "Inspect ROS1 Package",
    (workspacePath) => inspectRos1Args(workspacePath),
    (result) => {
      output.appendSection("ROS1 Package", [
        `Package: ${result.package_name || "unknown"}`,
        `Format: ${result.package_format || "unknown"}`,
        `Detected type: ${result.detected_project_type}`
      ]);
      output.appendSection("Issues", result.issues);
      output.appendSection("Next Steps", result.suggested_next_steps);
      tree.update({ packageName: result.package_name, issuesCount: result.issues.length });
    }
  );
}

async function analyzeDependencies(): Promise<void> {
  await runJsonCommand<DependencyAnalysisResult>(
    "Analyze Dependencies",
    (workspacePath) => analyzeDependenciesArgs(workspacePath),
    (result) => {
      output.appendSection("Declared Dependencies", flattenRecord(result.declared_dependencies));
      output.appendSection("Detected Usage", flattenRecord(result.detected_usage));
      output.appendSection("Possibly Missing", result.possibly_missing);
      output.appendSection("Possibly Unused", result.possibly_unused);
      output.appendSection("Warnings", result.warnings);
      tree.update({ dependencyWarningsCount: result.warnings.length + result.possibly_missing.length });
    }
  );
}

async function generateMigrationPlan(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) {
    return;
  }
  const outputDir = getOutputDirectory(workspacePath);
  const planPath = migrationPlanPath(outputDir);
  await fs.mkdir(outputDir, { recursive: true });
  const args = generateMigrationPlanArgs(workspacePath, planPath);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const data = JSON.parse(await fs.readFile(planPath, "utf8")) as MigrationPlanResult;
    output.appendSection("Migration Plan", [
      `Output: ${planPath}`,
      `Package: ${data.package_name || "unknown"}`,
      `Target: ${data.target}`,
      `Confidence: ${data.confidence}`
    ]);
    output.appendSection("Risks", data.risks ?? []);
    output.appendSection("Next Steps", data.suggested_next_steps ?? []);
    tree.update({ packageName: data.package_name, migrationPlanStatus: "generated" });
    output.show();
  } catch (error) {
    showFailure(error);
  }
}

async function previewMigration(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) {
    return;
  }
  const planPath = migrationPlanPath(getOutputDirectory(workspacePath));
  try {
    await fs.access(planPath);
  } catch {
    vscode.window.showWarningMessage("No migration_plan.json found. Run RoboPilot: Generate Migration Plan first.");
    return;
  }
  await runJsonCommand<MigrationPreviewResult>(
    "Preview Migration",
    (workspace) => previewMigrationArgs(planPath, workspace),
    (result) => {
      output.appendSection("Files to Create", result.files_to_create);
      output.appendSection("Manual Migration", result.files_requiring_manual_migration);
      output.appendSection("Interface Review", result.interface_files_to_review);
      output.appendSection("Risks", result.risks);
      output.appendSection("Next Steps", result.suggested_next_steps);
      tree.update({ packageName: result.package_name, migrationPlanStatus: "previewed" });
    }
  );
}

async function validateProjectSpec(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) {
    return;
  }
  const specPath = path.join(workspacePath, "robopilot.yaml");
  try {
    await fs.access(specPath);
  } catch {
    vscode.window.showWarningMessage("No robopilot.yaml found in the workspace root.");
    return;
  }
  const args = validateProjectSpecArgs(specPath);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    output.appendSection("ProjectSpec Validation", [result.stdout.trim() || "Validation completed."]);
    if (result.stderr.trim()) {
      output.appendSection("stderr", [result.stderr.trim()]);
    }
    output.show();
  } catch (error) {
    showFailure(error);
  }
}

async function runJsonCommand<T>(
  label: string,
  buildArgs: (workspacePath: string) => string[],
  render: (result: T) => void
): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) {
    return;
  }
  const args = buildArgs(workspacePath);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const parsed = parseJsonOutput<T>(result.stdout);
    render(parsed);
    if (result.stderr.trim()) {
      output.appendSection("stderr", [result.stderr.trim()]);
    }
    output.show();
  } catch (error) {
    showFailure(error);
  }
}

function getWorkspacePath(): string | undefined {
  const folder = vscode.workspace.workspaceFolders?.[0];
  if (!folder) {
    vscode.window.showWarningMessage("Open a workspace folder before running RoboPilot commands.");
    return undefined;
  }
  return folder.uri.fsPath;
}

function getExecutablePath(): string {
  return vscode.workspace.getConfiguration("robopilot").get<string>("executablePath", "robopilot");
}

function getOutputDirectory(workspacePath: string): string {
  const configured = vscode.workspace.getConfiguration("robopilot").get<string>("outputDirectory", ".robopilot_vscode");
  return resolveOutputDirectory(workspacePath, configured);
}

function renderCommand(args: readonly string[]): string {
  return `${getExecutablePath()} ${args.map(quoteArg).join(" ")}`;
}

function quoteArg(arg: string): string {
  return arg.includes(" ") ? `"${arg}"` : arg;
}

function showFailure(error: unknown): void {
  const maybeDetails = error as { stderr?: string };
  const message = formatCliError(error);
  output.appendError(message, maybeDetails.stderr);
  output.show();
  vscode.window.showErrorMessage(message);
}

function flattenRecord(record: Record<string, string[]>): string[] {
  return Object.entries(record).map(([key, values]) => `${key}: ${values.length ? values.join(", ") : "none"}`);
}
