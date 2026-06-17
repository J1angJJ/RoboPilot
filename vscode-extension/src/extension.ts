import * as fs from "fs/promises";
import * as path from "path";
import * as vscode from "vscode";
import {
  analyzeDependenciesArgs,
  detectWorkspaceArgs,
  formatCliError,
  generateMigrationPlanArgs,
  generateMigrationScaffoldArgs,
  generateScaffoldReportArgs,
  inspectRos1Args,
  lintWorkspaceArgs,
  migrationPlanPath,
  parseJsonOutput,
  previewMigrationArgs,
  previewMigrationScaffoldArgs,
  resolveOutputDirectory,
  runRobopilot,
  scaffoldDirectoryPath,
  scaffoldReportPath,
  validateMigrationScaffoldArgs,
  validateProjectSpecArgs
} from "./robopilotCli";
import { RoboPilotOutput } from "./output";
import { RoboPilotProjectTreeProvider } from "./projectTree";
import {
  DependencyAnalysisResult,
  DetectResult,
  LintIssue,
  LintResult,
  MigrationPlanResult,
  MigrationPreviewResult,
  MigrationScaffoldGenerationResult,
  MigrationScaffoldPreviewResult,
  MigrationScaffoldValidationResult,
  Ros1InspectionResult,
  ScaffoldFileItem
} from "./types";

let output: RoboPilotOutput;
let tree: RoboPilotProjectTreeProvider;
let diagnostics: vscode.DiagnosticCollection;
let statusBar: vscode.StatusBarItem;

const LINT_WATCH_PATTERNS = ["**/package.xml", "**/CMakeLists.txt", "**/setup.py", "**/setup.cfg"];

export function activate(context: vscode.ExtensionContext): void {
  output = new RoboPilotOutput();
  tree = new RoboPilotProjectTreeProvider();
  diagnostics = vscode.languages.createDiagnosticCollection("robopilot");
  context.subscriptions.push(diagnostics);

  // Status bar
  statusBar = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
  statusBar.command = "robopilot.showOutput";
  statusBar.text = "$(checklist) RoboPilot";
  statusBar.tooltip = "RoboPilot — run Detect Workspace to start";
  statusBar.show();
  context.subscriptions.push(statusBar);

  context.subscriptions.push(output);
  context.subscriptions.push(vscode.window.registerTreeDataProvider("robopilot.projectView", tree));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.detectWorkspace", detectWorkspace));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.inspectRos1", inspectRos1));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.analyzeDependencies", analyzeDependencies));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.generateMigrationPlan", generateMigrationPlan));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.previewMigration", previewMigration));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.previewMigrationScaffold", previewMigrationScaffold));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.generateMigrationScaffold", generateMigrationScaffold));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.validateMigrationScaffold", validateMigrationScaffold));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.generateScaffoldReport", generateScaffoldReport));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.openScaffoldReport", openScaffoldReport));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.validateProjectSpec", validateProjectSpec));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.showOutput", () => output.show()));

  // v2.1.0 M9: new commands
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.lintWorkspace", lintWorkspace));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.showTemplates", showTemplates));

  // v2.2.0 M15: template-init and migrate-score
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.templateInit", templateInit));
  context.subscriptions.push(vscode.commands.registerCommand("robopilot.showMigrationScore", showMigrationScore));

  // v2.1.0 M9: lint on save for package files
  context.subscriptions.push(
    vscode.workspace.onDidSaveTextDocument((doc) => {
      if (isLintableFile(doc.fileName)) {
        lintWorkspaceSilent(doc.fileName);
      }
    })
  );
}

export function deactivate(): void {
  // VSCode disposes registered subscriptions.
}

// ---------------------------------------------------------------------------
// M9: Lint workspace command
// ---------------------------------------------------------------------------

