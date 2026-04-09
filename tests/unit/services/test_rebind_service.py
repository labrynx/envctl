from __future__ import annotations

import logging
from pathlib import Path

import pytest

import envctl.services.rebind_service as rebind_service
from envctl.domain.app_config import AppConfig
from tests.support.app_config import make_app_config
from tests.support.contexts import make_project_context


def make_config(tmp_path: Path) -> AppConfig:
    return make_app_config(tmp_path)


def test_load_previous_values_returns_empty_when_previous_project_id_is_none(
    tmp_path: Path,
) -> None:
    projects_dir = tmp_path / "vault" / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    result = rebind_service._load_previous_values(projects_dir, None)

    assert result == {}


def test_load_previous_values_returns_empty_when_previous_vault_does_not_exist(
    tmp_path: Path,
) -> None:
    projects_dir = tmp_path / "vault" / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)

    result = rebind_service._load_previous_values(projects_dir, "prj_aaaaaaaaaaaaaaaa")

    assert result == {}


def test_load_previous_values_returns_empty_when_values_file_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    projects_dir = tmp_path / "vault" / "projects"
    previous_vault_dir = projects_dir / "demo--prj_aaaaaaaaaaaaaaaa"
    previous_vault_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(
        rebind_service,
        "find_vault_dir_by_project_id",
        lambda _projects_dir, project_id: previous_vault_dir,
    )

    result = rebind_service._load_previous_values(projects_dir, "prj_aaaaaaaaaaaaaaaa")

    assert result == {}


def test_load_previous_values_reads_existing_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    projects_dir = tmp_path / "vault" / "projects"
    previous_vault_dir = projects_dir / "demo--prj_aaaaaaaaaaaaaaaa"
    previous_vault_dir.mkdir(parents=True, exist_ok=True)
    values_path = previous_vault_dir / "values.env"
    values_path.write_text('APP_NAME="demo"\nDEBUG="true"\n', encoding="utf-8")

    monkeypatch.setattr(
        rebind_service,
        "find_vault_dir_by_project_id",
        lambda _projects_dir, project_id: previous_vault_dir,
    )

    result = rebind_service._load_previous_values(projects_dir, "prj_aaaaaaaaaaaaaaaa")

    assert result == {
        "APP_NAME": "demo",
        "DEBUG": "true",
    }


