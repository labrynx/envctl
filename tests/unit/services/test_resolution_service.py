from __future__ import annotations

from types import SimpleNamespace

import envctl.services.resolution_service as resolution_service
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from tests.support.contracts import make_contract, make_standard_contract, make_variable_spec


def test_load_contract_for_context_uses_repo_contract_path(monkeypatch) -> None:
    fake_context = SimpleNamespace(repo_contract_path="/tmp/project/.envctl.schema.yaml")
    captured: dict[str, object] = {}

    def fake_load_contract(path):
        captured["path"] = path
        return "contract-object"

    monkeypatch.setattr(resolution_service, "load_contract", fake_load_contract)

    result = load_contract_for_context(fake_context)

    assert result == "contract-object"
    assert captured["path"] == fake_context.repo_contract_path


def test_resolve_environment_prefers_system_over_vault_and_default(monkeypatch) -> None:
    contract = make_standard_contract()
    context = SimpleNamespace(vault_values_path="/tmp/vault.env")

    monkeypatch.setattr(
        resolution_service,
        "load_env_file",
        lambda _path: {
            "APP_NAME": "from-vault",
            "DATABASE_URL": "https://vault.example.com",
            "UNKNOWN_KEY": "x",
        },
    )
    monkeypatch.setenv("APP_NAME", "from-system")
    monkeypatch.setenv("DATABASE_URL", "https://system.example.com")
    monkeypatch.setenv("DEBUG", "true")

    report = resolve_environment(context, contract)

    assert report.missing_required == []
    assert report.invalid_keys == []
    assert report.unknown_keys == ["UNKNOWN_KEY"]

    assert report.values["APP_NAME"].value == "from-system"
    assert report.values["APP_NAME"].source == "system"

    assert report.values["DATABASE_URL"].value == "https://system.example.com"
    assert report.values["DATABASE_URL"].source == "system"
    assert report.values["DATABASE_URL"].masked is True

    assert report.values["DEBUG"].value == "true"
    assert report.values["DEBUG"].source == "system"

    assert report.values["PORT"].value == "3000"
    assert report.values["PORT"].source == "default"


def test_resolve_environment_marks_missing_required_keys(monkeypatch) -> None:
    contract = make_standard_contract()
    context = SimpleNamespace(vault_values_path="/tmp/vault.env")

    monkeypatch.setattr(resolution_service, "load_env_file", lambda _path: {})
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    report = resolve_environment(context, contract)

    assert report.missing_required == ["APP_NAME", "DATABASE_URL"]
    assert report.invalid_keys == []
    assert "PORT" in report.values
    assert report.values["PORT"].value == "3000"
    assert report.values["PORT"].source == "default"


def test_resolve_environment_marks_invalid_int_bool_url_choice_and_pattern(monkeypatch) -> None:
    contract = make_standard_contract()
    context = SimpleNamespace(vault_values_path="/tmp/vault.env")

    monkeypatch.setattr(
        resolution_service,
        "load_env_file",
        lambda _path: {
            "APP_NAME": "demo",
            "PORT": "abc",
            "DEBUG": "maybe",
            "DATABASE_URL": "not-a-url",
            "ENVIRONMENT": "staging",
            "SLUG": "Bad Slug",
        },
    )
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("ENVIRONMENT", raising=False)
    monkeypatch.delenv("SLUG", raising=False)

    report = resolve_environment(context, contract)

    assert report.missing_required == []
    assert report.invalid_keys == ["DATABASE_URL", "DEBUG", "ENVIRONMENT", "PORT", "SLUG"]

    assert report.values["PORT"].valid is False
    assert report.values["PORT"].detail == "Expected an integer"

    assert report.values["DEBUG"].valid is False
    assert report.values["DEBUG"].detail == "Expected a boolean"

    assert report.values["DATABASE_URL"].valid is False
    assert report.values["DATABASE_URL"].detail == "Expected a valid URL"

    assert report.values["ENVIRONMENT"].valid is False
    assert report.values["ENVIRONMENT"].detail == "Expected one of: dev, prod"

    assert report.values["SLUG"].valid is False
    assert report.values["SLUG"].detail == "Value does not match pattern: ^[a-z0-9-]+$"


def test_resolve_environment_accepts_valid_bool_variants(monkeypatch) -> None:
    contract = make_contract(
        {
            "DEBUG": make_variable_spec(
                name="DEBUG",
                type="bool",
                required=True,
                sensitive=False,
            ),
        }
    )
    context = SimpleNamespace(vault_values_path="/tmp/vault.env")

    for value in ["true", "false", "1", "0", "yes", "no"]:
        monkeypatch.setattr(
            resolution_service,
            "load_env_file",
            lambda _path, value=value: {"DEBUG": value},
        )
        monkeypatch.delenv("DEBUG", raising=False)

        report = resolve_environment(context, contract)

        assert report.invalid_keys == []
        assert report.values["DEBUG"].valid is True
