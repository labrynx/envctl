from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import envctl.services.remove_service as remove_service


def make_context(tmp_path: Path) -> SimpleNamespace:
    vault_dir = tmp_path / "vault" / "demo--abc123"
    return SimpleNamespace(
        repo_contract_path=tmp_path / ".envctl.schema.yaml",
        vault_project_dir=vault_dir,
        vault_values_path=vault_dir / "values.env",
    )


def test_run_remove_returns_without_changes_when_confirmation_rejected(
    tmp_path: Path,
    monkeypatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        remove_service,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        remove_service,
        "load_contract_optional",
        lambda path: SimpleNamespace(variables={"API_KEY": object()}),
    )

    _, result = remove_service.run_remove(
        "API_KEY",
        yes=False,
        confirm=lambda message, default: False,
    )

    assert result.removed_from_vault is False
    assert result.removed_from_contract is False


def test_run_remove_removes_from_vault_and_contract(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True)
    context.vault_values_path.write_text("API_KEY=123\n", encoding="utf-8")

    contract = SimpleNamespace(variables={"API_KEY": object()})

    monkeypatch.setattr(
        remove_service,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(remove_service, "load_contract_optional", lambda path: contract)
    monkeypatch.setattr(
        remove_service,
        "remove_variable",
        lambda contract, key: SimpleNamespace(),
    )
    monkeypatch.setattr(remove_service, "write_contract", lambda path, contract: None)

    _, result = remove_service.run_remove("API_KEY", yes=True)

    assert result.removed_from_vault is True
    assert result.removed_from_contract is True