def test_run_rebind_creates_new_binding_without_copying_when_no_previous_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    context = make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_bbbbbbbbbbbbbbbb",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        vault_project_dir=config.projects_dir / "demo--prj_bbbbbbbbbbbbbbbb",
    )

    monkeypatch.setattr(rebind_service, "load_config", lambda: config)
    monkeypatch.setattr(
        rebind_service,
        "load_configured_vault_crypto",
        lambda _config, _context: None,
    )
    monkeypatch.setattr(rebind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(rebind_service, "get_local_git_config", lambda _repo_root, key: None)
    monkeypatch.setattr(rebind_service, "new_project_id", lambda: "prj_bbbbbbbbbbbbbbbb")
    monkeypatch.setattr(
        rebind_service,
        "build_context_for_project_id",
        lambda _config, repo_root, project_id, binding_source="local": context,
    )
    monkeypatch.setattr(
        rebind_service,
        "persist_project_binding",
        lambda _config, context_arg: context_arg,
    )

    context_result, result = rebind_service.run_rebind(copy_values=True)

    assert context_result == context
    assert result.previous_project_id is None
    assert result.new_project_id == "prj_bbbbbbbbbbbbbbbb"
    assert result.copied_values is False
    assert context.vault_project_dir.exists()
    assert context.vault_values_path.exists()
    assert context.vault_values_path.read_text(encoding="utf-8") == ""


def test_run_rebind_copies_previous_values_when_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    context = make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_bbbbbbbbbbbbbbbb",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        vault_project_dir=config.projects_dir / "demo--prj_bbbbbbbbbbbbbbbb",
    )

    monkeypatch.setattr(rebind_service, "load_config", lambda: config)
    monkeypatch.setattr(
        rebind_service,
        "load_configured_vault_crypto",
        lambda _config, _context: None,
    )
    monkeypatch.setattr(rebind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        rebind_service,
        "get_local_git_config",
        lambda _repo_root, key: "prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(rebind_service, "new_project_id", lambda: "prj_bbbbbbbbbbbbbbbb")
    monkeypatch.setattr(
        rebind_service,
        "build_context_for_project_id",
        lambda _config, repo_root, project_id, binding_source="local": context,
    )
    monkeypatch.setattr(
        rebind_service,
        "persist_project_binding",
        lambda _config, context_arg: context_arg,
    )
    monkeypatch.setattr(
        rebind_service,
        "_load_previous_values",
        lambda projects_dir, previous_project_id, crypto=None: {
            "APP_NAME": "demo",
            "DEBUG": "true",
        },
    )

    context_result, result = rebind_service.run_rebind(copy_values=True)

    assert context_result == context
    assert result.previous_project_id == "prj_aaaaaaaaaaaaaaaa"
    assert result.new_project_id == "prj_bbbbbbbbbbbbbbbb"
    assert result.copied_values is True
    assert context.vault_values_path.exists()
    content = context.vault_values_path.read_text(encoding="utf-8")
    lines = set(content.strip().splitlines())
    assert "APP_NAME=demo" in lines
    assert "DEBUG=true" in lines


def test_run_rebind_does_not_copy_values_when_empty_is_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    context = make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_bbbbbbbbbbbbbbbb",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        vault_project_dir=config.projects_dir / "demo--prj_bbbbbbbbbbbbbbbb",
    )

    monkeypatch.setattr(rebind_service, "load_config", lambda: config)
    monkeypatch.setattr(
        rebind_service,
        "load_configured_vault_crypto",
        lambda _config, _context: None,
    )
    monkeypatch.setattr(rebind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        rebind_service,
        "get_local_git_config",
        lambda _repo_root, key: "prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(rebind_service, "new_project_id", lambda: "prj_bbbbbbbbbbbbbbbb")
    monkeypatch.setattr(
        rebind_service,
        "build_context_for_project_id",
        lambda _config, repo_root, project_id, binding_source="local": context,
    )
    monkeypatch.setattr(
        rebind_service,
        "persist_project_binding",
        lambda _config, context_arg: context_arg,
    )
    monkeypatch.setattr(
        rebind_service,
        "_load_previous_values",
        lambda projects_dir, previous_project_id, crypto=None: {
            "APP_NAME": "demo",
        },
    )

    context_result, result = rebind_service.run_rebind(copy_values=False)

    assert context_result == context
    assert result.previous_project_id == "prj_aaaaaaaaaaaaaaaa"
    assert result.new_project_id == "prj_bbbbbbbbbbbbbbbb"
    assert result.copied_values is False
    assert context.vault_values_path.exists()
    assert context.vault_values_path.read_text(encoding="utf-8") == ""


def test_run_rebind_logs_debug_and_info_summary(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    config = make_config(tmp_path)
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    context = make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_bbbbbbbbbbbbbbbb",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        vault_project_dir=config.projects_dir / "demo--prj_bbbbbbbbbbbbbbbb",
    )

    monkeypatch.setattr(rebind_service, "load_config", lambda: config)
    monkeypatch.setattr(
        rebind_service,
        "load_configured_vault_crypto",
        lambda _config, _context: None,
    )
    monkeypatch.setattr(rebind_service, "resolve_repo_root", lambda: repo_root)
    monkeypatch.setattr(
        rebind_service,
        "get_local_git_config",
        lambda _repo_root, key: "prj_aaaaaaaaaaaaaaaa",
    )
    monkeypatch.setattr(rebind_service, "new_project_id", lambda: "prj_bbbbbbbbbbbbbbbb")
    monkeypatch.setattr(
        rebind_service,
        "build_context_for_project_id",
        lambda _config, repo_root, project_id, binding_source="local": context,
    )
    monkeypatch.setattr(
        rebind_service,
        "persist_project_binding",
        lambda _config, context_arg: context_arg,
    )
    monkeypatch.setattr(
        rebind_service,
        "_load_previous_values",
        lambda projects_dir, previous_project_id, crypto=None: {"APP_NAME": "demo"},
    )

    logger = logging.getLogger("envctl")
    logger.addHandler(caplog.handler)
    logger.setLevel(logging.DEBUG)
    caplog.set_level("DEBUG")

    try:
        rebind_service.run_rebind(copy_values=True)
    finally:
        logger.removeHandler(caplog.handler)

    assert any(
        record.name == "envctl.services.rebind_service"
        and record.levelname == "DEBUG"
        and record.message == "Loaded previous rebind values"
        and getattr(record, "previous_value_count", None) == 1
        for record in caplog.records
    )
    assert any(
        record.name == "envctl.services.rebind_service"
        and record.levelname == "INFO"
        and record.message == "Repository rebound to new project id"
        and getattr(record, "copied_values", None) is True
        for record in caplog.records
    )
