from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

import envctl.services.add_service as add_service
from envctl.domain.contract import Contract, VariableSpec


def make_context(tmp_path: Path) -> SimpleNamespace:
    vault_dir = tmp_path / "vault" / "demo--abc123"
    return SimpleNamespace(
        repo_contract_path=tmp_path / ".envctl.schema.yaml",
        vault_project_dir=vault_dir,
        vault_values_path=vault_dir / "values.env",
    )


def test_stringify_handles_none_and_scalars() -> None:
    assert add_service._stringify(None) is None
    assert add_service._stringify(3) == "3"
    assert add_service._stringify(True) == "True"


def test_prompt_optional_returns_default_for_blank_answer() -> None:
    result = add_service._prompt_optional(
        lambda message, secret, default: "   ",
        "Description",
        default="fallback",
    )

    assert result == "fallback"


def test_prompt_optional_returns_trimmed_answer() -> None:
    result = add_service._prompt_optional(
        lambda message, secret, default: " custom ",
        "Description",
        default=None,
    )

    assert result == "custom"


def test_prompt_choices_returns_default_when_blank() -> None:
    result = add_service._prompt_choices(
        lambda message, secret, default: "",
        default=("a", "b"),
    )

    assert result == ("a", "b")


def test_prompt_choices_parses_csv() -> None:
    result = add_service._prompt_choices(
        lambda message, secret, default: "a, b, c",
        default=(),
    )

    assert result == ("a", "b", "c")


def test_apply_overrides_replaces_requested_fields() -> None:
    spec = VariableSpec(name="APP_NAME")

    updated = add_service._apply_overrides(
        spec,
        override_type="string",
        override_required=False,
        override_sensitive=False,
        override_description="Demo app",
        override_default="demo",
        override_example="demo",
        override_pattern=r"^[a-z]+$",
        override_choices=("a", "b"),
    )

    assert updated.required is False
    assert updated.sensitive is False
    assert updated.description == "Demo app"
    assert updated.default == "demo"
    assert updated.example == "demo"
    assert updated.pattern == r"^[a-z]+$"
    assert updated.choices == ("a", "b")


def test_edit_spec_interactively_updates_fields() -> None:
    answers = iter(["int", "Description", "42", "example", r"^\d+$", "a, b"])
    confirms = iter([False, False])

    spec = VariableSpec(
        name="PORT",
        type="string",
        required=True,
        sensitive=True,
        description="",
        default=None,
        example=None,
        pattern=None,
        choices=(),
    )

    updated = add_service._edit_spec_interactively(
        spec,
        prompt=lambda message, secret, default: next(answers),
        confirm=lambda message, default: next(confirms),
    )

    assert updated.type == "int"
    assert updated.required is False
    assert updated.sensitive is False
    assert updated.description == "Description"
    assert updated.default == "42"
    assert updated.example == "example"
    assert updated.pattern == r"^\d+$"
    assert updated.choices == ("a", "b")


def test_run_add_creates_contract_and_entry(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    returned_context, result = add_service.run_add("APP_NAME", "demo")

    assert returned_context is context
    assert result.contract_created is True
    assert result.contract_updated is True
    assert result.contract_entry_created is True
    assert context.vault_values_path.exists()
    assert context.repo_contract_path.exists()


def test_run_add_uses_existing_spec_when_present(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)
    existing = VariableSpec(name="APP_NAME", description="Existing description")
    contract = Contract(version=1, variables={"APP_NAME": existing})

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: contract)

    _, result = add_service.run_add("APP_NAME", "demo")

    assert result.contract_created is False
    assert result.contract_entry_created is False
    assert result.inferred_spec is None


def test_run_add_requires_callbacks_when_interactive(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    with pytest.raises(ValueError, match="Interactive add requires prompt and confirm callbacks"):
        add_service.run_add("APP_NAME", "demo", interactive=True)


def test_run_add_applies_overrides_and_interactive_edit(tmp_path: Path, monkeypatch) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(add_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(add_service, "load_contract_optional", lambda path: None)

    _, result = add_service.run_add(
        "APP_NAME",
        "demo",
        interactive=True,
        prompt=lambda message, secret, default: default or "",
        confirm=lambda message, default: default,
        override_description="Overridden description",
        override_sensitive=False,
    )

    assert result.contract_updated is True
    content = context.repo_contract_path.read_text(encoding="utf-8")
    assert "Overridden description" in content
    assert "sensitive: false" in content
