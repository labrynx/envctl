from __future__ import annotations

import pytest

from envctl.errors import LinkError, ProjectDetectionError
from envctl.services.init_service import run_init
from envctl.services.repair_service import run_repair


def test_repair_force_true_relinks_regular_file_without_prompt(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    context.repo_env_path.unlink()
    context.repo_env_path.write_text("LOCAL_ONLY=1\n", encoding="utf-8")

    repaired = run_repair(force=True)

    backups = list(repo_dir.glob(".env.local.backup-*"))
    assert len(backups) == 1
    assert repaired.repo_env_path.is_symlink()
    assert repaired.repo_env_path.resolve() == repaired.vault_env_path.resolve()


def test_repair_aborts_if_confirmation_is_rejected(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    context.repo_env_path.unlink()
    context.repo_env_path.write_text("LOCAL_ONLY=1\n", encoding="utf-8")

    def deny(_message: str, _default: bool) -> bool:
        return False

    with pytest.raises(LinkError):
        run_repair(force=False, confirm=deny)


def test_repair_fails_when_vault_env_is_missing(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.vault_env_path.unlink()

    with pytest.raises(ProjectDetectionError):
        run_repair(force=True)
