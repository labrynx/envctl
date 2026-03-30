from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

import envctl.services.vault_service as vault_service
from envctl.domain.operations import (
    EditResult,
    VaultCheckResult,
    VaultPruneResult,
    VaultShowResult,
)
from envctl.errors import ExecutionError
from tests.support.contexts import make_project_context


def make_context(tmp_path: Path):
    """Build a filesystem-backed project context for vault-service tests."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_project_dir = tmp_path / "vault" / "demo--prj_aaaaaaaaaaaaaaaa"
    vault_values_path = vault_project_dir / "values.env"
    repo_contract_path = repo_root / ".envctl.schema.yaml"

    return make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=repo_root,
        repo_contract_path=repo_contract_path,
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_values_path,
        vault_state_path=vault_project_dir / "state.json",
    )


def test_load_vault_context_returns_context(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: ("config", context),
    )

    assert vault_service._load_vault_context() is context


def test_ensure_vault_file_creates_file_and_returns_true_when_new(tmp_path: Path) -> None:
    context = make_context(tmp_path)

    created = vault_service._ensure_vault_file(context)

    assert created is True
    assert context.vault_project_dir.exists()
    assert context.vault_values_path.exists()
    assert context.vault_values_path.read_text(encoding="utf-8") == ""


def test_ensure_vault_file_returns_false_when_file_already_exists(tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    created = vault_service._ensure_vault_file(context)

    assert created is False
    assert context.vault_values_path.read_text(encoding="utf-8") == "APP_NAME=demo\n"


def test_has_private_file_permissions_returns_false_when_stat_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        vault_service.os,
        "stat",
        lambda path: (_ for _ in ()).throw(OSError("boom")),
    )

    assert vault_service._has_private_file_permissions("/tmp/missing.env") is False


def test_has_private_file_permissions_returns_true_for_600(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeStat:
        st_mode = 0o100600

    monkeypatch.setattr(vault_service.os, "stat", lambda path: FakeStat())

    assert vault_service._has_private_file_permissions("/tmp/file.env") is True


def test_has_private_file_permissions_returns_false_for_non_600(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeStat:
        st_mode = 0o100644

    monkeypatch.setattr(vault_service.os, "stat", lambda path: FakeStat())

    assert vault_service._has_private_file_permissions("/tmp/file.env") is False


def test_run_vault_edit_opens_file_and_returns_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)

    captured: dict[str, Any] = {}

    monkeypatch.setattr(
        vault_service,
        "open_file",
        lambda path: captured.update({"path": path}),
    )
    monkeypatch.setattr(
        vault_service,
        "load_env_file",
        lambda path: {"APP_NAME": "demo"},
    )

    result_context, result = vault_service.run_vault_edit()

    assert result_context is context
    assert result == EditResult(path=context.vault_values_path, created=False)
    assert captured["path"] == str(context.vault_values_path)


def test_run_vault_edit_raises_when_reloaded_file_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: True)
    monkeypatch.setattr(vault_service, "open_file", lambda path: None)

    def fake_load_env_file(path: Path) -> dict[str, str]:
        raise OSError("boom")

    monkeypatch.setattr(vault_service, "load_env_file", fake_load_env_file)

    with pytest.raises(ExecutionError, match="Unable to read edited vault file"):
        vault_service.run_vault_edit()


def test_run_vault_check_returns_non_existing_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )

    result_context, result = vault_service.run_vault_check()

    assert result_context is context
    assert result == VaultCheckResult(
        path=context.vault_values_path,
        exists=False,
        parseable=False,
        private_permissions=False,
        key_count=0,
    )


def test_run_vault_check_returns_existing_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\nPORT=3000\n", encoding="utf-8")

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(
        vault_service,
        "load_env_file",
        lambda path: {"APP_NAME": "demo", "PORT": "3000"},
    )
    monkeypatch.setattr(vault_service, "_has_private_file_permissions", lambda path: True)

    result_context, result = vault_service.run_vault_check()

    assert result_context is context
    assert result == VaultCheckResult(
        path=context.vault_values_path,
        exists=True,
        parseable=True,
        private_permissions=True,
        key_count=2,
    )


def test_run_vault_check_raises_when_file_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )

    def fake_load_env_file(path: Path) -> dict[str, str]:
        raise OSError("boom")

    monkeypatch.setattr(vault_service, "load_env_file", fake_load_env_file)

    with pytest.raises(ExecutionError, match="Unable to read vault file"):
        vault_service.run_vault_check()


def test_run_vault_path_returns_string_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )

    result_context, path = vault_service.run_vault_path()

    assert result_context is context
    assert path == str(context.vault_values_path)


def test_run_vault_show_returns_non_existing_result(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )

    result_context, result = vault_service.run_vault_show()

    assert result_context is context
    assert result == VaultShowResult(
        path=context.vault_values_path,
        exists=False,
        values={},
    )


def test_run_vault_show_returns_values(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(vault_service, "load_env_file", lambda path: {"APP_NAME": "demo"})

    result_context, result = vault_service.run_vault_show()

    assert result_context is context
    assert result == VaultShowResult(
        path=context.vault_values_path,
        exists=True,
        values={"APP_NAME": "demo"},
    )


def test_run_vault_show_raises_when_file_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )

    def fake_load_env_file(path: Path) -> dict[str, str]:
        raise OSError("boom")

    monkeypatch.setattr(vault_service, "load_env_file", fake_load_env_file)

    with pytest.raises(ExecutionError, match="Unable to read vault file"):
        vault_service.run_vault_show()


def test_get_unknown_vault_keys_raises_when_contract_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: True)

    def fake_load_contract(path: Path) -> Any:
        raise vault_service.ContractError("invalid contract")

    monkeypatch.setattr(vault_service, "load_contract", fake_load_contract)

    with pytest.raises(ExecutionError, match="Cannot inspect vault without a valid contract"):
        vault_service.get_unknown_vault_keys()


def test_run_vault_prune_raises_when_contract_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: True)

    def fake_load_contract(path: Path) -> Any:
        raise vault_service.ContractError("invalid contract")

    monkeypatch.setattr(vault_service, "load_contract", fake_load_contract)

    with pytest.raises(ExecutionError, match="Cannot inspect vault without a valid contract"):
        vault_service.run_vault_prune()


def test_run_vault_prune_returns_without_changes_when_no_unknown_keys(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)
    monkeypatch.setattr(
        vault_service,
        "load_contract",
        lambda path: type(
            "FakeContract", (), {"variables": {"APP_NAME": object(), "PORT": object()}}
        )(),
    )
    monkeypatch.setattr(
        vault_service,
        "load_env_file",
        lambda path: {"APP_NAME": "demo", "PORT": "3000"},
    )

    result_context, result = vault_service.run_vault_prune()

    assert result_context is context
    assert result == VaultPruneResult(
        path=context.vault_values_path,
        removed_keys=(),
        kept_keys=2,
    )


def test_run_vault_prune_removes_unknown_keys(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "_load_vault_context",
        lambda persist_binding=False: context,
    )
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)
    monkeypatch.setattr(
        vault_service,
        "load_contract",
        lambda path: type("FakeContract", (), {"variables": {"APP_NAME": object()}})(),
    )
    monkeypatch.setattr(
        vault_service,
        "load_env_file",
        lambda path: {"APP_NAME": "demo", "OLD_KEY": "legacy"},
    )

    written: dict[str, Any] = {}

    monkeypatch.setattr(
        vault_service,
        "write_text_atomic",
        lambda path, content: written.update({"path": path, "content": content}),
    )
    monkeypatch.setattr(
        vault_service,
        "dump_env",
        lambda data: f"serialized:{data}",
    )

    result_context, result = vault_service.run_vault_prune()

    assert result_context is context
    assert result == VaultPruneResult(
        path=context.vault_values_path,
        removed_keys=("OLD_KEY",),
        kept_keys=1,
    )
    assert written["path"] == context.vault_values_path
    assert written["content"] == "serialized:{'APP_NAME': 'demo'}"
