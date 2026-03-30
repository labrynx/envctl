from __future__ import annotations

from pathlib import Path

from envctl.domain.app_config import AppConfig
from envctl.domain.runtime import RuntimeMode


def make_app_config(
    tmp_path: Path,
    *,
    env_filename: str = ".env.local",
    schema_filename: str = ".envctl.schema.yaml",
    runtime_mode: RuntimeMode = RuntimeMode.LOCAL,
    default_profile: str = "local",
) -> AppConfig:
    """Build a minimal AppConfig for tests."""
    config_path = tmp_path / "config" / "config.json"
    vault_dir = tmp_path / "vault"

    return AppConfig(
        config_path=config_path,
        vault_dir=vault_dir,
        env_filename=env_filename,
        schema_filename=schema_filename,
        runtime_mode=runtime_mode,
        default_profile=default_profile,
    )
