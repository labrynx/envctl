"""Status domain models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

StatusSummaryKind = Literal[
    "missing_contract",
    "invalid_contract",
    "satisfied",
    "unsatisfied",
]
StatusIssueKind = Literal[
    "contract_missing",
    "contract_error",
    "missing_required",
    "invalid_values",
    "unknown_keys",
]
StatusActionKind = Literal[
    "create_contract_or_add_key",
    "fix_contract_file",
    "fill_or_set_values",
    "fix_invalid_values",
    "add_or_remove_unknown_keys",
]


@dataclass(frozen=True)
class StatusIssue:
    """One structured status issue."""

    kind: StatusIssueKind
    keys: tuple[str, ...] = ()
    detail: str | None = None


@dataclass(frozen=True)
class StatusReport:
    """Structured project status report."""

    project_slug: str
    project_id: str
    repo_root: Path
    contract_exists: bool
    vault_exists: bool
    resolved_valid: bool
    summary_kind: StatusSummaryKind
    issues: tuple[StatusIssue, ...]
    suggested_action_kind: StatusActionKind | None
