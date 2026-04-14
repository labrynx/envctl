from __future__ import annotations

from pathlib import Path

from envctl.cli.serializers.diagnostics import (
    serialize_contract_diagnostics,
    serialize_error_diagnostics,
    serialize_project_binding_diagnostics,
)
from envctl.cli.serializers.errors import (
    serialize_error,
)
from envctl.cli.serializers.hooks import (
    serialize_hook_operation_report,
    serialize_hooks_status_report,
)
from envctl.domain.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnosticIssue,
    ContractDiagnostics,
    ProjectBindingDiagnostics,
)
from envctl.domain.hooks import (
    HookAction,
    HookInspectionResult,
    HookName,
    HookOperationReport,
    HookOperationResult,
    HooksStatusLevel,
    HooksStatusReport,
    HookStatus,
)
from tests.support.paths import normalize_path_str


def test_serialize_contract_diagnostics_returns_expected_shape() -> None:
    diagnostics = ContractDiagnostics(
        category="invalid_variable_shape",
        path=Path("/tmp/demo/.envctl.yaml"),
        key="PORT",
        field="variables",
        issues=(
            ContractDiagnosticIssue(
                field="variables.PORT",
                detail="Variable must be a mapping",
            ),
        ),
        suggested_actions=("envctl check", "fix .envctl.yaml"),
    )

    payload = serialize_contract_diagnostics(diagnostics)
    assert payload["category"] == "invalid_variable_shape"
    assert normalize_path_str(payload["path"]) == "/tmp/demo/.envctl.yaml"
    assert payload["key"] == "PORT"
    assert payload["issues"] == [
        {
            "field": "variables.PORT",
            "detail": "Variable must be a mapping",
        }
    ]


def test_serialize_error_diagnostics_routes_to_specific_serializer() -> None:
    binding = ProjectBindingDiagnostics(category="ambiguous_vault_identity")
    config = ConfigDiagnostics(category="invalid_json")

    assert serialize_project_binding_diagnostics(binding)["category"] == "ambiguous_vault_identity"
    assert serialize_error_diagnostics(config)["category"] == "invalid_json"

    payload = serialize_error(
        error_type=type(config).__name__,
        message="boom",
        command="envctl check",
        details=serialize_error_diagnostics(config),
    )
    assert payload["error"]["details"]["category"] == "invalid_json"


def test_serialize_hooks_status_report_returns_expected_shape() -> None:
    report = HooksStatusReport(
        hooks_path=Path("/tmp/demo/.git/hooks"),
        overall_status=HooksStatusLevel.DEGRADED,
        results=(
            HookInspectionResult(
                name=HookName.PRE_COMMIT,
                path=Path("/tmp/demo/.git/hooks/pre-commit"),
                status=HookStatus.MISSING,
                managed=False,
                is_executable=None,
            ),
        ),
    )

    payload = serialize_hooks_status_report(report)

    assert payload["overall_status"] == "degraded"
    assert payload["results"][0]["hook_name"] == "pre-commit"
    assert payload["results"][0]["is_executable"] is None


def test_serialize_hook_operation_report_returns_expected_shape() -> None:
    report = HookOperationReport(
        hooks_path=Path("/tmp/demo/.git/hooks"),
        final_status=HooksStatusLevel.HEALTHY,
        changed=True,
        results=(
            HookOperationResult(
                name=HookName.PRE_COMMIT,
                path=Path("/tmp/demo/.git/hooks/pre-commit"),
                before_status=HookStatus.MISSING,
                after_status=HookStatus.HEALTHY,
                action=HookAction.CREATED,
                changed=True,
                managed=True,
            ),
        ),
    )

    payload = serialize_hook_operation_report(report)

    assert payload["overall_status"] == "healthy"
    assert payload["changed"] is True
    assert payload["results"][0]["action"] == "created"
