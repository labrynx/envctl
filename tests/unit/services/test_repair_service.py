from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.repair_service as repair_service
from envctl.domain.app_config import AppConfig
from envctl.domain.project import BindingSource, ProjectContext
from envctl.errors import ExecutionError, ProjectDetectionError
from tests.support.app_config import make_app_config


def make_config(tmp_path: Path) -> AppConfig:
    return make_app_config(tmp_path)


def make_context(
    tmp_path: Path,
    *,
    project_id: str,
    binding_source: BindingSource,
    project_slug: str = "demo-app",
    project_key: str = "demo-app",
    repo_remote: str | None = "git@github.com:alessbarb/demo-app.git",
) -> ProjectContext:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_project_dir = tmp_path / "vault" / "projects" / f"{project_slug}--{project_id}"

    return ProjectContext(
        project_slug=project_slug,
        project_key=project_key,
        project_id=project_id,
        repo_root=repo_root,
        repo_remote=repo_remote,
        binding_source=binding_source,
        repo_env_path=repo_root / ".env.local",
        repo_contract_path=repo_root / ".envctl.schema.yaml",
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_project_dir / "values.env",
        vault_state_path=vault_project_dir / "state.json",
    )


def test_run_repair_raises_when_local_binding_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(repair_service, "get_local_git_config", lambda root, key: "invalid-binding")

    with pytest.raises(ExecutionError, match="Invalid project binding"):
        repair_service.run_repair()


def test_run_repair_returns_healthy_when_bound_vault_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    context = make_context(
        tmp_path,
        project_id="prj_aaaaaaaaaaaaaaaa",
        binding_source="local",
    )

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        repair_service,
        "get_local_git_config",
        lambda root, key: "prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(
        repair_service,
        "find_vault_dir_by_project_id",
        lambda projects_dir, project_id: context.vault_project_dir,
    )
    monkeypatch.setattr(
        repair_service,
        "build_context_for_project_id",
        lambda config_arg, repo_root, project_id, binding_source="local": context,
    )

    persisted_calls: list[ProjectContext] = []

    def fake_persist_project_binding(
        config_arg: AppConfig, context_arg: ProjectContext
    ) -> ProjectContext:
        persisted_calls.append(context_arg)
        return context_arg

    monkeypatch.setattr(repair_service, "persist_project_binding", fake_persist_project_binding)

    repaired_context, result = repair_service.run_repair()

    assert repaired_context == context
    assert result.status == "healthy"
    assert result.project_id == "prj_aaaaaaaaaaaaaaaa"
    assert persisted_calls == [context]


def test_run_repair_returns_needs_action_when_bound_vault_is_missing_and_not_recreated(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        repair_service,
        "get_local_git_config",
        lambda root, key: "prj_bbbbbbbbbbbbbbbb",
    )
    monkeypatch.setattr(
        repair_service,
        "find_vault_dir_by_project_id",
        lambda projects_dir, project_id: None,
    )

    repaired_context, result = repair_service.run_repair()

    assert repaired_context is None
    assert result.status == "needs_action"
    assert result.project_id == "prj_bbbbbbbbbbbbbbbb"
    assert "recreate-bound-vault" in result.detail


def test_run_repair_recreates_bound_vault_when_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    context = make_context(
        tmp_path,
        project_id="prj_cccccccccccccccc",
        binding_source="local",
    )

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        repair_service,
        "get_local_git_config",
        lambda root, key: "prj_cccccccccccccccc",
    )
    monkeypatch.setattr(
        repair_service,
        "find_vault_dir_by_project_id",
        lambda projects_dir, project_id: None,
    )
    monkeypatch.setattr(
        repair_service,
        "build_context_for_project_id",
        lambda config_arg, repo_root, project_id, binding_source="local": context,
    )
    monkeypatch.setattr(
        repair_service, "persist_project_binding", lambda config_arg, context_arg: context
    )

    ensured_dirs: list[Path] = []
    ensured_files: list[tuple[Path, str]] = []

    monkeypatch.setattr(repair_service, "ensure_dir", lambda path: ensured_dirs.append(path))
    monkeypatch.setattr(
        repair_service, "ensure_file", lambda path, content: ensured_files.append((path, content))
    )

    repaired_context, result = repair_service.run_repair(recreate_bound_vault=True)

    assert repaired_context == context
    assert result.status == "recreated"
    assert result.project_id == "prj_cccccccccccccccc"
    assert ensured_dirs == [context.vault_project_dir]
    assert ensured_files == [(context.vault_values_path, "")]


