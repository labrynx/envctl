from __future__ import annotations

import json
from pathlib import Path

import pytest

import envctl.repository.project_context as project_context_module
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.errors import ProjectDetectionError
from tests.support.app_config import make_app_config


def make_config(tmp_path: Path) -> AppConfig:
    return make_app_config(tmp_path)


def write_state(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_find_vault_dir_by_project_id_returns_match(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    expected = projects_dir / "demo-app--prj_aaaaaaaaaaaaaaaa"
    expected.mkdir()

    result = project_context_module.find_vault_dir_by_project_id(
        projects_dir,
        "prj_aaaaaaaaaaaaaaaa",
    )

    assert result == expected


def test_find_vault_dir_by_project_id_returns_none_when_missing(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    result = project_context_module.find_vault_dir_by_project_id(
        projects_dir,
        "prj_missing00000000",
    )

    assert result is None


def test_find_vault_dir_by_project_id_raises_when_multiple_matches_exist(tmp_path: Path) -> None:
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    (projects_dir / "demo-a--prj_aaaaaaaaaaaaaaaa").mkdir()
    (projects_dir / "demo-b--prj_aaaaaaaaaaaaaaaa").mkdir()

    with pytest.raises(ProjectDetectionError, match="Multiple vault directories found"):
        project_context_module.find_vault_dir_by_project_id(
            projects_dir,
            "prj_aaaaaaaaaaaaaaaa",
        )


def test_build_project_context_returns_bound_local_context_when_git_binding_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = config.projects_dir / "demo-app--prj_aaaaaaaaaaaaaaaa"
    write_state(
        vault_dir / "state.json",
        {
            "version": 2,
            "project_slug": "demo-app",
            "project_key": "demo-app",
            "project_id": "prj_aaaaaaaaaaaaaaaa",
            "repo_root": str(repo_root),
            "git_remote": "git@github.com:alessbarb/demo-app.git",
            "known_paths": [str(repo_root)],
            "created_at": "2026-03-30T00:00:00Z",
            "last_seen_at": "2026-03-30T00:00:00Z",
        },
    )

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "repo-name"
    )
    monkeypatch.setattr(
        project_context_module,
        "get_local_git_config",
        lambda root, key: "prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(
        project_context_module,
        "get_repo_remote",
        lambda root: "git@github.com:alessbarb/demo-app.git",
    )
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: None)

    context = project_context_module.build_project_context(config)

    assert context.project_id == "prj_aaaaaaaaaaaaaaaa"
    assert context.project_slug == "demo-app"
    assert context.project_key == "demo-app"
    assert context.binding_source == "local"
    assert context.repo_root == repo_root
    assert context.repo_contract_path == repo_root / ".envctl.schema.yaml"
    assert context.repo_env_path == repo_root / ".env.local"
    assert context.vault_project_dir == vault_dir
    assert context.vault_state_path == vault_dir / "state.json"
    assert context.vault_values_path == vault_dir / "values.env"


def test_build_project_context_recovers_from_remote_match_when_no_binding_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = config.projects_dir / "demo-app--prj_bbbbbbbbbbbbbbbb"
    write_state(
        vault_dir / "state.json",
        {
            "version": 2,
            "project_slug": "demo-app",
            "project_key": "demo-app",
            "project_id": "prj_bbbbbbbbbbbbbbbb",
            "repo_root": str(repo_root),
            "git_remote": "git@github.com:alessbarb/demo-app.git",
            "known_paths": [str(repo_root)],
            "created_at": "2026-03-30T00:00:00Z",
            "last_seen_at": "2026-03-30T00:00:00Z",
        },
    )

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "repo-name"
    )
    monkeypatch.setattr(project_context_module, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(
        project_context_module,
        "get_repo_remote",
        lambda root: "git@github.com:alessbarb/demo-app.git",
    )
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: None)

    context = project_context_module.build_project_context(config)

    assert context.project_id == "prj_bbbbbbbbbbbbbbbb"
    assert context.project_slug == "demo-app"
    assert context.project_key == "demo-app"
    assert context.binding_source == "recovered"
    assert context.vault_project_dir == vault_dir


