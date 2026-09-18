# Third-Party Licenses & Governance Invariants

This document details the third-party dependencies, license attributes, and governance
invariants for **pasta-press** (Version 1.2.2).

The repository [`LICENSE`](LICENSE) (MIT License, Copyright (c) 2026 Lukas Geiger)
covers **only the code, prompts, and documentation written for this project**.
External libraries and runtime dependencies retain their respective copyright notices
and license terms.

---

## 1. Runtime & CLI Dependencies

| Component | Upstream / Package | License | Role / Scope |
|---|---|---|---|
| **requests** | `requests>=2.28` (PyPI) | Apache-2.0 | HTTP communication with local Ollama API |
| **click** | `click>=8.0` (PyPI) | BSD-3-Clause | CLI command dispatcher, arguments, options |
| **pypandoc** | `pypandoc>=1.11` (PyPI, optional) | MIT | Python wrapper for external pandoc binary conversion |
| **Python Standard Library** | Python 3.10+ | PSF-2.0 | Standard data structures, regex, json, path operations |

---

## 2. External Binary Isolation (Pandoc)

- **Component**: Pandoc (Universal document converter)
- **License**: GNU General Public License v2.0 or later (GPL-2.0-or-later)
- **Architecture & Isolation Boundary**:
  - Pandoc is **not vendored** and **not statically linked** into `pasta-press`.
  - Pandoc is invoked exclusively as an **optional, independent external CLI sub-process** via `pypandoc` for document format translation (`.docx`, `.odt`, `.rtf` &rarr; Markdown).
  - Native text workflows (`.txt`, `.md`, `.json`, `.csv`, `.yaml`, `.tex`) do not invoke Pandoc.
  - **Zero-Copyleft Contagion Guarantee**: The separate sub-process execution model across standard OS file descriptors preserves the independent, permissive MIT licensing of `pasta-press`.

---

## 3. Execution Security & User Privilege Model

- **Non-Elevation (`RunAsInvoker`)**: `pasta-press` executes strictly in user space. It never requests or requires administrative (`Administrator` / `root`) elevation.
- **Local-First / Zero External Egress**:
  - All LLM interactions are routed strictly to the configured local or intranet Ollama instance (default `http://localhost:11434`).
  - No telemetry, analytics, telemetry tokens, or external API calls exist.
  - Network activity is restricted to local loopback or explicit LAN endpoints.

---

## 4. Governance & Quality Invariants (INV-LOCAL-01..INV-LOCAL-10)

| ID | Invariant Name | Specification & Guarantee |
|---|---|---|
| **INV-LOCAL-01** | Zero External Egress | Strict local-first architecture; 100% loopback/LAN Ollama execution. |
| **INV-LOCAL-02** | Unprivileged Execution | Conforms to `RunAsInvoker`; zero privilege elevation requirements. |
| **INV-LOCAL-03** | Permissive Licensing | MIT license for project code; permissive runtime dependencies. |
| **INV-LOCAL-04** | Deterministic Reassembly | Exact preservation of paragraph delimiters and boundary whitespace. |
| **INV-LOCAL-05** | Transparent Failure Fallback | Failed chunks fallback to original text; chunk metrics reported. |
| **INV-LOCAL-06** | Honest AI Disclosure | Generative paraphrasing; no false watermark immunity claims; disclosure upheld. |
| **INV-LOCAL-07** | Multi-Host Sync Guardrails | Gitignore hardened against multi-host conflict files and lock files. |
| **INV-LOCAL-08** | PEP 621 Standardized | Declarative build system and tool configuration in `pyproject.toml`. |
| **INV-LOCAL-09** | Manifest Version Parity | Synchronized versioning (1.2.2) across packaging, CLI, and docs. |
| **INV-LOCAL-10** | 48-Hour Security SLA | Documented coordinated vulnerability response policy in `SECURITY.md`. |

---

## 5. SPDX License Expressions

```spdx
PackageName: pasta-press
PackageVersion: 1.2.2
PackageDownloadLocation: https://github.com/ellmos-ai/pasta-press
PackageLicenseDeclared: MIT
PackageLicenseConcluded: MIT
FilesAnalyzed: false
PackageCopyrightText: 2026 Lukas Geiger
```
