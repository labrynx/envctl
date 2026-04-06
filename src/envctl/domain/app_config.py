"""Application configuration models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from envctl.constants import DEFAULT_PROJECTS_DIRNAME
from envctl.domain.runtime import RuntimeMode


@dataclass(frozen=True)
class AppConfig:
    """Resolved application configuration."""

    config_path: Path
    vault_dir: Path
    env_filename: str
    contract_filename: str
    runtime_mode: RuntimeMode
    default_profile: str
    encryption_enabled: bool = False
    encryption_strict: bool = False

    @property
    def projects_dir(self) -> Path:
        """Return the managed projects directory inside the vault."""
        return self.vault_dir / DEFAULT_PROJECTS_DIRNAME
