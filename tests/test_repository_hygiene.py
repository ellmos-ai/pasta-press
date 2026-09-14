# SPDX-License-Identifier: MIT
"""Vertragstests für Repository-Hygiene, CI-Härtung, PEP 621 und Governance."""

from __future__ import annotations

import compileall
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parent.parent


def test_gitignore_contains_multihost_and_lock_patterns():
    """Prüft, ob .gitignore vor Multi-Host-Konflikten, Locks und Caches schützt."""
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    pflicht_muster = [
        "LOCK",
        "LOCK.*",
        "LOCK*.txt",
        "uv.lock",
        "* (kopie)*",
        "* (copy)*",
        "*-WORKSTATION*",
        "*-ASUS*",
        "*-LAPTOP*",
        "*-Mac Studio*",
        ".coverage",
        "coverage/",
    ]
    for muster in pflicht_muster:
        assert muster in gitignore, f"Muster '{muster}' fehlt in .gitignore"


def test_ci_workflows_exist_and_are_hardened():
    """CI-Workflows müssen existieren und Timeout- sowie Concurrency-Schutz tragen."""
    workflows_dir = ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir(), ".github/workflows Verzeichnis fehlt"

    erwartete_workflows = ["ci.yml", "stale.yml", "welcome.yml"]
    for wf in erwartete_workflows:
        pfad = workflows_dir / wf
        assert pfad.is_file(), f"Workflow-Datei {wf} fehlt"
        inhalt = pfad.read_text(encoding="utf-8")
        assert "timeout-minutes:" in inhalt, f"Workflow {wf} fehlt 'timeout-minutes'"
        assert "concurrency:" in inhalt, f"Workflow {wf} fehlt 'concurrency'"
        assert "cancel-in-progress: true" in inhalt, f"Workflow {wf} bricht veraltete Läufe nicht ab"


def test_pyproject_pep621_urls_and_pytest_options():
    """pyproject.toml muss PEP 621 Projekt-URLs und verbindliche Pytest-Flags führen."""
    pyproject_pfad = ROOT / "pyproject.toml"
    assert pyproject_pfad.is_file(), "pyproject.toml fehlt"

    with pyproject_pfad.open("rb") as f:
        data = tomllib.load(f)

    project = data.get("project", {})
    urls = project.get("urls", {})
    erwartete_urls = [
        "Repository",
        "Issues",
        "Documentation",
        "German Documentation",
        "Security Policy",
        "LLM Context Index",
        "Marketing Log",
    ]
    for key in erwartete_urls:
        assert key in urls, f"PEP 621 URL '{key}' fehlt in pyproject.toml [project.urls]"

    # Pytest-Flags
    pytest_opts = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    addopts = pytest_opts.get("addopts", "")
    assert "-ra" in addopts and "-v" in addopts, f"pytest addopts unvollständig: {addopts}"


def test_version_parity_across_manifests():
    """Version 1.2.2 muss über alle Manifeste, Module und Kontextdateien harmonisiert sein."""
    # pyproject.toml
    with (ROOT / "pyproject.toml").open("rb") as f:
        pyproject_ver = tomllib.load(f)["project"]["version"]

    # pastapress/__init__.py
    from pastapress import __version__ as init_ver

    # llms.txt
    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert f"Version: {pyproject_ver}" in llms_text, "Version in llms.txt weicht ab"

    # CHANGELOG.md
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## [{pyproject_ver}]" in changelog, f"Changelog führt Version {pyproject_ver} nicht"

    # MARKETING-LOG.txt
    marketing_log = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert f"Version: {pyproject_ver}" in marketing_log, f"MARKETING-LOG führt Version {pyproject_ver} nicht"

    assert pyproject_ver == init_ver == "1.2.2", (
        f"Versionsinkonsistenz: pyproject={pyproject_ver}, __init__={init_ver}"
    )


def test_security_policy_and_sla():
    """SECURITY.md muss vorhanden sein und Kernversprechen sowie die 48h-SLA enthalten."""
    sec_pfad = ROOT / "SECURITY.md"
    assert sec_pfad.is_file(), "SECURITY.md fehlt"
    inhalt = sec_pfad.read_text(encoding="utf-8")
    assert "48 hours" in inhalt or "48 Stunden" in inhalt, "48h SLA fehlt in SECURITY.md"
    assert "Local-First" in inhalt or "Zero External Network Egress" in inhalt, "Local-First fehlt in SECURITY.md"
    assert "RunAsInvoker" in inhalt, "RunAsInvoker fehlt in SECURITY.md"


def test_marketing_log_intact():
    """MARKETING-LOG.txt muss vorhanden sein und Governance-Invarianten aufführen."""
    log_pfad = ROOT / "MARKETING-LOG.txt"
    assert log_pfad.is_file(), "MARKETING-LOG.txt fehlt"
    inhalt = log_pfad.read_text(encoding="utf-8")
    assert "INV-LOCAL-01" in inhalt and "INV-LOCAL-10" in inhalt, "Invarianten fehlen in MARKETING-LOG.txt"
    assert "[PERSONA-01]" in inhalt and "[PERSONA-04]" in inhalt, "Personas fehlen in MARKETING-LOG.txt"


def test_syntax_compilation():
    """pastapress, tests und docs müssen ohne Syntaxfehler kompilieren."""
    erfolg = compileall.compile_dir(str(ROOT / "pastapress"), quiet=1)
    erfolg = erfolg and compileall.compile_dir(str(ROOT / "tests"), quiet=1)
    erfolg = erfolg and compileall.compile_dir(str(ROOT / "docs"), quiet=1)
    assert erfolg, "Syntaxfehler bei compileall gefunden"
