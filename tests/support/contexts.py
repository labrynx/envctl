from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace


def make_project_context(
    *,
    project_slug: str = "demo",
    project_id: str = "abc123",
    repo_root: Path | str = "/tmp/demo",
    repo_contract_path: Path | str = "/tmp/demo/.envctl.schema.yaml",
    vault_values_path: Path | str = "/tmp/demo/vault.env",
    repo_env_path: Path | str = "/tmp/demo/.env.local",
    display_name: str = "demo",
) -> SimpleNamespace:
    """Build a lightweight project context for tests."""
    return SimpleNamespace(
        project_slug=project_slug,
        project_id=project_id,
        repo_root=repo_root,
        repo_contract_path=repo_contract_path,
        vault_values_path=vault_values_path,
        repo_env_path=repo_env_path,
        display_name=display_name,
    )


def make_status_context(
    tmp_path: Path,
    *,
    contract_exists: bool,
    vault_exists: bool,
    project_slug: str = "demo",
    project_id: str = "abc123",
) -> SimpleNamespace:
    """Build a filesystem-backed context for status-service tests."""
    repo_contract_path = tmp_path / ".envctl.schema.yaml"
    vault_values_path = tmp_path / "vault.env"

    if contract_exists:
        repo_contract_path.write_text(
            "version: 1\nvariables:\n  APP_NAME: {}\n",
            encoding="utf-8",
        )

    if vault_exists:
        vault_values_path.write_text('APP_NAME="demo"\n', encoding="utf-8")

    return make_project_context(
        project_slug=project_slug,
        project_id=project_id,
        repo_root=tmp_path,
        repo_contract_path=repo_contract_path,
        vault_values_path=vault_values_path,
        repo_env_path=tmp_path / ".env.local",
        display_name=project_slug,
    )
