from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.add_service as add_service
from envctl.domain.contract import Contract, VariableSpec
from envctl.domain.operations import AddVariableRequest
from envctl.domain.project import ProjectContext
from tests.support.contexts import make_project_context


def make_context(tmp_path: Path) -> ProjectContext:
    repo_root = tmp_path / "repo"
    repo_root.mkdir(parents=True, exist_ok=True)

    vault_dir = tmp_path / "vault" / "demo--prj_aaaaaaaaaaaaaaaa"

    return make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        repo_contract_path=repo_root / ".envctl.yaml",
        vault_project_dir=vault_dir,
        vault_values_path=vault_dir / "values.env",
        vault_state_path=vault_dir / "state.json",
    )


def test_apply_request_to_spec_replaces_requested_fields() -> None:
    spec = VariableSpec(name="APP_NAME")

    updated, inferred_spec, inferred_fields_used = add_service._apply_request_to_spec(
        spec,
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
            override_type="string",
            override_required=False,
            override_sensitive=False,
            override_description="Demo app",
            override_default="a",
            override_example="demo",
            override_format="json",
            override_pattern=r"^[a-z]+$",
            override_choices=("a", "b"),
        ),
    )

    assert updated.required is False
    assert updated.sensitive is False
    assert updated.description == "Demo app"
    assert updated.default == "a"
    assert updated.example == "demo"
    assert updated.format == "json"
    assert updated.pattern == r"^[a-z]+$"
    assert updated.choices == ("a", "b")
    assert inferred_spec is None
    assert inferred_fields_used == ()


def test_apply_request_to_spec_returns_inferred_spec_when_no_overrides() -> None:
    spec = VariableSpec(
        name="APP_NAME",
        description="Existing",
        type="string",
        required=True,
        sensitive=False,
    )

    updated, inferred_spec, inferred_fields_used = add_service._apply_request_to_spec(
        spec,
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        ),
    )

    assert updated == spec
    assert inferred_spec == {
        "type": "string",
        "required": True,
        "sensitive": False,
        "description": "Existing",
    }
    assert inferred_fields_used == ("type", "required", "sensitive", "description")


def test_run_add_creates_contract_and_entry(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    returned_context, result = add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        )
    )

    assert returned_context == context
    assert result.contract_created is True
    assert result.contract_updated is True
    assert result.contract_entry_created is True
    assert context.vault_values_path.exists()
    assert context.repo_contract_path.exists()


def test_run_add_uses_existing_contract_and_updates_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    existing = VariableSpec(name="APP_NAME", description="Existing description")
    contract = Contract(version=1, variables={"APP_NAME": existing})

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: contract)

    _, result = add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        )
    )

    assert result.contract_created is False
    assert result.contract_entry_created is False
    assert result.contract_updated is True
    assert result.inferred_spec is not None


def test_run_add_applies_overrides(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
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


def test_run_add_applies_format_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    add_service.run_add(
        AddVariableRequest(
            key="TEST_JSON",
            value='{"ok": true}',
            override_format="json",
        )
    )

    content = context.repo_contract_path.read_text(encoding="utf-8")
    assert "format: json" in content


def test_run_add_rejects_invalid_format_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    with pytest.raises(add_service.ValidationError, match=r"Invalid variable format"):
        add_service.run_add(
            AddVariableRequest(
                key="TEST_JSON",
                value='{"ok": true}',
                override_format="xml",
            )
        )


def test_run_add_rejects_format_for_non_string_type(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    with pytest.raises(add_service.ValidationError, match=r"only be used with type 'string'"):
        add_service.run_add(
            AddVariableRequest(
                key="PORT",
                value="3000",
                override_type="int",
                override_format="json",
            )
        )


def test_run_add_writes_value_to_vault(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    add_service.run_add(
        AddVariableRequest(
            key="APP_NAME",
            value="demo",
        )
    )

    content = context.vault_values_path.read_text(encoding="utf-8")
    assert "APP_NAME=demo" in content


def test_run_add_updates_existing_vault_value(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    context.vault_project_dir.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=old\n", encoding="utf-8")

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
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


def test_run_add_updates_existing_contract_when_spec_changes(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    existing = VariableSpec(name="APP_NAME", description="Old description")
    contract = Contract(version=1, variables={"APP_NAME": existing})

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
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


def test_run_add_writes_contract_when_existing_spec_is_recomputed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_context(tmp_path)
    existing = VariableSpec(name="APP_NAME", description="Existing description")
    contract = Contract(version=1, variables={"APP_NAME": existing})

    monkeypatch.setattr(
        add_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
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

    assert result.contract_updated is True
    assert len(written_contracts) == 1
