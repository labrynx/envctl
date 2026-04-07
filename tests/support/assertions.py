from __future__ import annotations

from envctl.domain.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnostics,
    ProjectBindingDiagnostics,
    ProjectionValidationDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)
from envctl.errors import ValidationError


def require_config_diagnostics(value: object) -> ConfigDiagnostics:
    assert isinstance(value, ConfigDiagnostics)
    return value


def require_contract_diagnostics(value: object) -> ContractDiagnostics:
    assert isinstance(value, ContractDiagnostics)
    return value


def require_state_diagnostics(value: object) -> StateDiagnostics:
    assert isinstance(value, StateDiagnostics)
    return value


def require_repository_discovery_diagnostics(
    value: object,
) -> RepositoryDiscoveryDiagnostics:
    assert isinstance(value, RepositoryDiscoveryDiagnostics)
    return value


def require_project_binding_diagnostics(value: object) -> ProjectBindingDiagnostics:
    assert isinstance(value, ProjectBindingDiagnostics)
    return value


def require_projection_validation_diagnostics(
    value: object,
) -> ProjectionValidationDiagnostics:
    if isinstance(value, ProjectionValidationDiagnostics):
        return value
    if isinstance(value, ValidationError) and isinstance(
        value.diagnostics,
        ProjectionValidationDiagnostics,
    ):
        return value.diagnostics
    raise AssertionError(f"Expected ProjectionValidationDiagnostics, got {type(value).__name__}")