async function lintWorkspace(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  await runJsonCommand<LintResult>(
    "Lint Workspace",
    (wp) => lintWorkspaceArgs(wp),
    (result) => {
      output.appendSection("Lint", [
        `Package: ${result.package_name ?? "unknown"}`,
        `Errors: ${result.error_count}, Warnings: ${result.warning_count}, Info: ${result.info_count}`
      ]);
      if (result.issues.length === 0) {
        output.appendSection("Result", ["No issues found."]);
      }
      for (const issue of result.issues) {
        output.appendSection(`${issue.severity}: ${issue.file}`, [`[${issue.rule}] ${issue.message}`]);
      }
      tree.update({
        workspacePath,
        packageName: result.package_name ?? undefined,
        lintStatus: result.error_count > 0 ? `${result.error_count} errors` : result.warning_count > 0 ? `${result.warning_count} warnings` : "clean",
        issuesCount: result.error_count,
        warningsCount: result.warning_count
      });
      updateStatusBar(result);
      // Populate diagnostics
      diagnostics.clear();
      const diagMap = new Map<string, vscode.Diagnostic[]>();
      for (const issue of result.issues) {
        const filePath = path.join(workspacePath, issue.file);
        const diag = lintIssueToDiagnostic(issue);
        if (!diagMap.has(filePath)) { diagMap.set(filePath, []); }
        diagMap.get(filePath)!.push(diag);
      }
      for (const [filePath, diags] of diagMap) {
        diagnostics.set(vscode.Uri.file(filePath), diags);
      }
    }
  );
}

async function lintWorkspaceSilent(filePath: string): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const args = lintWorkspaceArgs(workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const parsed = parseJsonOutput<LintResult>(result.stdout);
    tree.update({
      lintStatus: parsed.error_count > 0 ? `${parsed.error_count} errors` : parsed.warning_count > 0 ? `${parsed.warning_count} warnings` : "clean",
      issuesCount: parsed.error_count,
      warningsCount: parsed.warning_count
    });
    updateStatusBar(parsed);
    diagnostics.clear();
    const diagMap = new Map<string, vscode.Diagnostic[]>();
    for (const issue of parsed.issues) {
      const targetFile = path.join(workspacePath, issue.file);
      if (!diagMap.has(targetFile)) { diagMap.set(targetFile, []); }
      diagMap.get(targetFile)!.push(lintIssueToDiagnostic(issue));
    }
    for (const [f, diags] of diagMap) {
      diagnostics.set(vscode.Uri.file(f), diags);
    }
  } catch {
    // Silent fail on lint — don't bother the user on save
  }
}

function isLintableFile(filePath: string): boolean {
  const name = path.basename(filePath);
  return name === "package.xml" || name === "CMakeLists.txt" || name === "setup.py" || name === "setup.cfg";
}

function lintIssueToDiagnostic(issue: LintIssue): vscode.Diagnostic {
  const severity = issue.severity === "error" ? vscode.DiagnosticSeverity.Error
    : issue.severity === "warning" ? vscode.DiagnosticSeverity.Warning
    : vscode.DiagnosticSeverity.Information;
  return new vscode.Diagnostic(
    new vscode.Range(0, 0, 0, 0),
    `[${issue.rule}] ${issue.message}`,
    severity
  );
}

function updateStatusBar(result: LintResult): void {
  if (result.error_count > 0) {
    statusBar.text = `$(error) RoboPilot: ${result.error_count} errors`;
    statusBar.backgroundColor = undefined;
  } else if (result.warning_count > 0) {
    statusBar.text = `$(warning) RoboPilot: ${result.warning_count} warnings`;
    statusBar.backgroundColor = undefined;
  } else {
    statusBar.text = `$(check) RoboPilot: clean`;
    statusBar.backgroundColor = undefined;
  }
}

// ---------------------------------------------------------------------------
// M9: Templates
// ---------------------------------------------------------------------------

async function showTemplates(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const args = ["tutorial", "--list", "--json"];
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const lessons = JSON.parse(result.stdout) as { id: string; title: string }[];
    output.appendSection("Available Templates & Tutorials", [
      `Found ${lessons.length} items:`,
      ...lessons.map((l: { id: string; title: string }) => `  ${l.id}: ${l.title}`)
    ]);
    output.appendSection("Quick Start", [
      "Run tutorial: robopilot tutorial --lesson demo_detector",
      "Plan with template: robopilot plan --template <name> --name <project> --task \"...\"",
      "Init templates: robopilot template-init"
    ]);
    tree.update({ templateCount: lessons.length });
    output.show();
  } catch (error) {
    showFailure(error);
  }
}

// ---------------------------------------------------------------------------
// M15: template-init and migrate-score
// ---------------------------------------------------------------------------

