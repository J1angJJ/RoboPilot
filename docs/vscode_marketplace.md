# VSCode Marketplace Publishing

RoboPilot's VSCode extension is available from Visual Studio Marketplace as `j1angjj.robopilot-vscode`.

This document records the publishing status, install steps, and safety checklist for future updates. Publishing must remain explicit and manual. Do not publish updates unless a release task explicitly asks for it.

## Publishing Boundary

Marketplace publishing is separate from local VSIX packaging and from the Python package release process.

RoboPilot's VSCode extension remains a thin wrapper over the installed RoboPilot CLI. Publishing the extension does not add ROS, ROS2, catkin, colcon, launch execution, generated node execution, or new LLM behavior.

The RoboPilot Python package and VSCode extension are versioned separately. RoboPilot's v2.0.x Python package release line uses its own package version; the VSCode extension remains at its own Marketplace version unless an extension release task changes it.

Users still need the RoboPilot CLI installed:

```bash
pip install robopilot
```

Install the Marketplace extension:

```bash
code --install-extension j1angjj.robopilot-vscode
```

## Publisher Id

Visual Studio Marketplace requires a publisher account.

The extension currently uses:

```txt
publisher: j1angjj
```

The expected extension id is:

```txt
j1angjj.robopilot-vscode
```

The Marketplace / VSIX icon is packaged from `vscode-extension/assets/robopilot-cover.png`, copied from the RoboPilot branding cover image under `docs/assets/branding/`.

Before publishing, confirm that the Marketplace publisher id exactly matches the `publisher` field in `vscode-extension/package.json`. If the real Marketplace publisher id differs, update `vscode-extension/package.json`, docs, and install/uninstall examples before publishing.

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
6. Verify no real token is committed:

```bash
git grep -n "VSCE_PAT\|pat_" -- . ":!docs/vscode_marketplace.md" ":!docs/zh-CN/vscode_marketplace.md"
```

7. Run local package checks before any publish attempt:

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
code --install-extension robopilot-vscode-0.5.0.vsix
```

Verify the extension loads, the command palette entries appear, and `RoboPilot: Show Output` works before considering Marketplace publishing.

## Future Manual Publish Updates

After the checklist is complete and the release owner explicitly decides to publish an update:

```bash
cd vscode-extension
npx vsce publish
```

If prompted, provide the Marketplace PAT through the secure `vsce` flow. Do not paste tokens into committed files or issue comments.

## Future GitHub Actions Publish Updates

The repository may include a manually triggered workflow at:

```txt
.github/workflows/vscode-publish.yml
```

That workflow should use `workflow_dispatch`, Node 20, `npm ci`, compile, tests, local package, and `npx vsce publish --pat ${{ secrets.VSCE_PAT }}`. It must not run on normal push or pull request events.

Only run the workflow after confirming the publisher id, extension version, changelog, README, local VSIX, and `VSCE_PAT` secret.

## Publishing Through GitHub Actions

Use the manually triggered workflow only after the preflight checklist passes:

1. Confirm the Visual Studio Marketplace publisher is `j1angjj`.
2. Add `VSCE_PAT` to GitHub repository secrets.
3. Open GitHub Actions.
4. Select `VSCode Marketplace Publish`.
5. Run workflow manually with `workflow_dispatch`.
6. Wait for compile, tests, package, and publish steps to finish.

The workflow must not echo the token and must not run on push or pull request events.

## Listing Verification

After each publish:

- Confirm the Marketplace listing title, description, README, license, repository link, and version.
- Install the extension from the Marketplace in a clean VSCode profile.
- Confirm the extension id is `j1angjj.robopilot-vscode`.
- Confirm `robopilot.executablePath` works with an installed RoboPilot CLI.
- Confirm the extension still states that RoboPilot does not require ROS, ROS2, catkin, colcon, launch execution, or generated node execution.

Install after publishing:

```bash
code --install-extension j1angjj.robopilot-vscode
```

The current verified extension id is `j1angjj.robopilot-vscode`.

## Updating Later

For later extension releases:

1. Update `vscode-extension/package.json` version.
2. Update `vscode-extension/CHANGELOG.md`.
3. Run compile, tests, and local package.
4. Verify the VSIX locally.
5. Publish only after confirming `VSCE_PAT` and publisher id.
6. Verify the Marketplace listing after publish.

Do not change Python package version solely for an extension-only patch unless the repository release plan calls for a coordinated release.

## If Publishing Fails

- Do not retry blindly with edited tokens in committed files.
- Read the failing workflow step and confirm whether the issue is publisher id, PAT scope, version already published, package validation, or network/service failure.
- Rotate the PAT if exposure is suspected.
- If the version was partially published, verify the Marketplace listing before deciding whether to publish a patch version.
- If an update fails before listing verification, keep user-facing install docs pointed at the last verified Marketplace release.

## Rollback And Deprecation

Treat Marketplace rollback conservatively:

- Prefer publishing a fixed patch version over deleting history.
- Unpublish only if the package is unsafe, contains secrets, or has a severe metadata problem.
- If a release is superseded, document the replacement version in the changelog.
- Never rotate or expose PATs through repository files; revoke and recreate tokens if exposure is suspected.