def test_run_repair_returns_needs_action_when_recovery_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(repair_service, "get_local_git_config", lambda root, key: None)

    def broken_build_project_context(config_arg: AppConfig) -> ProjectContext:
        raise ProjectDetectionError("Ambiguous vault identity for this repository.")

    monkeypatch.setattr(repair_service, "build_project_context", broken_build_project_context)

    repaired_context, result = repair_service.run_repair()

    assert repaired_context is None
    assert result.status == "needs_action"
    assert result.project_id is None
    assert "Ambiguous vault identity" in result.detail


def test_run_repair_returns_healthy_when_context_is_already_local(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    context = make_context(
        tmp_path,
        project_id="prj_dddddddddddddddd",
        binding_source="local",
    )

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(repair_service, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(repair_service, "build_project_context", lambda config_arg: context)

    repaired_context, result = repair_service.run_repair()

    assert repaired_context == context
    assert result.status == "healthy"
    assert result.project_id == "prj_dddddddddddddddd"


def test_run_repair_persists_recovered_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    recovered = make_context(
        tmp_path,
        project_id="prj_eeeeeeeeeeeeeeee",
        binding_source="recovered",
    )
    repaired = make_context(
        tmp_path,
        project_id="prj_eeeeeeeeeeeeeeee",
        binding_source="local",
    )

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(repair_service, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(repair_service, "build_project_context", lambda config_arg: recovered)
    monkeypatch.setattr(
        repair_service,
        "persist_project_binding",
        lambda config_arg, context_arg: repaired,
    )

    repaired_context, result = repair_service.run_repair()

    assert repaired_context == repaired
    assert result.status == "repaired"
    assert result.project_id == "prj_eeeeeeeeeeeeeeee"


def test_run_repair_returns_needs_action_for_derived_context_when_not_creating(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    context = make_context(
        tmp_path,
        project_id="tmp_deadbeefcafe",
        binding_source="derived",
        repo_remote=None,
    )

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(repair_service, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(repair_service, "build_project_context", lambda config_arg: context)

    repaired_context, result = repair_service.run_repair()

    assert repaired_context == context
    assert result.status == "needs_action"
    assert result.project_id == "tmp_deadbeefcafe"
    assert "create-if-missing" in result.detail


def test_run_repair_creates_and_persists_new_binding_when_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    derived = make_context(
        tmp_path,
        project_id="tmp_deadbeefcafe",
        binding_source="derived",
        repo_remote=None,
    )
    created = make_context(
        tmp_path,
        project_id="prj_ffffffffffffffff",
        binding_source="local",
        repo_remote=None,
    )

    monkeypatch.setattr(repair_service, "load_config", lambda: config)
    monkeypatch.setattr(repair_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(repair_service, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(repair_service, "build_project_context", lambda config_arg: derived)
    monkeypatch.setattr(repair_service, "new_project_id", lambda: "prj_ffffffffffffffff")
    monkeypatch.setattr(
        repair_service,
        "persist_project_binding",
        lambda config_arg, context_arg: created,
    )

    ensured_dirs: list[Path] = []
    ensured_files: list[tuple[Path, str]] = []

    monkeypatch.setattr(repair_service, "ensure_dir", lambda path: ensured_dirs.append(path))
    monkeypatch.setattr(
        repair_service, "ensure_file", lambda path, content: ensured_files.append((path, content))
    )

    repaired_context, result = repair_service.run_repair(create_if_missing=True)

    assert repaired_context == created
    assert result.status == "created"
    assert result.project_id == "prj_ffffffffffffffff"
    assert ensured_dirs == [created.vault_project_dir]
    assert ensured_files == [(created.vault_values_path, "")]
