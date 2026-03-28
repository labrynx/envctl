from __future__ import annotations

import stat

from envctl.services.init_service import run_init


def test_init_creates_vault_file_and_symlink(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)

    context = run_init()

    assert context.vault_env_path.exists()
    assert context.repo_env_path.is_symlink()
    assert context.repo_env_path.resolve() == context.vault_env_path.resolve()
    assert stat.S_IMODE(context.vault_project_dir.stat().st_mode) == 0o700
    assert stat.S_IMODE(context.vault_env_path.stat().st_mode) == 0o600
