import * as vscode from "vscode";

export class RoboPilotOutput {
  private readonly channel: vscode.OutputChannel;

  constructor() {
    this.channel = vscode.window.createOutputChannel("RoboPilot");
  }

  appendCommand(command: string, workspacePath: string): void {
    this.channel.appendLine("");
    this.channel.appendLine(`> ${command}`);
    this.channel.appendLine(`Workspace: ${workspacePath}`);
  }

  appendSection(title: string, lines: readonly string[]): void {
    this.channel.appendLine("");
    this.channel.appendLine(title);
    this.channel.appendLine("-".repeat(title.length));
    if (lines.length === 0) {
      this.channel.appendLine("- none");
      return;
    }
    for (const line of lines) {
      this.channel.appendLine(`- ${line}`);
    }
  }

  appendLine(line: string): void {
    this.channel.appendLine(line);
  }

  appendError(message: string, stderr?: string): void {
    this.channel.appendLine("");
    this.channel.appendLine("Error");
    this.channel.appendLine("-----");
    this.channel.appendLine(message);
    if (stderr) {
      this.channel.appendLine("");
      this.channel.appendLine("stderr");
      this.channel.appendLine("------");
      this.channel.appendLine(stderr);
    }
    this.channel.appendLine("");
    this.channel.appendLine("Troubleshooting: ensure RoboPilot is installed with `pip install robopilot` or configure robopilot.executablePath.");
  }

  show(): void {
    this.channel.show(true);
  }

  dispose(): void {
    this.channel.dispose();
  }
}
