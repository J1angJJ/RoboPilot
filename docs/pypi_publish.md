# PyPI Publishing

This document describes the intended PyPI publishing setup for RoboPilot.

## PyPI Account Setup

Maintainers should create accounts on:

- PyPI: https://pypi.org/
- TestPyPI: https://test.pypi.org/

Enable two-factor authentication on both accounts.

## Trusted Publishing

RoboPilot should prefer PyPI Trusted Publishing over long-lived API tokens.

For PyPI, configure a pending publisher matching:

```txt
Project name: robopilot
Owner: J1angJJ
Repository: RoboPilot
Workflow: publish.yml
Environment: pypi
```

The workflow uses GitHub's OIDC identity token. No PyPI token should be committed.

## TestPyPI

TestPyPI is useful before the first real publish or when validating release automation.

The optional workflow is:

```txt
.github/workflows/test-publish.yml
```

It should publish to TestPyPI only through a dedicated environment such as `testpypi`.

## Local Build Verification

Before publishing:

```bash
python -m pip install -U build twine
python -m build
python -m twine check dist/*
```

## GitHub Actions Publishing Flow

The production publishing workflow is:

```txt
.github/workflows/publish.yml
```

It is intended for GitHub Release or manual release workflow use. The workflow should:

- check out the repository
- set up Python
- install build tooling
- build sdist and wheel
- run `twine check`
- publish through Trusted Publishing

## Secrets and Tokens

Do not commit:

- PyPI API tokens
- TestPyPI API tokens
- `.pypirc`
- local credentials
- environment files containing secrets

If a token is accidentally exposed, revoke it immediately and rotate any related credentials.

## Verify Installation After Release

After a PyPI release:

```bash
python -m pip install -U robopilot
robopilot --help
robopilot detect --help
```

For TestPyPI:

```bash
python -m pip install -i https://test.pypi.org/simple/ robopilot
robopilot --help
```
