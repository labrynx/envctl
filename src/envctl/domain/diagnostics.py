"""Diagnostic models for check and inspect commands."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolvedValue
from envctl.domain.selection import ContractSelection

ProblemKind = Literal[
    "missing_required",
    "invalid_value",
    "expansion_reference_error",
    "unknown_key",
    "invalid_contract",
]


@dataclass(frozen=True)
class CommandWarning:
    """Non-fatal warning attached to one command result."""

    kind: str
    message: str


@dataclass(frozen=True)
class DiagnosticProblem:
    """One actionable problem for human and JSON output."""

    key: str
    kind: ProblemKind
    message: str
    actions: tuple[str, ...]


@dataclass(frozen=True)
class DiagnosticSummary:
    """Compact summary for one diagnostic command."""

    total: int
    valid: int
    invalid: int
    unknown: int


@dataclass(frozen=True)
class CheckResult:
    """Structured result for ``envctl check``."""

    active_profile: str
    selection: ContractSelection
    summary: DiagnosticSummary
    problems: tuple[DiagnosticProblem, ...]
    values: tuple[ResolvedValue, ...] = ()
    warnings: tuple[CommandWarning, ...] = ()

    @property
    def ok(self) -> bool:
        return self.summary.invalid == 0 and self.summary.unknown == 0


@dataclass(frozen=True)
class InspectResult:
    """Structured result for ``envctl inspect``."""

    project: ProjectContext
    active_profile: str
    selection: ContractSelection
    contract_path: str
    values_path: str
    summary: DiagnosticSummary
    variables: tuple[ResolvedValue, ...]
    problems: tuple[DiagnosticProblem, ...]
    warnings: tuple[CommandWarning, ...] = ()


@dataclass(frozen=True)
class InspectKeyResult:
    """Structured result for ``envctl inspect KEY``."""

    project: ProjectContext
    active_profile: str
    item: ResolvedValue
    contract_type: str
    contract_format: str | None
    groups: tuple[str, ...]
    default: str | int | bool | None
    sensitive: bool
    warnings: tuple[CommandWarning, ...] = ()
