from __future__ import annotations

from pathlib import Path

import pytest

from envctl.errors import LinkError
from envctl.services.init_service import run_init
from envctl.services.repair_service import run_repair


def test_repair_recreates_missing_symlink(isolated_env, repo_dir, monkeypatch) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    assert context.repo_env_path.is_symlink()
    context.repo_env_path.unlink()

    repaired = run_repair()

    assert repaired.repo_env_path.is_symlink()
    assert repaired.repo_env_path.resolve() == repaired.vault_env_path.resolve()


def test_repair_fixes_wrong_symlink(isolated_env, repo_dir, monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    wrong_target = tmp_path / "wrong.env"
    wrong_target.write_text("WRONG=1\n", encoding="utf-8")

    context.repo_env_path.unlink()
    context.repo_env_path.symlink_to(wrong_target)

    repaired = run_repair()

    assert repaired.repo_env_path.is_symlink()
    assert repaired.repo_env_path.resolve() == repaired.vault_env_path.resolve()


def test_repair_can_backup_regular_file_before_relink(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    context.repo_env_path.unlink()
    context.repo_env_path.write_text("LOCAL_ONLY=1\n", encoding="utf-8")

    monkeypatch.setattr("typer.confirm", lambda *args, **kwargs: True)

    repaired = run_repair()

    backups = list(repo_dir.glob(".env.local.backup-*"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "LOCAL_ONLY=1\n"
    assert repaired.repo_env_path.is_symlink()
    assert repaired.repo_env_path.resolve() == repaired.vault_env_path.resolve()


def test_repair_aborts_if_user_declines_backup(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    context.repo_env_path.unlink()
    context.repo_env_path.write_text("LOCAL_ONLY=1\n", encoding="utf-8")

    monkeypatch.setattr("typer.confirm", lambda *args, **kwargs: False)

    with pytest.raises(LinkError):
        run_repair()

    assert context.repo_env_path.exists()
    assert not context.repo_env_path.is_symlink()