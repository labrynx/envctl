from __future__ import annotations

from envctl.services.init_service import run_init


def test_init_creates_vault_file_and_symlink(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)

    context = run_init()

    assert context.vault_env_path.exists()
    assert context.repo_env_path.is_symlink()
    assert context.repo_env_path.resolve() == context.vault_env_path.resolve()