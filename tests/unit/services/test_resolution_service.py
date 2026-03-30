from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.resolution_service as resolution_service
from envctl.domain.contract import Contract
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_standard_contract, make_variable_spec


def test_load_contract_for_context_uses_repo_contract_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_context = make_project_context(repo_contract_path="/tmp/project/.envctl.schema.yaml")
    captured: dict[str, Path] = {}
    contract = make_contract()

    def fake_load_contract(path: Path) -> Contract:
        captured["path"] = path
        return contract

    monkeypatch.setattr(resolution_service, "load_contract", fake_load_contract)

    result = load_contract_for_context(fake_context)

    assert result is contract
    assert captured["path"] == fake_context.repo_contract_path


def test_resolve_environment_prefers_system_over_profile_and_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_standard_contract()
    context = make_project_context()

    staging_path = context.vault_project_dir / "profiles" / "staging.env"

    def fake_load_env_file(path: Path) -> dict[str, str]:
        assert path == staging_path
        return {
            "APP_NAME": "from-profile",
            "DATABASE_URL": "https://profile.example.com",
            "UNKNOWN_KEY": "x",
        }

    monkeypatch.setattr(resolution_service, "load_env_file", fake_load_env_file)
    monkeypatch.setenv("APP_NAME", "from-system")
    monkeypatch.setenv("DATABASE_URL", "https://system.example.com")
    monkeypatch.setenv("DEBUG", "true")

    report = resolve_environment(context, contract, active_profile="staging")

    assert report.missing_required == ()
    assert report.invalid_keys == ()
    assert report.unknown_keys == ("UNKNOWN_KEY",)

    assert report.values["APP_NAME"].value == "from-system"
    assert report.values["APP_NAME"].source == "system"

    assert report.values["DATABASE_URL"].value == "https://system.example.com"
    assert report.values["DATABASE_URL"].source == "system"
    assert report.values["DATABASE_URL"].masked is True

    assert report.values["DEBUG"].value == "true"
    assert report.values["DEBUG"].source == "system"

    assert report.values["PORT"].value == "3000"
    assert report.values["PORT"].source == "default"


def test_resolve_environment_uses_local_values_env_for_local_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(vault_values_path="/tmp/vault.env")
    contract = make_standard_contract()

    def fake_load_env_file(path: Path) -> dict[str, str]:
        assert path == context.vault_values_path
        return {
            "APP_NAME": "from-vault",
            "DATABASE_URL": "https://vault.example.com",
        }

    monkeypatch.setattr(resolution_service, "load_env_file", fake_load_env_file)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)

    report = resolve_environment(context, contract, active_profile="local")

    assert report.missing_required == ()
    assert report.invalid_keys == ()
    assert report.values["APP_NAME"].value == "from-vault"
    assert report.values["APP_NAME"].source == "vault"
    assert report.values["DATABASE_URL"].source == "vault"
    assert report.values["PORT"].source == "default"


def test_resolve_environment_does_not_fallback_to_values_env_for_explicit_profiles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_standard_contract()
    context = make_project_context()

    staging_path = context.vault_project_dir / "profiles" / "staging.env"

    def fake_load_env_file(path: Path) -> dict[str, str]:
        assert path == staging_path
        return {}

    monkeypatch.setattr(resolution_service, "load_env_file", fake_load_env_file)
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PORT", raising=False)

    report = resolve_environment(context, contract, active_profile="staging")

    assert report.missing_required == ("APP_NAME", "DATABASE_URL")
    assert report.invalid_keys == ()
    assert "PORT" in report.values
    assert report.values["PORT"].value == "3000"
    assert report.values["PORT"].source == "default"


def test_resolve_environment_marks_invalid_int_bool_url_choice_and_pattern(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_standard_contract()
    context = make_project_context(vault_values_path="/tmp/vault.env")

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

    report = resolve_environment(context, contract, active_profile="local")

    assert report.missing_required == ()
    assert report.invalid_keys == ("DATABASE_URL", "DEBUG", "ENVIRONMENT", "PORT", "SLUG")

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


def test_resolve_environment_supports_custom_contract_types(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "RETRY_COUNT": make_variable_spec(name="RETRY_COUNT", type="int", required=True),
            "ENABLE_CACHE": make_variable_spec(name="ENABLE_CACHE", type="bool", required=True),
            "SERVICE_URL": make_variable_spec(name="SERVICE_URL", type="url", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    monkeypatch.setattr(
        resolution_service,
        "load_env_file",
        lambda _path: {
            "RETRY_COUNT": "3",
            "ENABLE_CACHE": "true",
            "SERVICE_URL": "https://example.com",
        },
    )
    monkeypatch.delenv("RETRY_COUNT", raising=False)
    monkeypatch.delenv("ENABLE_CACHE", raising=False)
    monkeypatch.delenv("SERVICE_URL", raising=False)

    report = resolve_environment(context, contract, active_profile="local")

    assert report.is_valid is True
    assert report.missing_required == ()
    assert report.invalid_keys == ()
    assert report.values["RETRY_COUNT"].source == "vault"
    assert report.values["ENABLE_CACHE"].source == "vault"
    assert report.values["SERVICE_URL"].source == "vault"
