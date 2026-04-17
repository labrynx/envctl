from __future__ import annotations

from pathlib import Path

from envctl.domain.deprecations import ContractDeprecationWarning, DeprecatedField
from envctl.domain.diagnostics import CommandWarning, DiagnosticProblem, ProblemKind


def make_command_warning(
    *,
    kind: str = "demo_warning",
    message: str = "Demo command warning",
) -> CommandWarning:
    return CommandWarning(
        kind=kind,
        message=message,
    )


def make_contract_deprecation_warning(
    *,
    key: str = "API_KEY",
    deprecated_field: DeprecatedField = "required",
    message: str = "Deprecated contract field",
) -> ContractDeprecationWarning:
    return ContractDeprecationWarning(
        key=key,
        deprecated_field=deprecated_field,
        message=message,
    )


def make_diagnostic_problem(
    *,
    key: str = "API_KEY",
    kind: ProblemKind = "invalid_value",
    message: str = "Invalid value",
    actions: tuple[str, ...] = ("Fix the value",),
) -> DiagnosticProblem:
    return DiagnosticProblem(
        key=key,
        kind=kind,
        message=message,
        actions=actions,
    )


def make_path(value: str = "/tmp/demo") -> Path:
    return Path(value)
