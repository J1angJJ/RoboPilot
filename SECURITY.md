# Security Policy

## Reporting Security Issues

Please do not post security-sensitive details in public issues.

Report security issues privately through GitHub's private vulnerability reporting if enabled, or contact the maintainer through a private channel listed on the project profile.

## Do Not Share Secrets

Do not include secrets in issues, discussions, logs, screenshots, examples, or pull requests.

Examples:

- PyPI tokens
- TestPyPI tokens
- OpenAI API keys
- `.env` files
- `.pypirc`
- private repository URLs
- local credentials

## Security-Sensitive Areas

For RoboPilot, security-sensitive behavior includes:

- handling API keys for optional LLM integrations
- packaging and publishing credentials
- file-writing apply workflows
- rollback from backup directories
- static inspection of untrusted projects

RoboPilot should not execute user ROS code, launch files, generated nodes, `catkin_make`, or `colcon` by default.

## Maintainer Response

Security reports should be triaged for:

- impact
- affected versions
- reproduction steps
- workaround or mitigation
- patch and release plan
