from __future__ import annotations

import pytest

import envctl.services.bind_service as bind_service
from envctl.errors import ExecutionError
from tests.support.app_config import make_app_config
from tests.support.contexts import make_project_context


def test_run_bind_rejects_invalid_project_id() -> None:
    with pytest.raises(ExecutionError, match="Invalid canonical project id"):
        bind_service.run_bind("bad-project")


def test_run_bind_rejects_missing_vault_for_project_id(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = make_app_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(bind_service, "load_config", lambda: config)
    monkeypatch.setattr(bind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        bind_service,
        "find_vault_dir_by_project_id",
        lambda projects_dir, project_id: None,
    )

    with pytest.raises(ExecutionError, match="No vault exists for project id"):
        bind_service.run_bind("prj_aaaaaaaaaaaaaaaa")


def test_run_bind_reports_unchanged_when_binding_is_already_current(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = make_app_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)
    vault_dir = config.projects_dir / "demo--prj_aaaaaaaaaaaaaaaa"
    vault_dir.mkdir(parents=True, exist_ok=True)
    context = make_project_context(
        repo_root=repo_root,
        project_id="prj_aaaaaaaaaaaaaaaa",
        vault_project_dir=vault_dir,
    )

    monkeypatch.setattr(bind_service, "load_config", lambda: config)
    monkeypatch.setattr(bind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        bind_service,
        "find_vault_dir_by_project_id",
        lambda projects_dir, project_id: vault_dir,
    )
    monkeypatch.setattr(
        bind_service,
        "get_local_git_config",
        lambda repo_root, key: "prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(
        bind_service,
        "build_context_for_project_id",
        lambda _config, repo_root, project_id, binding_source="local": context,
    )
    monkeypatch.setattr(
        bind_service,
        "persist_project_binding",
        lambda _config, context_arg: context_arg,
    )

    _, result = bind_service.run_bind("prj_aaaaaaaaaaaaaaaa")

    assert result.project_id == "prj_aaaaaaaaaaaaaaaa"
    assert result.changed is False
