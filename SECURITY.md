# Security Policy

This repository is a research benchmark and does not process production secrets
by default.

## Reporting a vulnerability

If you find a security issue in the benchmark code or documentation, please open
a GitHub issue with enough detail to reproduce the problem. Do not include
private credentials, API keys, or confidential data in issues.

## Handling secrets

The default benchmark does not require external API keys. If you extend the
benchmark to use hosted embedding or generation services, store credentials
outside the repository using environment variables or a local `.env` file that
is excluded from version control.
