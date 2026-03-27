from __future__ import annotations

from envctl.services.init_service import run_init
from envctl.services.status_service import run_status


def test_status_after_init(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    report = run_status()

    assert report.state == "healthy"
    assert report.project_slug == context.project_slug
    assert report.project_id == context.project_id
    assert report.repo_env_status == "linked"
    assert report.vault_env_status == "present"
    assert report.issues == []
    assert report.suggested_action is None


def test_status_when_not_initialized(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)

    report = run_status()

    assert report.state == "not initialized"
    assert report.project_slug is None
    assert report.project_id is None
    assert report.repo_env_status == "unmanaged"
    assert report.vault_env_status == "unknown"
    assert report.issues == []
    assert report.suggested_action == "envctl init"


def test_status_when_repo_symlink_is_missing(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.repo_env_path.unlink()

    report = run_status()

    assert report.state == "broken"
    assert report.project_slug == context.project_slug
    assert report.project_id == context.project_id
    assert report.repo_env_status == "missing"
    assert report.vault_env_status == "present"
    assert ".env.local is missing" in report.issues
    assert report.suggested_action == "envctl repair"


def test_status_when_repo_env_is_regular_file(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.repo_env_path.unlink()
    context.repo_env_path.write_text("LOCAL_ONLY=1\n", encoding="utf-8")

    report = run_status()

    assert report.state == "broken"
    assert report.repo_env_status == "regular file"
    assert report.vault_env_status == "present"
    assert ".env.local is a regular file, not a managed symlink" in report.issues
    assert report.suggested_action == "envctl repair"


def test_status_when_repo_symlink_points_elsewhere(isolated_env, repo_dir, monkeypatch, tmp_path) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    wrong_target = tmp_path / "wrong.env"
    wrong_target.write_text("WRONG=1\n", encoding="utf-8")

    context.repo_env_path.unlink()
    context.repo_env_path.symlink_to(wrong_target)

    report = run_status()

    assert report.state == "broken"
    assert report.repo_env_status == "symlink mismatch"
    assert report.vault_env_status == "present"
    assert ".env.local is not linked to the managed vault file" in report.issues
    assert report.suggested_action == "envctl repair"


def test_status_when_vault_env_is_missing(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.vault_env_path.unlink()

    report = run_status()

    assert report.state == "missing vault"
    assert report.project_slug == context.project_slug
    assert report.project_id == context.project_id
    assert report.vault_env_status == "missing"
    assert "managed vault env file does not exist" in report.issues
    assert report.suggested_action == "envctl init"