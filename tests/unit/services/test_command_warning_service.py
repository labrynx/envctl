from __future__ import annotations

from envctl.domain.diagnostics import DiagnosticSummary, InspectResult
from envctl.domain.selection import ContractSelection
from envctl.services.command_warning_service import (
    build_deprecated_command_warning,
    build_doctor_legacy_checks,
)
from tests.support.contexts import make_project_context


def test_build_deprecated_command_warning_uses_stable_message() -> None:
    warning = build_deprecated_command_warning(
        command_name="envctl doctor",
        replacement="envctl inspect",
        removal_version="v2.6.0",
    )

    assert warning.kind == "deprecated_command"
    assert "envctl doctor" in warning.message
    assert "envctl inspect" in warning.message
    assert "v2.6.0" in warning.message


def test_build_doctor_legacy_checks_builds_expected_items() -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = InspectResult(
        project=context,
        active_profile="staging",
        selection=ContractSelection(),
        contract_path=str(context.repo_contract_path),
        values_path=str(context.vault_values_path),
        summary=DiagnosticSummary(total=0, valid=0, invalid=0, unknown=0),
        variables=(),
        problems=(),
    )

    checks = build_doctor_legacy_checks(result)

    assert [check.name for check in checks] == ["project", "active_profile"]
    assert checks[0].status == "ok"
    assert "Resolved project" in checks[0].detail
    assert checks[1].detail == "Active profile: staging"