def test_build_project_context_recovers_from_project_key_when_repo_has_no_remote(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = config.projects_dir / "demo-app--prj_cccccccccccccccc"
    write_state(
        vault_dir / "state.json",
        {
            "version": 2,
            "project_slug": "demo-app",
            "project_key": "shared-service",
            "project_id": "prj_cccccccccccccccc",
            "repo_root": "/some/other/path",
            "git_remote": None,
            "known_paths": ["/some/other/path"],
            "created_at": "2026-03-30T00:00:00Z",
            "last_seen_at": "2026-03-30T00:00:00Z",
        },
    )

    class Meta:
        project_key = "shared-service"

    class Contract:
        meta = Meta()

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "repo-name"
    )
    monkeypatch.setattr(project_context_module, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(project_context_module, "get_repo_remote", lambda root: None)
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: Contract())

    context = project_context_module.build_project_context(config)

    assert context.project_id == "prj_cccccccccccccccc"
    assert context.project_slug == "demo-app"
    assert context.project_key == "shared-service"
    assert context.binding_source == "recovered"
    assert context.vault_project_dir == vault_dir


def test_build_project_context_recovers_from_known_paths_when_repo_has_no_remote(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = config.projects_dir / "demo-app--prj_dddddddddddddddd"
    write_state(
        vault_dir / "state.json",
        {
            "version": 2,
            "project_slug": "demo-app",
            "project_key": "other-key",
            "project_id": "prj_dddddddddddddddd",
            "repo_root": "/another/path",
            "git_remote": None,
            "known_paths": [str(repo_root.resolve())],
            "created_at": "2026-03-30T00:00:00Z",
            "last_seen_at": "2026-03-30T00:00:00Z",
        },
    )

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "repo-name"
    )
    monkeypatch.setattr(project_context_module, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(project_context_module, "get_repo_remote", lambda root: None)
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: None)

    context = project_context_module.build_project_context(config)

    assert context.project_id == "prj_dddddddddddddddd"
    assert context.binding_source == "recovered"
    assert context.vault_project_dir == vault_dir


def test_build_project_context_raises_when_recovery_is_ambiguous(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    write_state(
        config.projects_dir / "demo-a--prj_1111111111111111" / "state.json",
        {
            "version": 2,
            "project_slug": "demo-a",
            "project_key": "shared-key",
            "project_id": "prj_1111111111111111",
            "repo_root": "/old/path/a",
            "git_remote": None,
            "known_paths": [],
            "created_at": "2026-03-30T00:00:00Z",
            "last_seen_at": "2026-03-30T00:00:00Z",
        },
    )
    write_state(
        config.projects_dir / "demo-b--prj_2222222222222222" / "state.json",
        {
            "version": 2,
            "project_slug": "demo-b",
            "project_key": "shared-key",
            "project_id": "prj_2222222222222222",
            "repo_root": "/old/path/b",
            "git_remote": None,
            "known_paths": [],
            "created_at": "2026-03-30T00:00:00Z",
            "last_seen_at": "2026-03-30T00:00:00Z",
        },
    )

    class Meta:
        project_key = "shared-key"

    class Contract:
        meta = Meta()

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "repo-name"
    )
    monkeypatch.setattr(project_context_module, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(project_context_module, "get_repo_remote", lambda root: None)
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: Contract())

    with pytest.raises(ProjectDetectionError, match="Ambiguous vault identity"):
        project_context_module.build_project_context(config)


def test_build_project_context_returns_derived_context_when_nothing_can_be_recovered(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "demo-app"
    )
    monkeypatch.setattr(project_context_module, "get_local_git_config", lambda root, key: None)
    monkeypatch.setattr(project_context_module, "get_repo_remote", lambda root: None)
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: None)

    context = project_context_module.build_project_context(config)

    assert context.binding_source == "derived"
    assert context.project_slug == "demo-app"
    assert context.project_key == "demo-app"
    assert context.project_id.startswith("tmp_")


