from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import typer

import envctl.cli.commands.vault.commands.audit as vault_audit_module
from envctl.domain.operations import VaultAuditFileResult, VaultAuditProjectResult


def test_vault_audit_command_reports_empty_vault(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_audit",
        lambda: (None, ()),
    )
    monkeypatch.setattr(vault_audit_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        vault_audit_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    vault_audit_module.vault_audit_command()

    output = captured["output"]
    assert captured["output_format"] == "text"
    assert output.metadata["kind"] == "vault_audit"
    assert output.metadata["projects"] == []
    assert output.metadata["summary"]["total_projects"] == 0
    assert output.metadata["ok"] is True
    assert output.messages[0].level == "warning"
    assert "No persisted vault projects were found" in output.messages[0].text


def test_vault_audit_command_reports_healthy_projects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    projects = (
        VaultAuditProjectResult(
            project_slug="demo-app",
            project_id="prj_aaaaaaaaaaaaaaaa",
            key_path=Path("/tmp/vault/demo-app--prj_aaaaaaaaaaaaaaaa/master.key"),
            key_exists=True,
            files=(
                VaultAuditFileResult(
                    path=Path("/tmp/vault/demo-app--prj_aaaaaaaaaaaaaaaa/values.env"),
                    state="encrypted",
                    detail="Encrypted and readable.",
                    private_permissions=True,
                ),
            ),
        ),
    )

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_audit",
        lambda: (None, projects),
    )
    monkeypatch.setattr(vault_audit_module, "is_json_output", lambda: True)
    monkeypatch.setattr(
        vault_audit_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    vault_audit_module.vault_audit_command()

    output = captured["output"]
    assert captured["output_format"] == "json"
    assert output.metadata["ok"] is True
    assert output.metadata["summary"]["healthy_projects"] == 1
    assert output.messages[0].level == "success"
    assert "look healthy" in output.messages[0].text
    assert output.sections[-1].title == "Summary"


def test_vault_audit_command_exits_non_zero_when_issues_are_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}
    projects = (
        VaultAuditProjectResult(
            project_slug="demo-app",
            project_id="prj_aaaaaaaaaaaaaaaa",
            key_path=Path("/tmp/vault/demo-app--prj_aaaaaaaaaaaaaaaa/master.key"),
            key_exists=False,
            files=(),
        ),
        VaultAuditProjectResult(
            project_slug="worker",
            project_id="prj_bbbbbbbbbbbbbbbb",
            key_path=Path("/tmp/vault/worker--prj_bbbbbbbbbbbbbbbb/master.key"),
            key_exists=True,
            files=(
                VaultAuditFileResult(
                    path=Path("/tmp/vault/worker--prj_bbbbbbbbbbbbbbbb/values.env"),
                    state="plaintext",
                    detail="File is plaintext.",
                    private_permissions=False,
                ),
            ),
        ),
    )

    monkeypatch.setattr(
        "envctl.services.vault_service.run_vault_audit",
        lambda: (None, projects),
    )
    monkeypatch.setattr(vault_audit_module, "is_json_output", lambda: False)
    monkeypatch.setattr(
        vault_audit_module,
        "present",
        lambda output, *, output_format: captured.update(
            {"output": output, "output_format": output_format}
        ),
    )

    with pytest.raises(typer.Exit) as exc_info:
        vault_audit_module.vault_audit_command()

    output = captured["output"]
    assert exc_info.value.exit_code == 1
    assert captured["output_format"] == "text"
    assert output.metadata["ok"] is False
    assert output.metadata["summary"]["projects_with_issues"] == 2
    assert output.metadata["summary"]["missing_keys"] == 1
    assert output.metadata["summary"]["missing_files"] == 1
    assert output.metadata["summary"]["plaintext_files"] == 1
    assert output.metadata["summary"]["insecure_files"] == 1
    assert output.messages[0].level == "warning"
    assert "Vault audit found issues" in output.messages[0].text
    assert output.messages[1].level == "warning"
    assert "do not have persisted vault files" in output.messages[1].text
