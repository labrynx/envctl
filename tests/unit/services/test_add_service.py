from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import envctl.services.add_service as add_service
from envctl.domain.contract import Contract, VariableSpec
from envctl.domain.operations import AddVariableRequest


def make_context(tmp_path: Path) -> SimpleNamespace:
    vault_dir = tmp_path / "vault" / "demo--abc123"
    return SimpleNamespace(
        repo_contract_path=tmp_path / ".envctl.schema.yaml",
        vault_project_dir=vault_dir,
        vault_values_path=vault_dir / "values.env",
    )


def test_apply_request_to_spec_replaces_requested_fields() -> None:
    spec = VariableSpec(name="APP_NAME")

    updated = add_service._apply_request_to_spec(
        spec,
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
            override_type="string",
            override_required=False,
            override_sensitive=False,
            override_description="Demo app",
            override_default="demo",
            override_example="demo",
            override_pattern=r"^[a-z]+$",
            override_choices=("a", "b"),
        ),
    )

    assert updated.required is False
    assert updated.sensitive is False
    assert updated.description == "Demo app"
    assert updated.default == "demo"
    assert updated.example == "demo"
    assert updated.pattern == r"^[a-z]+$"
    assert updated.choices == ("a", "b")


def test_apply_request_to_spec_returns_same_spec_when_no_overrides() -> None:
    spec = VariableSpec(name="APP_NAME", description="Existing")

    updated = add_service._apply_request_to_spec(
        spec,
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        ),
    )

    assert updated == spec


def test_run_add_creates_contract_and_entry(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    returned_context, result = add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        )
    )

    assert returned_context is context
    assert result.contract_created is True
    assert result.contract_updated is True
    assert result.contract_entry_created is True
    assert result.declared_in_contract is True
    assert context.vault_values_path.exists()
    assert context.repo_contract_path.exists()


def test_run_add_uses_existing_spec_when_present(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    existing = VariableSpec(name="APP_NAME", description="Existing description")
    contract = Contract(version=1, variables={"APP_NAME": existing})

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: contract)

    _, result = add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        )
    )

    assert result.contract_created is False
    assert result.contract_entry_created is False
    assert result.inferred_spec is None


def test_run_add_applies_overrides(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    _, result = add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
            override_description="Overridden description",
            override_sensitive=False,
        )
    )

    assert result.contract_updated is True
    content = context.repo_contract_path.read_text(encoding="utf-8")
    assert "Overridden description" in content
    assert "sensitive: false" in content


def test_run_add_writes_value_to_vault(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        )
    )

    content = context.vault_values_path.read_text(encoding="utf-8")
    assert "APP_NAME=demo" in content


def test_run_add_updates_existing_vault_value(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=old\n", encoding="utf-8")

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="new",
        )
    )

    content = context.vault_values_path.read_text(encoding="utf-8")
    assert "APP_NAME=new" in content
    assert "APP_NAME=old" not in content


def test_run_add_updates_existing_contract_when_spec_changes(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    existing = VariableSpec(name="APP_NAME", description="Old description")
    contract = Contract(version=1, variables={"APP_NAME": existing})

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: contract)

    _, result = add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
            override_description="New description",
        )
    )

    assert result.contract_updated is True
    content = context.repo_contract_path.read_text(encoding="utf-8")
    assert "New description" in content


def test_run_add_does_not_rewrite_contract_when_existing_spec_is_unchanged(
    tmp_path: Path, monkeypatch
) -> None:
    context = make_context(tmp_path)
    existing = VariableSpec(name="APP_NAME", description="Existing description")
    contract = Contract(version=1, variables={"APP_NAME": existing})

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: contract)

    written_contracts: list[tuple[Path, Contract]] = []

    monkeypatch.setattr(
        add_service,
        "write_contract",
        lambda path, contract_obj: written_contracts.append((path, contract_obj)),
    )

    _, result = add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        )
    )

    assert result.contract_updated is False
    assert written_contracts == []
