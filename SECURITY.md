# Security Policy

## Supported Versions

Currently, only the `master` branch is supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities (e.g. prompt injection, unauthorized
network access in the dependencies, unhandled file I/O exploits) privately via
**GitHub Security Advisories** ("Report a vulnerability" on the Security tab
of this repository).

Do NOT create public issues for security vulnerabilities.

## Data Privacy

PastaPress processes all text inputs locally by sending them to a
locally-hosted Ollama instance. No text data is sent to external cloud APIs or
third parties.
Ensure that your `config.json` points to an Ollama host you control
(`http://localhost:11434` by default).
