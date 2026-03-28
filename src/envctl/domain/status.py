"""Status domain models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StatusReport:
    """Human-oriented project status report."""

    project_slug: str
    project_id: str
    repo_root: Path
    contract_exists: bool
    vault_exists: bool
    resolved_valid: bool
    summary: str
    issues: list[str]
    suggested_action: str | None
