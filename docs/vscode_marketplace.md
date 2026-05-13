# VSCode Marketplace Publishing

This document prepares RoboPilot's VSCode extension for future Visual Studio Marketplace publishing. It is preparation only. Do not publish the extension unless a release task explicitly asks for it.

## Publishing Boundary

Marketplace publishing is separate from local VSIX packaging and from the Python package release process.

RoboPilot's VSCode extension remains a thin wrapper over the installed RoboPilot CLI. Publishing the extension must not add ROS, ROS2, catkin, colcon, launch execution, generated node execution, or new LLM behavior.

## Publisher Id

Visual Studio Marketplace requires a publisher account.

The extension currently uses:

```txt
publisher: j1angjj
```

Before publishing, confirm that the Marketplace publisher id exactly matches this value. If the real Marketplace publisher id differs, update `vscode-extension/package.json`, docs, and install/uninstall examples before publishing.

## Token Safety

Publishing with `vsce` requires a Personal Access Token.

Recommended GitHub secret name:

```txt
VSCE_PAT
```

Do not commit the token. Do not place it in `.env`, package metadata, documentation examples, logs, or workflow output.

## Manual Preparation Checklist

1. Create or confirm the Visual Studio Marketplace publisher.
2. Create an Azure DevOps Personal Access Token with the required Marketplace publishing scope.
3. Add the PAT to GitHub repository secrets as `VSCE_PAT` if GitHub Actions publishing will be used.
4. Verify `vscode-extension/package.json` has the correct `publisher`, `name`, `displayName`, `description`, `repository`, `license`, `categories`, and `keywords`.
5. Verify `vscode-extension/README.md` and `vscode-extension/CHANGELOG.md` are current.
6. Run local package checks before any publish attempt:

```bash
cd vscode-extension
npm install
npm run compile
npm test
npm run package
```

## Local Packaging

Use the local VSIX flow for final review:

```bash
cd vscode-extension
npm run package
```

Install the generated package locally:

```bash
code --install-extension robopilot-vscode-0.4.0.vsix
```

Verify the extension loads, the command palette entries appear, and `RoboPilot: Show Output` works before considering Marketplace publishing.

## Future Manual Publish

After the checklist is complete and the release owner explicitly decides to publish:

```bash
cd vscode-extension
npx vsce publish
```

If prompted, provide the Marketplace PAT through the secure `vsce` flow. Do not paste tokens into committed files or issue comments.

## Future GitHub Actions Publish

The repository may include a manually triggered workflow at:

```txt
.github/workflows/vscode-publish.yml
```

That workflow should use `workflow_dispatch`, Node 20, `npm ci`, compile, tests, local package, and `npx vsce publish --pat ${{ secrets.VSCE_PAT }}`. It must not run on normal push or pull request events.

Only run the workflow after confirming the publisher id, extension version, changelog, README, local VSIX, and `VSCE_PAT` secret.

## Listing Verification

After a future publish:

- Confirm the Marketplace listing title, description, README, license, repository link, and version.
- Install the extension from the Marketplace in a clean VSCode profile.
- Confirm `robopilot.executablePath` works with an installed RoboPilot CLI.
- Confirm the extension still states that RoboPilot does not require ROS, ROS2, catkin, colcon, launch execution, or generated node execution.

## Rollback And Deprecation

Treat Marketplace rollback conservatively:

- Prefer publishing a fixed patch version over deleting history.
- Unpublish only if the package is unsafe, contains secrets, or has a severe metadata problem.
- If a release is superseded, document the replacement version in the changelog.
- Never rotate or expose PATs through repository files; revoke and recreate tokens if exposure is suspected.
