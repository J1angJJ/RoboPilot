# VSCode Marketplace 发布说明

RoboPilot VSCode extension 已在 Visual Studio Marketplace 上架，extension id 是：

```txt
j1angjj.robopilot-vscode
```

本文说明安装方式、发布状态和后续更新的安全边界。

## 安装

用户仍然需要先安装 RoboPilot CLI：

```bash
pip install robopilot
```

然后安装 Marketplace 扩展：

```bash
code --install-extension j1angjj.robopilot-vscode
```

如果 VSCode 找不到 `robopilot`，请配置：

```txt
robopilot.executablePath
```

## 发布边界

Marketplace 发布独立于 Python package 发布和本地 VSIX 打包。

RoboPilot VSCode extension 仍然是已安装 `robopilot` CLI 的薄包装。扩展不会运行 ROS、ROS2、`catkin_make`、`colcon`、launch 文件或生成节点，也不会自动完成完整 ROS1 到 ROS2 迁移。

RoboPilot Python package 和 VSCode extension 分开版本化。RoboPilot v2.0.x Python package 发布线使用自己的包版本；除非有单独的 extension release 任务，否则 VSCode extension 保持自己的 Marketplace 版本。

## Publisher id

当前 publisher 是：

```txt
j1angjj
```

当前 extension id 是：

```txt
j1angjj.robopilot-vscode
```

后续发布更新前，必须确认 Visual Studio Marketplace 的 publisher id 与 `vscode-extension/package.json` 中的 `publisher` 字段一致。

## Token 安全

`vsce publish` 需要 Personal Access Token。推荐 GitHub Secret 名称：

```txt
VSCE_PAT
```

不要提交 PAT。不要把 PAT 写入 `.env`、文档示例、package metadata、日志或 workflow 输出。

## 后续更新流程

1. 更新 `vscode-extension/package.json` version。
2. 更新 `vscode-extension/CHANGELOG.md`。
3. 运行本地检查：

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

4. 确认 publisher id 和 `VSCE_PAT`。
5. 通过手动触发 `.github/workflows/vscode-publish.yml` 或明确确认的 `vsce publish` 发布。
6. 发布后验证 Marketplace listing。

workflow 不应在 push 或 pull request 上自动发布，也不应打印 token。

## 发布后验证

每次发布后都应确认：

- Marketplace listing 标题、说明、README、license、repository link 和版本正确。
- extension id 是 `j1angjj.robopilot-vscode`。
- 可以在干净 VSCode 环境中安装：

```bash
code --install-extension j1angjj.robopilot-vscode
```

- `robopilot.executablePath` 能指向已安装的 RoboPilot CLI。
- listing 仍然说明不需要 ROS、ROS2、catkin、colcon、launch 执行或生成节点执行。

## 发布失败时

- 不要把 token 写入仓库文件后重试。
- 先判断失败原因：publisher id、PAT scope、版本已存在、package validation、网络或 Marketplace 服务问题。
- 如果怀疑 token 暴露，立即撤销并重建 PAT。
- 如果更新发布失败，用户文档应继续指向最后一个已验证的 Marketplace 版本。
