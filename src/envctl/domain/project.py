"""Project domain models."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from envctl.domain.diagnostics import CommandWarning
    from envctl.vault_crypto import VaultCrypto

ConfirmFn = Callable[[str, bool], bool]
PromptFn = Callable[[str, bool, str | None], str]

BindingSource = Literal["local", "recovered", "derived"]


@dataclass(frozen=True)
class ProjectContext:
    """Resolved project context for the current repository."""

    project_slug: str
    project_key: str
    project_id: str
    repo_root: Path
    repo_remote: str | None
    binding_source: BindingSource
    repo_env_path: Path
    repo_contract_path: Path
    vault_project_dir: Path
    vault_values_path: Path
    vault_state_path: Path
    vault_key_path: Path
    vault_crypto: VaultCrypto | None = None
    runtime_warnings: tuple[CommandWarning, ...] = ()

    @property
    def display_name(self) -> str:
        """Return a display name for terminal output."""
        return f"{self.project_slug} ({self.project_id})"
