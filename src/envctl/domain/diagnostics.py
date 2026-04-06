"""Diagnostic models for check and inspect commands."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
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
class InspectContractGraph:
    """Composed contract graph summary for inspect output."""

    root_path: Path = Path(".")
    contract_paths: tuple[Path, ...] = ()
    contracts_total: int = 0
    variables_total: int = 0
    sets_total: int = 0
    groups_total: int = 0
    import_graph: dict[Path, tuple[Path, ...]] = field(default_factory=dict)
    declared_in: dict[str, Path] = field(default_factory=dict)
    sets_index: dict[str, tuple[str, ...]] = field(default_factory=dict)
    groups_index: dict[str, tuple[str, ...]] = field(default_factory=dict)


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
    contract_graph: InspectContractGraph = field(default_factory=InspectContractGraph)
    warnings: tuple[CommandWarning, ...] = ()


@dataclass(frozen=True)
class InspectKeyResult:
    """Structured result for ``envctl inspect KEY``."""

    project: ProjectContext
    active_profile: str
    item: ResolvedValue
    contract_type: str
    contract_format: str | None
    declared_in: Path = Path(".")
    sets: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    default: str | int | bool | None = None
    sensitive: bool = False
    warnings: tuple[CommandWarning, ...] = ()
