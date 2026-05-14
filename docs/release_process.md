# Release Process

This document describes the lightweight release process for RoboPilot.

## Version Bump

Update the project version in:

- `pyproject.toml`
- generated package template version strings, if the release should update generated demo metadata
- committed static demo package metadata, if it is intentionally refreshed

Use semantic versioning for normal releases:

```txt
v0.24.0
v1.0.0-rc.1
v1.0.0
```

For Python package metadata, release candidates must use the PEP 440 form in `pyproject.toml`:

```toml
version = "1.0.0rc1"
```

For the v2.0.0 release candidate, use:

```toml
version = "2.0.0rc1"
```

Use the human-facing git tag form for tags and GitHub Releases:

```txt
v1.0.0-rc.1
```

For v2.0.0-rc.1:

```txt
v2.0.0-rc.1
```

PyPI displays the PEP 440 package version (`2.0.0rc1`). GitHub Releases and documentation should use the human-facing form (`v2.0.0-rc.1`). The final v2.0 release should use `2.0.0` in `pyproject.toml` and `v2.0.0` for the tag.

The VSCode extension is versioned separately from the Python package. Do not change `vscode-extension/package.json` for a Python-only RC unless the extension package itself changes.

## Changelog

Update `CHANGELOG.md` under `Unreleased` before cutting a release.

For a release tag, move relevant notes under a dated release heading when appropriate:

```md
## [1.0.0] - YYYY-MM-DD
```

Release candidate heading example:

```md
## [2.0.0-rc.1] - YYYY-MM-DD
```

Keep release notes focused on user-visible changes, documentation, safety behavior, compatibility, and known limitations.

## Test Checklist

Run the full suite:

```bash
python -m pytest
```

Windows fallback:

```bash
python -m pytest --basetemp=".pytest_tmp" -p no:cacheprovider
```

Manually verify:

```bash
robopilot --help
robopilot detect --help
robopilot migrate-plan --help
robopilot apply --help
robopilot history --help
```

## Build Checklist

Install local packaging tools:

```bash
python -m pip install -U build twine
```

Build the source distribution and wheel:

```bash
python -m build
```

Check the built distributions before publishing:

```bash
python -m twine check dist/*
```

Do not commit `dist/`, `build/`, or `*.egg-info` artifacts.

## Commit Convention

Use concise conventional commits. Example:

```bash
git commit -m "chore: prepare vX.Y.Z release"
```

Other useful prefixes:

- `docs:` documentation-only changes
- `test:` test-only changes
- `fix:` bug fixes
- `chore:` release, metadata, or maintenance work

## Push and CI

Push the release preparation branch and wait for GitHub Actions to pass.

```bash
git push
```

Do not tag a release until CI is green or the failure is understood and documented.

## Tagging

Use annotated tags when cutting a release.

Release candidate example:

```bash
git tag -a v1.0.0-rc.1 -m "RoboPilot v1.0.0-rc.1"
git push origin v1.0.0-rc.1
```

Stable release example:

```bash
git tag -a v1.0.0 -m "RoboPilot v1.0.0"
git push origin v1.0.0
```

## GitHub Release Checklist

The GitHub Release description should include:

- release summary
- user-facing changes
- safety model notes
- compatibility notes
- known limitations
- test result summary
- upgrade notes, if any
- link to `CHANGELOG.md`

Publishing should use PyPI Trusted Publishing through the `pypi` GitHub environment when possible. Do not commit PyPI or TestPyPI tokens.

Optional TestPyPI validation can use the dedicated TestPyPI workflow before the production release. After publishing, verify installation in a fresh environment:

```bash
python -m pip install -U robopilot
robopilot --help
```

## Rollback Plan

If a release has a problem:

1. Mark the GitHub Release as pre-release or add a warning note.
2. Open an issue describing the failure and affected versions.
3. Revert or fix on a new branch.
4. Run the full test suite and manual CLI checks.
5. Publish a patch release or replacement release candidate.

Avoid deleting tags unless absolutely necessary and coordinated, because users may already have fetched them.