async function templateInit(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const args = ["template-init", "--root", workspacePath];
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    output.appendSection("Template Init", result.stdout.trim().split(/\r?\n/));
    output.appendSection("Next Steps", [
      "Edit .robopilot/templates/my_custom_node/template.yaml",
      "Validate: robopilot template-validate --path .robopilot/templates/my_custom_node",
      "Use: robopilot plan --template my_custom_node --name <proj> --task \"...\""
    ]);
    output.show();
    vscode.window.showInformationMessage("RoboPilot: Templates directory created in .robopilot/templates/");
  } catch (error) {
    showFailure(error);
  }
}

async function showMigrationScore(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const args = ["migrate-score", workspacePath, "--json"];
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const parsed = JSON.parse(result.stdout) as {
      overall_score: number;
      source_project_type: string;
      package_name: string | null;
    };
    const score = parsed.overall_score;
    const band = score >= 80 ? "LOW" : score >= 60 ? "MODERATE" : score >= 40 ? "HIGH" : "VERY HIGH";
    output.appendSection("Migration Readiness Score", [
      `Score: ${score}/100 — ${band} difficulty`,
      `Package: ${parsed.package_name ?? "unknown"}`,
      `Type: ${parsed.source_project_type}`
    ]);
    tree.update({ packageName: parsed.package_name ?? undefined });
    statusBar.text = `$(graph) RoboPilot: migrate ${score}/100`;
    statusBar.tooltip = `ROS1→ROS2 migration readiness: ${score}/100 (${band})`;
    output.show();
  } catch (error) {
    showFailure(error);
  }
}

// ---------------------------------------------------------------------------
// Existing commands (unchanged below)
// ---------------------------------------------------------------------------

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
      tree.update({ workspacePath: result.project_path, projectType: result.project_type });
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
  if (!workspacePath) { return; }
  const outputDir = getOutputDirectory(workspacePath);
  const planPath = migrationPlanPath(outputDir);
  await fs.mkdir(outputDir, { recursive: true });
  const args = generateMigrationPlanArgs(workspacePath, planPath);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const data = JSON.parse(await fs.readFile(planPath, "utf8")) as MigrationPlanResult;
    output.appendSection("Migration Plan", [
      `Output: ${planPath}`, `Package: ${data.package_name || "unknown"}`,
      `Target: ${data.target}`, `Confidence: ${data.confidence}`
    ]);
    output.appendSection("Risks", data.risks ?? []);
    output.appendSection("Next Steps", data.suggested_next_steps ?? []);
    tree.update({ workspacePath, packageName: data.package_name, migrationPlanStatus: "generated" });
    output.show();
  } catch (error) { showFailure(error); }
}

async function previewMigration(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const planPath = migrationPlanPath(getOutputDirectory(workspacePath));
  try { await fs.access(planPath); } catch {
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
      tree.update({ workspacePath, packageName: result.package_name, migrationPlanStatus: "previewed" });
    }
  );
}

async function previewMigrationScaffold(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const planPath = migrationPlanPath(getOutputDirectory(workspacePath));
  if (!(await pathExists(planPath))) {
    vscode.window.showWarningMessage("No migration_plan.json found. Generate Migration Plan first.");
    return;
  }
  await runJsonCommand<MigrationScaffoldPreviewResult>(
    "Preview Migration Scaffold",
    () => previewMigrationScaffoldArgs(planPath),
    (result) => {
      output.appendSection("Scaffold Preview", [
        `Package: ${result.package_name || "unknown"}`,
        `Target style: ${result.target_style || "unknown"}`,
        `Scaffold files: ${result.scaffold_files_to_create.length}`,
        `Placeholder files: ${result.placeholder_files.length}`
      ]);
      output.appendSection("Scaffold Files to Create", formatScaffoldFiles(result.scaffold_files_to_create));
      output.appendSection("Placeholder Files", formatScaffoldFiles(result.placeholder_files));
      output.appendSection("Manual Migration Files", result.files_requiring_manual_migration);
      output.appendSection("Risks", result.risks);
      output.appendSection("Conflicts", result.conflicts);
      output.appendSection("Next Steps", result.suggested_next_steps);
      tree.update({
        workspacePath, packageName: result.package_name,
        scaffoldPreviewStatus: result.conflicts.length ? "conflicts" : "previewed",
        warningsCount: result.risks.length + result.conflicts.length
      });
    }
  );
}

