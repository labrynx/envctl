from __future__ import annotations

from envctl.services.init_service import run_init
from envctl.services.remove_service import run_remove


def test_remove_deletes_managed_state_and_restores_repo_env(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()
    context.vault_env_path.write_text("KEY=VALUE\n", encoding="utf-8")

    result = run_remove(force=True)

    assert result.removed_repo_symlink is True
    assert result.restored_repo_env_file is True
    assert result.removed_repo_metadata is True
    assert result.removed_vault_env is True

    assert context.repo_env_path.exists()
    assert not context.repo_env_path.is_symlink()
    assert context.repo_env_path.read_text(encoding="utf-8") == "KEY=VALUE\n"

    assert not context.repo_metadata_path.exists()
    assert not context.vault_env_path.exists()


def test_remove_leaves_regular_repo_env_untouched(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    context.repo_env_path.unlink()
    context.repo_env_path.write_text("LOCAL_ONLY=1\n", encoding="utf-8")

    monkeypatch.setattr("typer.confirm", lambda *args, **kwargs: True)

    result = run_remove()

    assert result.left_regular_repo_env_untouched is True
    assert result.restored_repo_env_file is False

    assert context.repo_env_path.exists()
    assert context.repo_env_path.read_text(encoding="utf-8") == "LOCAL_ONLY=1\n"
    assert not context.repo_metadata_path.exists()
    assert not context.vault_env_path.exists()


def test_remove_removes_broken_symlink_without_restoration(
    isolated_env,
    repo_dir,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.chdir(repo_dir)
    context = run_init()

    wrong_target = tmp_path / "wrong.env"
    wrong_target.write_text("WRONG=1\n", encoding="utf-8")

    context.repo_env_path.unlink()
    context.repo_env_path.symlink_to(wrong_target)

    monkeypatch.setattr("typer.confirm", lambda *args, **kwargs: True)

    result = run_remove()

    assert result.removed_repo_symlink is True
    assert result.removed_broken_repo_symlink is True
    assert result.restored_repo_env_file is False
    assert not context.repo_env_path.exists()
    assert not context.repo_metadata_path.exists()
    assert not context.vault_env_path.exists()