def test_build_project_context_raises_for_invalid_local_binding(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "demo-app"
    )
    monkeypatch.setattr(
        project_context_module, "get_local_git_config", lambda root, key: "not-valid"
    )
    monkeypatch.setattr(project_context_module, "get_repo_remote", lambda root: None)
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: None)

    with pytest.raises(ProjectDetectionError, match="Invalid project binding"):
        project_context_module.build_project_context(config)


def test_build_project_context_raises_when_bound_project_has_no_matching_vault(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(project_context_module, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "demo-app"
    )
    monkeypatch.setattr(
        project_context_module,
        "get_local_git_config",
        lambda root, key: "prj_eeeeeeeeeeeeeeee",
    )
    monkeypatch.setattr(project_context_module, "get_repo_remote", lambda root: None)
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: None)

    with pytest.raises(ProjectDetectionError, match="no matching vault exists"):
        project_context_module.build_project_context(config)


def test_build_context_for_project_id_prefers_state_slug_and_key_when_vault_exists(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = config.projects_dir / "fallback-name--prj_ffffffffffffffff"
    write_state(
        vault_dir / "state.json",
        {
            "version": 2,
            "project_slug": "state-slug",
            "project_key": "state-key",
            "project_id": "prj_ffffffffffffffff",
            "repo_root": str(repo_root),
            "git_remote": None,
            "known_paths": [str(repo_root)],
            "created_at": "2026-03-30T00:00:00Z",
            "last_seen_at": "2026-03-30T00:00:00Z",
        },
    )

    monkeypatch.setattr(project_context_module, "get_repo_remote", lambda root: None)
    monkeypatch.setattr(
        project_context_module, "resolve_project_name", lambda root, name: "fallback-name"
    )
    monkeypatch.setattr(project_context_module, "load_contract_optional", lambda path: None)

    context = project_context_module.build_context_for_project_id(
        config,
        repo_root=repo_root,
        project_id="prj_ffffffffffffffff",
    )

    assert context.project_slug == "state-slug"
    assert context.project_key == "state-key"
    assert context.project_id == "prj_ffffffffffffffff"
    assert context.vault_project_dir == vault_dir


def test_persist_project_binding_writes_state_and_returns_local_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    captured_git_config: list[tuple[Path, str, str]] = []

    def fake_set_local_git_config(repo_root_arg: Path, key: str, value: str) -> None:
        captured_git_config.append((repo_root_arg, key, value))

    monkeypatch.setattr(project_context_module, "set_local_git_config", fake_set_local_git_config)

    context = ProjectContext(
        project_slug="demo-app",
        project_key="demo-app",
        project_id="prj_abcdabcdabcdabcd",
        repo_root=repo_root,
        repo_remote="git@github.com:alessbarb/demo-app.git",
        binding_source="derived",
        repo_env_path=repo_root / ".env.local",
        repo_contract_path=repo_root / ".envctl.schema.yaml",
        vault_project_dir=config.projects_dir / "placeholder",
        vault_values_path=config.projects_dir / "placeholder" / "values.env",
        vault_state_path=config.projects_dir / "placeholder" / "state.json",
    )

    persisted = project_context_module.persist_project_binding(config, context)

    assert persisted.binding_source == "local"
    assert persisted.project_id == "prj_abcdabcdabcdabcd"
    assert persisted.vault_project_dir == config.projects_dir / "demo-app--prj_abcdabcdabcdabcd"
    assert persisted.vault_values_path == persisted.vault_project_dir / "values.env"
    assert persisted.vault_state_path == persisted.vault_project_dir / "state.json"

    assert captured_git_config == [
        (
            repo_root,
            "envctl.projectId",
            "prj_abcdabcdabcdabcd",
        )
    ]

    state = json.loads(persisted.vault_state_path.read_text(encoding="utf-8"))
    assert state["version"] == 2
    assert state["project_slug"] == "demo-app"
    assert state["project_key"] == "demo-app"
    assert state["project_id"] == "prj_abcdabcdabcdabcd"
    assert state["repo_root"] == str(repo_root)
    assert state["git_remote"] == "git@github.com:alessbarb/demo-app.git"
    assert state["known_paths"] == [str(repo_root)]
