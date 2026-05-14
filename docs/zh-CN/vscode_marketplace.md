# VSCode Marketplace 发布说明

本文说明 RoboPilot VSCode extension 发布到 Visual Studio Marketplace 前后的安全检查。发布必须是显式、手动的。除非发布任务明确要求，不要发布扩展。

## 发布边界

Marketplace 发布独立于本地 VSIX 打包，也独立于 Python package 发布。

RoboPilot VSCode extension 仍然是已安装 `robopilot` CLI 的薄包装。发布扩展不能引入 ROS、ROS2、`catkin_make`、`colcon`、launch 执行、生成节点执行或新的 LLM 行为。

## Publisher id

扩展当前使用：

```txt
publisher: j1angjj
```

预期扩展 id 是：

```txt
j1angjj.robopilot-vscode
```

发布前必须确认 Visual Studio Marketplace 的 publisher id 与 `vscode-extension/package.json` 中的 `publisher` 字段完全一致。如果不一致，先更新 `package.json`、文档和安装示例，再发布。

## Token 安全

`vsce publish` 需要 Personal Access Token。推荐 GitHub Secret 名称：

```txt
VSCE_PAT
```

不要提交 PAT。不要把 PAT 写入 `.env`、文档示例、package metadata、日志或 workflow 输出。

## 发布前检查

1. 创建或确认 Visual Studio Marketplace publisher。
2. 确认 publisher id 是 `j1angjj`。
3. 创建具有 Marketplace 发布权限的 Azure DevOps PAT。
4. 如果使用 GitHub Actions，把 PAT 添加为仓库 secret `VSCE_PAT`。
5. 检查 `vscode-extension/package.json` 的 `publisher`、`name`、`displayName`、`description`、`repository`、`license`、`categories` 和 `keywords`。
6. 检查 `vscode-extension/README.md` 和 `vscode-extension/CHANGELOG.md`。
7. 本地运行打包检查：

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

8. 确认没有真实 token 被提交。

## 本地 VSIX 检查

安装本地包进行最终检查：

```bash
code --install-extension robopilot-vscode-0.5.0.vsix
```

确认扩展能加载，Command Palette 中能看到 RoboPilot 命令，`RoboPilot: Show Output` 可用。

## 通过 GitHub Actions 发布

`.github/workflows/vscode-publish.yml` 应该只允许 `workflow_dispatch` 手动触发。

发布步骤：

1. 确认 publisher id 和 `VSCE_PAT`。
2. 打开 GitHub Actions。
3. 选择 `VSCode Marketplace Publish`。
4. 手动触发 workflow。
5. 等待 compile、test、package 和 publish 步骤完成。

workflow 不应在 push 或 pull request 上自动发布，也不应打印 token。

## 手动发布

如果发布负责人明确决定本地发布：

```bash
cd vscode-extension
npx vsce publish
```

通过 `vsce` 的安全提示提供 PAT。不要把 token 贴到提交、issue 或文档里。

## 发布后验证

发布成功后：

- 确认 Marketplace listing 标题、说明、README、license、repository link 和版本。
- 确认 extension id 是 `j1angjj.robopilot-vscode`。
- 在干净 VSCode 环境中安装：

```bash
code --install-extension j1angjj.robopilot-vscode
```

- 确认 `robopilot.executablePath` 能指向已安装的 RoboPilot CLI。
- 确认 listing 仍然说明不需要 ROS、ROS2、catkin、colcon、launch 执行或生成节点执行。

只有在 listing 验证成功后，README 才能声称 Marketplace 可用。

## 之后如何更新

1. 更新 `vscode-extension/package.json` version。
2. 更新 `vscode-extension/CHANGELOG.md`。
3. 运行 compile、test 和 local package。
4. 本地验证 VSIX。
5. 确认 publisher id 和 `VSCE_PAT`。
6. 发布并验证 Marketplace listing。

## 发布失败时

- 不要把 token 写入仓库文件后重试。
- 先判断失败原因：publisher id、PAT scope、版本已存在、package validation、网络或 Marketplace 服务问题。
- 如果怀疑 token 暴露，立即撤销并重建 PAT。
- 如果版本可能部分发布，先检查 Marketplace listing。
- 在 listing 验证成功前，README 应继续使用“Marketplace publishing is prepared”这类表述。
