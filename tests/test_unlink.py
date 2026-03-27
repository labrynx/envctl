from __future__ import annotations

from envctl.services.init_service import run_init
from envctl.services.unlink_service import run_unlink


def test_unlink_removes_repo_symlink_only(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    assert context.vault_env_path.exists()
    assert context.repo_env_path.is_symlink()

    result = run_unlink()

    assert result.removed is True
    assert not result.context.repo_env_path.exists()
    assert result.context.vault_env_path.exists()


def test_unlink_is_noop_when_repo_env_is_missing(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.repo_env_path.unlink()

    result = run_unlink()

    assert result.removed is False
    assert result.context.vault_env_path.exists()


def test_unlink_is_noop_when_repo_env_is_regular_file(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.repo_env_path.unlink()
    context.repo_env_path.write_text("LOCAL_ONLY=1\n", encoding="utf-8")

    result = run_unlink()

    assert result.removed is False
    assert result.context.repo_env_path.exists()
    assert not result.context.repo_env_path.is_symlink()
    assert result.context.repo_env_path.read_text(encoding="utf-8") == "LOCAL_ONLY=1\n"
    assert result.context.vault_env_path.exists()