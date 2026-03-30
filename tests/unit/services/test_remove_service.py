from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import envctl.services.remove_service as remove_service


def make_context(tmp_path: Path) -> SimpleNamespace:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = tmp_path / "vault" / "demo--prj_aaaaaaaaaaaaaaaa"

    return SimpleNamespace(
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=repo_root,
        repo_contract_path=repo_root / ".envctl.schema.yaml",
        vault_project_dir=vault_dir,
        vault_values_path=vault_dir / "values.env",
        vault_state_path=vault_dir / "state.json",
    )


def test_run_remove_returns_without_changes_when_key_is_missing(
    tmp_path: Path,
    monkeypatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        remove_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        remove_service,
        "load_contract_optional",
        lambda path: SimpleNamespace(variables={}),
    )

    _, result = remove_service.run_remove(
        key="API_KEY",
        remove_from_contract=False,
    )

    assert result.removed_from_vault is False
    assert result.removed_from_contract is False


def test_run_remove_removes_from_vault_and_contract(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True)
    context.vault_values_path.write_text("API_KEY=123\n", encoding="utf-8")

    updated_contract = SimpleNamespace(variables={})
    contract = SimpleNamespace(
        variables={"API_KEY": object()},
        without_variable=lambda key: updated_contract,
    )

    monkeypatch.setattr(
        remove_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(remove_service, "load_contract_optional", lambda path: contract)
    monkeypatch.setattr(remove_service, "write_contract", lambda path, contract: None)

    _, result = remove_service.run_remove(
        key="API_KEY",
        remove_from_contract=True,
    )

    assert result.removed_from_vault is True
    assert result.removed_from_contract is True
