from __future__ import annotations

from envctl.errors import LinkError
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


def test_remove_aborts_when_confirmation_is_rejected(
    isolated_env,
    repo_dir,
    monkeypatch,
) -> None:
    monkeypatch.chdir(repo_dir)
    run_init()

    def deny(_message: str, _default: bool) -> bool:
        return False

    try:
        run_remove(force=False, confirm=deny)
        raise AssertionError("Expected LinkError")
    except LinkError:
        pass
