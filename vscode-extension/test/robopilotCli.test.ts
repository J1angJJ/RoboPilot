import * as assert from "assert";
import { test } from "node:test";
import * as path from "path";
import {
  analyzeDependenciesArgs,
  detectWorkspaceArgs,
  formatCliError,
  generateMigrationPlanArgs,
  generateMigrationScaffoldArgs,
  generateScaffoldReportArgs,
  inspectRos1Args,
  isMissingExecutableError,
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
} from "../src/robopilotCli";

test("builds command arguments without shell interpolation", () => {
  assert.deepStrictEqual(detectWorkspaceArgs("C:\\demo project"), ["detect", "C:\\demo project", "--json"]);
  assert.deepStrictEqual(inspectRos1Args("/tmp/pkg"), ["inspect-ros1", "/tmp/pkg", "--json"]);
  assert.deepStrictEqual(analyzeDependenciesArgs("/tmp/pkg"), ["deps", "/tmp/pkg", "--json"]);
  assert.deepStrictEqual(previewMigrationArgs("/tmp/plan.json", "/tmp/pkg"), [
    "migrate-preview",
    "--plan",
    "/tmp/plan.json",
    "--project",
    "/tmp/pkg",
    "--json"
  ]);
  assert.deepStrictEqual(validateProjectSpecArgs("/tmp/robopilot.yaml"), ["validate", "--spec", "/tmp/robopilot.yaml"]);
});

test("builds migration plan arguments", () => {
  assert.deepStrictEqual(generateMigrationPlanArgs("/tmp/pkg", "/tmp/out/migration_plan.json"), [
    "migrate-plan",
    "--from",
    "/tmp/pkg",
    "--to",
    "ros2",
    "--output",
    "/tmp/out/migration_plan.json",
    "--format",
    "json"
  ]);
});

test("builds migration scaffold workflow arguments", () => {
  assert.deepStrictEqual(previewMigrationScaffoldArgs("/tmp/out/migration_plan.json"), [
    "migrate-scaffold-preview",
    "--plan",
    "/tmp/out/migration_plan.json",
    "--json"
  ]);
  assert.deepStrictEqual(generateMigrationScaffoldArgs("/tmp/out/migration_plan.json", "/tmp/out/ros2_scaffold"), [
    "migrate-scaffold",
    "--plan",
    "/tmp/out/migration_plan.json",
    "--output",
    "/tmp/out/ros2_scaffold",
    "--json"
  ]);
  assert.deepStrictEqual(validateMigrationScaffoldArgs("/tmp/out/migration_plan.json", "/tmp/out/ros2_scaffold"), [
    "migrate-scaffold-validate",
    "--plan",
    "/tmp/out/migration_plan.json",
    "--scaffold",
    "/tmp/out/ros2_scaffold",
    "--json"
  ]);
  assert.deepStrictEqual(generateScaffoldReportArgs("/tmp/out/migration_plan.json", "/tmp/out/ros2_scaffold", "/tmp/out/scaffold_report.md"), [
    "migrate-scaffold-report",
    "--plan",
    "/tmp/out/migration_plan.json",
    "--scaffold",
    "/tmp/out/ros2_scaffold",
    "--output",
    "/tmp/out/scaffold_report.md"
  ]);
});

test("parses JSON output", () => {
  const result = parseJsonOutput<{ project_type: string }>("{\"project_type\":\"robopilot_project\"}");
  assert.strictEqual(result.project_type, "robopilot_project");
});

test("reports JSON parse failures clearly", () => {
  assert.throws(() => parseJsonOutput("{not-json"), /invalid JSON/);
});

test("detects missing executable errors", () => {
  const error = Object.assign(new Error("spawn robopilot ENOENT"), { code: "ENOENT" });
  assert.strictEqual(isMissingExecutableError(error), true);
  assert.match(formatCliError(error), /pip install robopilot/);
});

test("resolves output directories", () => {
  assert.strictEqual(resolveOutputDirectory("/workspace", ".robopilot_vscode"), path.join("/workspace", ".robopilot_vscode"));
  assert.strictEqual(migrationPlanPath("/workspace/.robopilot_vscode"), path.join("/workspace/.robopilot_vscode", "migration_plan.json"));
  assert.strictEqual(scaffoldDirectoryPath("/workspace/.robopilot_vscode"), path.join("/workspace/.robopilot_vscode", "ros2_scaffold"));
  assert.strictEqual(scaffoldReportPath("/workspace/.robopilot_vscode"), path.join("/workspace/.robopilot_vscode", "scaffold_report.md"));
});

test("runRobopilot returns stdout stderr and exit code", async () => {
  const result = await runRobopilot("robopilot", ["detect", "/tmp", "--json"], {
    execFileImpl: (_file, _args, _options, callback) => {
      callback(null, "{\"ok\":true}", "");
    }
  });
  assert.deepStrictEqual(result, {
    stdout: "{\"ok\":true}",
    stderr: "",
    exitCode: 0
  });
});

test("runRobopilot rejects missing executable with friendly error", async () => {
  await assert.rejects(
    () =>
      runRobopilot("missing-robopilot", ["--help"], {
        execFileImpl: (_file, _args, _options, callback) => {
          const error = Object.assign(new Error("spawn missing-robopilot ENOENT"), { code: "ENOENT" });
          callback(error, "", "");
        }
      }),
    /pip install robopilot/
  );
});
