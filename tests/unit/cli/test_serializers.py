from __future__ import annotations

from pathlib import Path

from envctl.cli.serializers import (
    serialize_contract_diagnostics,
    serialize_error,
    serialize_error_diagnostics,
    serialize_project_binding_diagnostics,
)
from envctl.domain.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnosticIssue,
    ContractDiagnostics,
    ProjectBindingDiagnostics,
)


def normalize_path_str(value: str) -> str:
    """Normalize serialized path values for cross-platform assertions."""
    return value.replace("\\", "/")


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
