# VSCode 本地 VSIX 打包

本文说明如何为 RoboPilot VSCode extension 生成本地 `.vsix`，用于本机安装测试。这个流程不会发布到 Visual Studio Marketplace。

## 要求

- Node.js 20
- npm
- 已安装 RoboPilot CLI

安装 CLI：

```bash
pip install robopilot
```

源码开发时：

```bash
python -m pip install -e ".[dev]"
```

## 构建和打包

从仓库根目录运行：

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

预期输出：

```txt
vscode-extension/robopilot-vscode-<version>.vsix
```

## 本地安装

```bash
code --install-extension robopilot-vscode-0.5.0.vsix
```

卸载：

```bash
code --uninstall-extension j1angjj.robopilot-vscode
```

如果没有 `code` 命令，可以从 VSCode Command Palette 安装 `Shell Command: Install 'code' command in PATH`，或者在 Extensions 视图中手动安装 VSIX。

## 配置

如果 VSCode 找不到 RoboPilot CLI，设置：

```txt
robopilot.executablePath
```

conda 用户可能需要填入环境中的绝对路径。

扩展默认输出目录：

```txt
.robopilot_vscode
```

如果旧 migration plan、scaffold 或 report 影响测试，可以手动清理这个目录。

## Marketplace 边界

本地 VSIX 打包不等于 Marketplace 发布。当前 Marketplace extension id 是 `j1angjj.robopilot-vscode`。后续发布新版本前必须确认 publisher id、README、CHANGELOG、版本号和 token 安全。
