from __future__ import annotations

from pathlib import Path

from envctl.domain.project import ProjectContext


def make_project_context(
    *,
    project_slug: str = "demo",
    project_key: str | None = None,
    project_id: str = "prj_aaaaaaaaaaaaaaaa",
    repo_root: Path | str = "/tmp/demo",
    repo_remote: str | None = None,
    binding_source: str = "local",
    repo_contract_path: Path | str | None = None,
    vault_project_dir: Path | str | None = None,
    vault_values_path: Path | str | None = None,
    vault_state_path: Path | str | None = None,
    repo_env_path: Path | str | None = None,
) -> ProjectContext:
    """Build a complete ProjectContext for tests."""
    repo_root = Path(repo_root)

    resolved_project_key = project_key or project_slug
    resolved_repo_contract_path = Path(repo_contract_path or (repo_root / ".envctl.schema.yaml"))
    resolved_repo_env_path = Path(repo_env_path or (repo_root / ".env.local"))

    resolved_vault_project_dir = Path(
        vault_project_dir or (repo_root.parent / "vault" / "projects" / f"{project_slug}--{project_id}")
    )
    resolved_vault_values_path = Path(vault_values_path or (resolved_vault_project_dir / "values.env"))
    resolved_vault_state_path = Path(vault_state_path or (resolved_vault_project_dir / "state.json"))

    return ProjectContext(
        project_slug=project_slug,
        project_key=resolved_project_key,
        project_id=project_id,
        repo_root=repo_root,
        repo_remote=repo_remote,
        binding_source=binding_source,
        repo_env_path=resolved_repo_env_path,
        repo_contract_path=resolved_repo_contract_path,
        vault_project_dir=resolved_vault_project_dir,
        vault_values_path=resolved_vault_values_path,
        vault_state_path=resolved_vault_state_path,
    )


def make_status_context(
    tmp_path: Path,
    *,
    contract_exists: bool,
    vault_exists: bool,
    project_slug: str = "demo",
    project_key: str | None = None,
    project_id: str = "prj_aaaaaaaaaaaaaaaa",
    repo_remote: str | None = None,
    binding_source: str = "local",
) -> ProjectContext:
    """Build a filesystem-backed ProjectContext for status-service tests."""
    repo_root = tmp_path
    repo_contract_path = repo_root / ".envctl.schema.yaml"
    vault_project_dir = tmp_path / "vault" / "projects" / f"{project_slug}--{project_id}"
    vault_values_path = vault_project_dir / "values.env"

    if contract_exists:
        repo_contract_path.write_text(
            "version: 1\nvariables:\n  APP_NAME: {}\n",
            encoding="utf-8",
        )

    if vault_exists:
        vault_project_dir.mkdir(parents=True, exist_ok=True)
        vault_values_path.write_text('APP_NAME="demo"\n', encoding="utf-8")

    return make_project_context(
        project_slug=project_slug,
        project_key=project_key,
        project_id=project_id,
        repo_root=repo_root,
        repo_remote=repo_remote,
        binding_source=binding_source,
        repo_contract_path=repo_contract_path,
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_values_path,
        vault_state_path=vault_project_dir / "state.json",
        repo_env_path=repo_root / ".env.local",
    )