async function generateMigrationScaffold(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const outputDir = getOutputDirectory(workspacePath);
  const planPath = migrationPlanPath(outputDir);
  const scaffoldDir = scaffoldDirectoryPath(outputDir);
  if (!(await pathExists(planPath))) {
    vscode.window.showWarningMessage("No migration_plan.json found. Generate Migration Plan first.");
    return;
  }
  await fs.mkdir(outputDir, { recursive: true });
  const args = generateMigrationScaffoldArgs(planPath, scaffoldDir);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const commandResult = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const result = parseJsonOutput<MigrationScaffoldGenerationResult>(commandResult.stdout);
    renderMigrationScaffoldGeneration(workspacePath, scaffoldDir, result);
    if (commandResult.stderr.trim()) {
      output.appendSection("stderr", [commandResult.stderr.trim()]);
    }
    output.show();
  } catch (error) {
    showFailure(error, [
      "RoboPilot does not pass --overwrite from the extension. Choose a clean output directory."
    ]);
  }
}

async function validateMigrationScaffold(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const outputDir = getOutputDirectory(workspacePath);
  const planPath = migrationPlanPath(outputDir);
  const scaffoldDir = scaffoldDirectoryPath(outputDir);
  if (!(await pathExists(planPath))) {
    vscode.window.showWarningMessage("No migration_plan.json found. Generate Migration Plan first.");
    return;
  }
  if (!(await pathExists(scaffoldDir))) {
    vscode.window.showWarningMessage("No ros2_scaffold directory found. Generate Migration Scaffold first.");
    return;
  }
  await runJsonCommand<MigrationScaffoldValidationResult>(
    "Validate Migration Scaffold",
    () => validateMigrationScaffoldArgs(planPath, scaffoldDir),
    (result) => {
      output.appendSection("Scaffold Validation", [
        `Valid: ${result.valid}`, `Package: ${result.package_name || "unknown"}`,
        `Target style: ${result.target_style || "unknown"}`
      ]);
      output.appendSection("Missing Files", result.missing_files);
      output.appendSection("Unexpected Files", result.unexpected_files);
      output.appendSection("Placeholder Checks", formatPlaceholderChecks(result.placeholder_checks));
      output.appendSection("Issues", result.issues);
      output.appendSection("Warnings", result.warnings);
      output.appendSection("Next Steps", result.suggested_next_steps);
      output.appendSection("Safety Note", [result.safety_note]);
      tree.update({
        workspacePath, packageName: result.package_name,
        scaffoldValidationStatus: result.valid ? "valid" : "invalid",
        issuesCount: result.issues.length + result.missing_files.length,
        warningsCount: result.warnings.length + result.unexpected_files.length
      });
    }
  );
}

async function generateScaffoldReport(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const outputDir = getOutputDirectory(workspacePath);
  const planPath = migrationPlanPath(outputDir);
  const scaffoldDir = scaffoldDirectoryPath(outputDir);
  const reportPath = scaffoldReportPath(outputDir);
  if (!(await pathExists(planPath))) {
    vscode.window.showWarningMessage("No migration_plan.json found. Generate Migration Plan first.");
    return;
  }
  if (!(await pathExists(scaffoldDir))) {
    vscode.window.showWarningMessage("No ros2_scaffold directory found. Generate Migration Scaffold first.");
    return;
  }
  await fs.mkdir(outputDir, { recursive: true });
  const args = generateScaffoldReportArgs(planPath, scaffoldDir, reportPath);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    output.appendSection("Scaffold Report", [`Report: ${reportPath}`, "Report generation completed."]);
    if (result.stdout.trim()) {
      output.appendSection("RoboPilot Output", result.stdout.trim().split(/\r?\n/));
    }
    if (result.stderr.trim()) { output.appendSection("stderr", [result.stderr.trim()]); }
    tree.update({ workspacePath, scaffoldReportStatus: "generated" });
    output.show();
    vscode.window.showInformationMessage(`RoboPilot scaffold report written to ${reportPath}`);
  } catch (error) { showFailure(error); }
}

