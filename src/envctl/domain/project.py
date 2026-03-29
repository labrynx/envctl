"""Project domain models."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ConfirmFn = Callable[[str, bool], bool]
PromptFn = Callable[[str, bool, str | None], str]

InitContractMode = Literal["empty", "example", "skip"]
InitContractStatus = Literal["existing", "created_empty", "created_from_example", "skipped"]


@dataclass(frozen=True)
class ProjectContext:
    """Resolved project context for the current repository."""

    project_slug: str
    project_id: str
    repo_root: Path
    repo_env_path: Path
    repo_contract_path: Path
    vault_project_dir: Path
    vault_values_path: Path
    vault_state_path: Path

    @property
    def display_name(self) -> str:
        """Return a display name for terminal output."""
        return f"{self.project_slug} ({self.project_id})"


@dataclass(frozen=True)
class InitResult:
    """Result of project initialization."""

    context: ProjectContext
    contract_status: InitContractStatus
