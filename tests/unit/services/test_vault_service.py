from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import envctl.services.vault_service as vault_service
from envctl.domain.operations import (
    EditResult,
    VaultCheckResult,
    VaultPruneResult,
    VaultShowResult,
)
from envctl.errors import ExecutionError


def make_context(tmp_path: Path) -> SimpleNamespace:
    vault_project_dir = tmp_path / "vault" / "demo--abc123"
    vault_values_path = vault_project_dir / "values.env"
    repo_contract_path = tmp_path / "repo" / ".envctl.schema.yaml"

    repo_contract_path.parent.mkdir(parents=True, exist_ok=True)

    return SimpleNamespace(
        vault_project_dir=vault_project_dir,
        vault_values_path=vault_values_path,
        repo_contract_path=repo_contract_path,
    )


def test_load_vault_context_returns_context(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        vault_service,
        "load_project_context",
        lambda: ("config", context),
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


def test_has_private_file_permissions_returns_false_when_stat_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        vault_service.os,
        "stat",
        lambda path: (_ for _ in ()).throw(OSError("boom")),
    )

    assert vault_service._has_private_file_permissions("/tmp/missing.env") is False


def test_has_private_file_permissions_returns_true_for_600(monkeypatch) -> None:
    class FakeStat:
        st_mode = 0o100600

    monkeypatch.setattr(vault_service.os, "stat", lambda path: FakeStat())

    assert vault_service._has_private_file_permissions("/tmp/file.env") is True


def test_has_private_file_permissions_returns_false_for_non_600(monkeypatch) -> None:
    class FakeStat:
        st_mode = 0o100644

    monkeypatch.setattr(vault_service.os, "stat", lambda path: FakeStat())

    assert vault_service._has_private_file_permissions("/tmp/file.env") is False


def test_run_vault_edit_opens_file_and_returns_result(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)

    captured: dict[str, object] = {}

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
    monkeypatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: True)
    monkeypatch.setattr(vault_service, "open_file", lambda path: None)

    def fake_load_env_file(path: Path) -> dict[str, str]:
        raise OSError("boom")

    monkeypatch.setattr(vault_service, "load_env_file", fake_load_env_file)

    with pytest.raises(ExecutionError, match="Unable to read edited vault file"):
        vault_service.run_vault_edit()


def test_run_vault_check_returns_non_existing_result(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)

    result_context, result = vault_service.run_vault_check()

    assert result_context is context
    assert result == VaultCheckResult(
        path=context.vault_values_path,
        exists=False,
        parseable=False,
        private_permissions=False,
        key_count=0,
    )