async function openScaffoldReport(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const reportPath = scaffoldReportPath(getOutputDirectory(workspacePath));
  if (!(await pathExists(reportPath))) {
    vscode.window.showWarningMessage("No scaffold_report.md found. Generate Scaffold Report first.");
    return;
  }
  const document = await vscode.workspace.openTextDocument(vscode.Uri.file(reportPath));
  await vscode.window.showTextDocument(document);
  tree.update({ workspacePath, scaffoldReportStatus: "opened" });
}

async function validateProjectSpec(): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const specPath = path.join(workspacePath, "robopilot.yaml");
  try { await fs.access(specPath); } catch {
    vscode.window.showWarningMessage("No robopilot.yaml found in the workspace root.");
    return;
  }
  const args = validateProjectSpecArgs(specPath);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    output.appendSection("ProjectSpec Validation", [result.stdout.trim() || "Validation completed."]);
    if (result.stderr.trim()) { output.appendSection("stderr", [result.stderr.trim()]); }
    output.show();
  } catch (error) { showFailure(error); }
}

async function runJsonCommand<T>(
  label: string,
  buildArgs: (workspacePath: string) => string[],
  render: (result: T) => void
): Promise<void> {
  const workspacePath = getWorkspacePath();
  if (!workspacePath) { return; }
  const args = buildArgs(workspacePath);
  output.appendCommand(renderCommand(args), workspacePath);
  try {
    const result = await runRobopilot(getExecutablePath(), args, { cwd: workspacePath });
    const parsed = parseJsonOutput<T>(result.stdout);
    render(parsed);
    if (result.stderr.trim()) { output.appendSection("stderr", [result.stderr.trim()]); }
    output.show();
  } catch (error) { showFailure(error); }
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

function renderMigrationScaffoldGeneration(
  workspacePath: string,
  scaffoldDir: string,
  result: MigrationScaffoldGenerationResult
): void {
  output.appendSection("Migration Scaffold", [
    `Output: ${scaffoldDir}`, `Package: ${result.package_name || "unknown"}`,
    `Target style: ${result.target_style || "unknown"}`
  ]);
  output.appendSection("Files Created", result.files_created);
  output.appendSection("Conflicts", result.conflicts);
  output.appendSection("Skipped Files", result.skipped_files);
  output.appendSection("Manual Migration Required", result.manual_migration_required);
  output.appendSection("Risks", result.risks);
  output.appendSection("Next Steps", result.suggested_next_steps);
  output.appendSection("Safety Note", [result.safety_note]);
  if (result.conflicts.length > 0) {
    output.appendSection("Conflict Help", [
      "RoboPilot does not pass --overwrite from the extension. Choose a clean output directory."
    ]);
  }
  tree.update({
    workspacePath, packageName: result.package_name,
    scaffoldDirectoryStatus: result.conflicts.length ? "conflicts" : "generated",
    warningsCount: result.risks.length + result.conflicts.length + result.skipped_files.length
  });
}

function showFailure(error: unknown, extraLines: readonly string[] = []): void {
  const maybeDetails = error as { stderr?: string };
  const message = formatCliError(error);
  output.appendError(message, maybeDetails.stderr);
  if (extraLines.length > 0) { output.appendSection("Help", extraLines); }
  output.show();
  vscode.window.showErrorMessage(message);
}

function flattenRecord(record: Record<string, string[]>): string[] {
  return Object.entries(record).map(([key, values]) => `${key}: ${values.length ? values.join(", ") : "none"}`);
}

function formatScaffoldFiles(files: readonly ScaffoldFileItem[]): string[] {
  return files.map((item) => {
    const details = [item.purpose, item.status].filter(Boolean).join("; ");
    return details ? `${item.path} (${details})` : item.path;
  });
}

function formatPlaceholderChecks(checks: readonly { path: string; passed: boolean; missing_concepts: string[] }[]): string[] {
  return checks.map((check) => {
    const missing = check.missing_concepts.length ? `; missing: ${check.missing_concepts.join(", ")}` : "";
    return `${check.path}: ${check.passed ? "passed" : "failed"}${missing}`;
  });
}

async function pathExists(targetPath: string): Promise<boolean> {
  try { await fs.access(targetPath); return true; } catch { return false; }
}