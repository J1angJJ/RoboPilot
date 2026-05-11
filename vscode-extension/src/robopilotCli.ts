import { execFile as nodeExecFile } from "child_process";
import * as path from "path";
import { CommandResult } from "./types";

export type ExecFileCallback = (
  error: (NodeJS.ErrnoException & { code?: string | number }) | null,
  stdout: string | Buffer,
  stderr: string | Buffer
) => void;

export type ExecFileLike = (
  file: string,
  args: readonly string[],
  options: { cwd?: string; timeout?: number; windowsHide?: boolean },
  callback: ExecFileCallback
) => void;

export interface RunOptions {
  cwd?: string;
  timeoutMs?: number;
  execFileImpl?: ExecFileLike;
}

export function detectWorkspaceArgs(workspacePath: string): string[] {
  return ["detect", workspacePath, "--json"];
}

export function inspectRos1Args(workspacePath: string): string[] {
  return ["inspect-ros1", workspacePath, "--json"];
}

export function analyzeDependenciesArgs(workspacePath: string): string[] {
  return ["deps", workspacePath, "--json"];
}

export function generateMigrationPlanArgs(workspacePath: string, outputPath: string): string[] {
  return [
    "migrate-plan",
    "--from",
    workspacePath,
    "--to",
    "ros2",
    "--output",
    outputPath,
    "--format",
    "json"
  ];
}

export function previewMigrationArgs(planPath: string, workspacePath: string): string[] {
  return ["migrate-preview", "--plan", planPath, "--project", workspacePath, "--json"];
}

export function validateProjectSpecArgs(specPath: string): string[] {
  return ["validate", "--spec", specPath];
}

export function resolveOutputDirectory(workspacePath: string, configuredDirectory: string): string {
  if (path.isAbsolute(configuredDirectory)) {
    return path.normalize(configuredDirectory);
  }
  return path.join(workspacePath, configuredDirectory);
}

export function migrationPlanPath(outputDirectory: string): string {
  return path.join(outputDirectory, "migration_plan.json");
}

export function parseJsonOutput<T>(stdout: string): T {
  try {
    return JSON.parse(stdout) as T;
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`RoboPilot returned invalid JSON: ${message}`);
  }
}

export function isMissingExecutableError(error: unknown): boolean {
  if (!error || typeof error !== "object") {
    return false;
  }
  const maybeError = error as { code?: string | number; message?: string };
  return maybeError.code === "ENOENT" || Boolean(maybeError.message?.includes("ENOENT"));
}

export function formatCliError(error: unknown): string {
  if (isMissingExecutableError(error)) {
    return "RoboPilot CLI was not found. Install it with: pip install robopilot, or set robopilot.executablePath.";
  }
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}

export function runRobopilot(
  executablePath: string,
  args: readonly string[],
  options: RunOptions = {}
): Promise<CommandResult> {
  const execFileImpl = options.execFileImpl ?? (nodeExecFile as unknown as ExecFileLike);
  return new Promise((resolve, reject) => {
    execFileImpl(
      executablePath,
      args,
      {
        cwd: options.cwd,
        timeout: options.timeoutMs ?? 30000,
        windowsHide: true
      },
      (error, stdout, stderr) => {
        const stdoutText = bufferToString(stdout);
        const stderrText = bufferToString(stderr);
        if (error) {
          const exitCode = typeof error.code === "number" ? error.code : 1;
          const failure = new Error(formatCliError(error));
          Object.assign(failure, { stdout: stdoutText, stderr: stderrText, exitCode });
          reject(failure);
          return;
        }
        resolve({
          stdout: stdoutText,
          stderr: stderrText,
          exitCode: 0
        });
      }
    );
  });
}

function bufferToString(value: string | Buffer): string {
  return Buffer.isBuffer(value) ? value.toString("utf8") : value;
}
