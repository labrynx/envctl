from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import envctl.services.remove_service as remove_service
from envctl.domain.operations import RemovePlan
from tests.support.contexts import make_project_context


def make_context(tmp_path: Path):
    """Build a filesystem-backed project context for remove-service tests."""
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = tmp_path / "vault" / "demo--prj_aaaaaaaaaaaaaaaa"

    return make_project_context(
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
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    plan = RemovePlan(
        key="API_KEY",
        present_in_vault=False,
        declared_in_contract=False,
    )

    monkeypatch.setattr(
        remove_service,
        "load_contract_optional",
        lambda path: SimpleNamespace(variables={}),
    )

    result = remove_service.run_remove(
        context=context,
        plan=plan,
        remove_from_contract=False,
    )

    assert result.removed_from_vault is False
    assert result.removed_from_contract is False


def test_run_remove_removes_from_vault_and_contract(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("API_KEY=123\n", encoding="utf-8")

    plan = RemovePlan(
        key="API_KEY",
        present_in_vault=True,
        declared_in_contract=True,
    )

    updated_contract = SimpleNamespace(variables={})
    contract = SimpleNamespace(
        variables={"API_KEY": object()},
        without_variable=lambda key: updated_contract,
    )

    monkeypatch.setattr(remove_service, "load_contract_optional", lambda path: contract)
    monkeypatch.setattr(remove_service, "write_contract", lambda path, contract: None)

    result = remove_service.run_remove(
        context=context,
        plan=plan,
        remove_from_contract=True,
    )

    assert result.removed_from_vault is True
    assert result.removed_from_contract is True
