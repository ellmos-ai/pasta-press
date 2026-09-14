# Security Policy

## Supported Versions

Currently, only the `master` branch and latest releases are supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.2.x   | :white_check_mark: |
| 1.x     | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities (e.g. prompt injection, unauthorized
network access in dependencies, unhandled file I/O exploits) privately via
**GitHub Security Advisories** ("Report a vulnerability" on the Security tab
of this repository).

Do NOT create public issues for security vulnerabilities.

### Service Level Agreement (SLA)
- **Initial Response:** Within **48 hours** of report submission.
- **Triage & Status Update:** Within **5 business days**.
- **Fix Delivery & Disclosure:** Coordinated release and security advisory publication upon patch verification.

## Data Privacy & Architectural Invariants

- **Local-First & Zero External Network Egress:** PastaPress processes all text inputs locally by communicating exclusively with a local or self-hosted Ollama instance (`http://localhost:11434` by default). No text data, telemetric payloads, or usage statistics are transmitted to external cloud APIs or third parties.
- **Unprivileged User Mode (`RunAsInvoker`):** The tool requires no administrative, root, or elevated privileges. All operations execute strictly within the security context of the invoking user.
- **Scope & Disclosure Boundaries:** PastaPress performs generative, paragraph-level paraphrasing and structural delimiter reassembly. It does not scan for, strip, or sanitize invisible Unicode steganography, C2PA claims, or binary file container metadata. Users remain responsible for reviewing generated text and fulfilling legal or organizational AI-disclosure obligations.