def test_run_vault_check_returns_existing_result(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\nPORT=3000\n", encoding="utf-8")

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
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


def test_run_vault_check_raises_when_file_cannot_be_read(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)

    def fake_load_env_file(path: Path) -> dict[str, str]:
        raise OSError("boom")

    monkeypatch.setattr(vault_service, "load_env_file", fake_load_env_file)

    with pytest.raises(ExecutionError, match="Unable to read vault file"):
        vault_service.run_vault_check()


def test_run_vault_path_returns_string_path(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)

    result_context, path = vault_service.run_vault_path()

    assert result_context is context
    assert path == str(context.vault_values_path)


def test_run_vault_show_returns_non_existing_result(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)

    result_context, result = vault_service.run_vault_show()

    assert result_context is context
    assert result == VaultShowResult(
        path=context.vault_values_path,
        exists=False,
        values={},
    )


def test_run_vault_show_returns_values(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "load_env_file", lambda path: {"APP_NAME": "demo"})

    result_context, result = vault_service.run_vault_show()

    assert result_context is context
    assert result == VaultShowResult(
        path=context.vault_values_path,
        exists=True,
        values={"APP_NAME": "demo"},
    )


def test_run_vault_show_raises_when_file_cannot_be_read(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)

    def fake_load_env_file(path: Path) -> dict[str, str]:
        raise OSError("boom")

    monkeypatch.setattr(vault_service, "load_env_file", fake_load_env_file)

    with pytest.raises(ExecutionError, match="Unable to read vault file"):
        vault_service.run_vault_show()


def test_run_vault_prune_raises_when_contract_is_invalid(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: True)

    def fake_load_contract(path: Path):
        raise vault_service.ContractError("invalid contract")

    monkeypatch.setattr(vault_service, "load_contract", fake_load_contract)

    with pytest.raises(ExecutionError, match="Cannot prune vault without a valid contract"):
        vault_service.run_vault_prune()


def test_run_vault_prune_returns_without_changes_when_no_unknown_keys(
    monkeypatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)
    monkeypatch.setattr(
        vault_service,
        "load_contract",
        lambda path: SimpleNamespace(variables={"APP_NAME": object(), "PORT": object()}),
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


def test_run_vault_prune_returns_without_changes_when_confirmation_is_rejected(
    monkeypatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)
    monkeypatch.setattr(
        vault_service,
        "load_contract",
        lambda path: SimpleNamespace(variables={"APP_NAME": object()}),
    )
    monkeypatch.setattr(
        vault_service,
        "load_env_file",
        lambda path: {"APP_NAME": "demo", "OLD_KEY": "legacy"},
    )

    captured: dict[str, object] = {}

    def fake_confirm(message: str, default: bool) -> bool:
        captured["message"] = message
        captured["default"] = default
        return False

    result_context, result = vault_service.run_vault_prune(confirm=fake_confirm)

    assert result_context is context
    assert result == VaultPruneResult(
        path=context.vault_values_path,
        removed_keys=(),
        kept_keys=2,
    )
    assert captured["message"] == "Remove 1 unknown key(s) from the local vault?"
    assert captured["default"] is False


def test_run_vault_prune_removes_unknown_keys_when_confirmed(
    monkeypatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)
    monkeypatch.setattr(
        vault_service,
        "load_contract",
        lambda path: SimpleNamespace(variables={"APP_NAME": object()}),
    )
    monkeypatch.setattr(
        vault_service,
        "load_env_file",
        lambda path: {"APP_NAME": "demo", "OLD_KEY": "legacy"},
    )

    written: dict[str, object] = {}

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

    result_context, result = vault_service.run_vault_prune(
        confirm=lambda message, default: True,
    )

    assert result_context is context
    assert result == VaultPruneResult(
        path=context.vault_values_path,
        removed_keys=("OLD_KEY",),
        kept_keys=1,
    )
    assert written["path"] == context.vault_values_path
    assert written["content"] == "serialized:{'APP_NAME': 'demo'}"


def test_run_vault_prune_removes_unknown_keys_without_confirmation_when_yes(
    monkeypatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(vault_service, "_load_vault_context", lambda: context)
    monkeypatch.setattr(vault_service, "_ensure_vault_file", lambda ctx: False)
    monkeypatch.setattr(
        vault_service,
        "load_contract",
        lambda path: SimpleNamespace(variables={"APP_NAME": object()}),
    )
    monkeypatch.setattr(
        vault_service,
        "load_env_file",
        lambda path: {"APP_NAME": "demo", "OLD_KEY": "legacy"},
    )
    monkeypatch.setattr(vault_service, "write_text_atomic", lambda path, content: None)
    monkeypatch.setattr(vault_service, "dump_env", lambda data: "APP_NAME=demo\n")

    result_context, result = vault_service.run_vault_prune(
        yes=True,
        confirm=lambda message, default: (_ for _ in ()).throw(
            AssertionError("confirm should not be called")
        ),
    )

    assert result_context is context
    assert result == VaultPruneResult(
        path=context.vault_values_path,
        removed_keys=("OLD_KEY",),
        kept_keys=1,
    )


def test_run_edit_delegates_to_run_vault_edit(monkeypatch, tmp_path: Path) -> None:
    context = make_context(tmp_path)
    expected = EditResult(path=context.vault_values_path, created=True)

    monkeypatch.setattr(
        vault_service,
        "run_vault_edit",
        lambda: (context, expected),
    )

    result_context, result = vault_service.run_edit()

    assert result_context is context
    assert result == expected
