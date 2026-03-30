from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import envctl.services.unset_service as unset_service


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


def test_run_unset_removes_key_and_marks_declared(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True)
    context.vault_values_path.write_text("API_KEY=123\n", encoding="utf-8")

    monkeypatch.setattr(
        unset_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
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
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        unset_service,
        "load_contract_optional",
        lambda path: (_ for _ in ()).throw(unset_service.ContractError("bad contract")),
    )

    _, result = unset_service.run_unset("API_KEY")

    assert result.removed_from_vault is False
    assert result.declared_in_contract is False
