# VSCode Marketplace 发布说明

本文用于准备未来的 Visual Studio Marketplace 发布。它不是自动发布流程。除非发布任务明确要求，不要发布扩展。

## 发布边界

Marketplace 发布独立于 Python 包发布和本地 VSIX 打包。

RoboPilot VSCode extension 仍然只是 RoboPilot CLI 的薄包装。发布扩展不能引入 ROS、ROS2、`catkin_make`、`colcon`、launch 执行、生成节点执行或新的 LLM 行为。

## Publisher id

扩展当前使用：

```txt
publisher: j1angjj
```

发布前必须确认 Visual Studio Marketplace 的 publisher id 与这个值完全一致。如果不一致，需要先更新 `vscode-extension/package.json`、文档和安装示例。

## Token 安全

`vsce publish` 需要 Personal Access Token。推荐 GitHub Secret 名称：

```txt
VSCE_PAT
```

不要提交 PAT。不要把 PAT 写入 `.env`、文档、package metadata、日志或 workflow 输出。

## 手动发布前检查

1. 创建或确认 Visual Studio Marketplace publisher。
2. 创建带有 Marketplace 发布权限的 Azure DevOps PAT。
3. 如果使用 GitHub Actions，把 PAT 添加为 `VSCE_PAT` secret。
4. 检查 `vscode-extension/package.json` 的 publisher、name、displayName、description、repository、license、categories 和 keywords。
5. 检查 `vscode-extension/README.md` 和 `vscode-extension/CHANGELOG.md`。
6. 先本地打包：

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

## 未来发布方式

手动发布：

```bash
cd vscode-extension
npx vsce publish
```

如果使用 GitHub Actions，发布 workflow 应该只允许 `workflow_dispatch` 手动触发，并使用 `secrets.VSCE_PAT`。不要在 push 或 pull request 上自动发布。

## 发布后验证

发布成功后再更新 README，说明 Marketplace 可用。验证内容包括 listing 标题、README、license、repository link、版本、安装流程和 `robopilot.executablePath` 配置。

如果没有实际发布，文档必须继续说“Marketplace publish preparation”，不能声称已经上架。
