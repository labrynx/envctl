from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import envctl.services.unset_service as unset_service


def make_context(tmp_path: Path) -> SimpleNamespace:
    vault_dir = tmp_path / "vault" / "demo--abc123"
    return SimpleNamespace(
        repo_contract_path=tmp_path / ".envctl.schema.yaml",
        vault_project_dir=vault_dir,
        vault_values_path=vault_dir / "values.env",
    )


def test_run_unset_removes_key_and_marks_declared(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True)
    context.vault_values_path.write_text("API_KEY=123\n", encoding="utf-8")

    monkeypatch.setattr(
        unset_service,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        unset_service,
        "load_contract_optional",
        lambda path: SimpleNamespace(variables={"API_KEY": object()}),
    )

    _, result = unset_service.run_unset("API_KEY")

    assert result.removed_from_vault is True
    assert result.declared_in_contract is True


def test_run_unset_handles_invalid_contract(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True)
    context.vault_values_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(
        unset_service,
        "load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        unset_service,
        "load_contract_optional",
        lambda path: (_ for _ in ()).throw(unset_service.ContractError("bad contract")),
    )

    _, result = unset_service.run_unset("API_KEY")

    assert result.removed_from_vault is False
    assert result.declared_in_contract is False
