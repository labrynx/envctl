from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.resolution_service as resolution_service
from envctl.domain.contract import Contract
from envctl.domain.project import ProjectContext
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from tests.support.contexts import make_project_context
from tests.support.contracts import make_contract, make_standard_contract, make_variable_spec


def patch_loaded_profile_values(
    monkeypatch: pytest.MonkeyPatch,
    *,
    context: ProjectContext,
    values: dict[str, str],
    profile: str = "local",
) -> Path:
    """Patch profile loading through the repository-backed service hook."""
    path = (
        context.vault_values_path
        if profile == "local"
        else context.vault_project_dir / "profiles" / f"{profile}.env"
    )
    monkeypatch.setattr(
        resolution_service,
        "load_profile_values",
        lambda _context, _profile, require_existing_explicit=False: (_profile, path, values),
    )
    return path


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

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        profile="staging",
        values={
            "APP_NAME": "from-profile",
            "DATABASE_URL": "https://profile.example.com",
            "UNKNOWN_KEY": "x",
        },
    )
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

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={
            "APP_NAME": "from-vault",
            "DATABASE_URL": "https://vault.example.com",
        },
    )
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

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        profile="staging",
        values={},
    )
    monkeypatch.delenv("APP_NAME", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PORT", raising=False)
    monkeypatch.delenv("DEBUG", raising=False)

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

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={
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

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={
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


def test_resolve_environment_validates_string_format_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "TEST_JSON": make_variable_spec(
                name="TEST_JSON",
                type="string",
                format="json",
                required=True,
            ),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"TEST_JSON": '{"ok": true}'},
    )
    monkeypatch.delenv("TEST_JSON", raising=False)

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["TEST_JSON"].valid is True

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"TEST_JSON": '{\\"broken\\"}'},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ("TEST_JSON",)
    assert report.values["TEST_JSON"].detail == "Expected a valid JSON string"


def test_resolve_environment_validates_string_format_url_and_csv(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "PUBLIC_ENDPOINT": make_variable_spec(
                name="PUBLIC_ENDPOINT",
                type="string",
                format="url",
                required=True,
            ),
            "TAGS": make_variable_spec(
                name="TAGS",
                type="string",
                format="csv",
                required=True,
            ),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={
            "PUBLIC_ENDPOINT": "not-a-url",
            "TAGS": " , ",
        },
    )
    monkeypatch.delenv("PUBLIC_ENDPOINT", raising=False)
    monkeypatch.delenv("TAGS", raising=False)

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ("PUBLIC_ENDPOINT", "TAGS")
    assert report.values["PUBLIC_ENDPOINT"].detail == "Expected a valid URL"
    assert report.values["TAGS"].detail == "Expected a non-empty CSV string"


def test_resolve_environment_expands_contract_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "USER": make_variable_spec(name="USER", type="string", required=True, sensitive=False),
            "PASSWORD": make_variable_spec(
                name="PASSWORD",
                type="string",
                required=True,
                sensitive=True,
            ),
            "AUTH": make_variable_spec(name="AUTH", type="string", required=True, sensitive=False),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={
            "USER": "neo4j",
            "PASSWORD": "super-secret",
            "AUTH": "${USER}/${PASSWORD}",
        },
    )
    monkeypatch.delenv("USER", raising=False)
    monkeypatch.delenv("PASSWORD", raising=False)
    monkeypatch.delenv("AUTH", raising=False)

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["AUTH"].value == "neo4j/super-secret"
    assert report.values["AUTH"].masked is True
    assert report.values["AUTH"].raw_value is None
    assert report.values["AUTH"].expansion_status == "expanded"
    assert report.values["AUTH"].expansion_refs == ("USER", "PASSWORD")


def test_resolve_environment_expands_external_process_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "CACHE_DIR": make_variable_spec(name="CACHE_DIR", type="string", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"CACHE_DIR": "${HOME}/.cache/demo"},
    )
    monkeypatch.setenv("HOME", "/tmp/example-home")
    monkeypatch.delenv("CACHE_DIR", raising=False)

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["CACHE_DIR"].value == "/tmp/example-home/.cache/demo"
    assert report.values["CACHE_DIR"].expansion_status == "expanded"
    assert report.values["CACHE_DIR"].expansion_refs == ("HOME",)


def test_resolve_environment_prefers_contract_values_over_process_for_expansion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "HOME": make_variable_spec(name="HOME", type="string", required=True),
            "TARGET": make_variable_spec(name="TARGET", type="string", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"HOME": "/contract-home", "TARGET": "${HOME}/work"},
    )
    monkeypatch.setenv("HOME", "/process-home")
    monkeypatch.delenv("TARGET", raising=False)

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["HOME"].source == "system"
    assert report.values["TARGET"].value == "/process-home/work"


def test_resolve_environment_supports_recursive_expansion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "A": make_variable_spec(name="A", type="string", required=True),
            "B": make_variable_spec(name="B", type="string", required=True),
            "C": make_variable_spec(name="C", type="string", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"A": "${B}", "B": "${C}", "C": "value"},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["A"].value == "value"
    assert report.values["A"].expansion_refs == ("B",)


def test_resolve_environment_allows_empty_references(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "EMPTY": make_variable_spec(name="EMPTY", type="string", required=False),
            "TARGET": make_variable_spec(name="TARGET", type="string", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"EMPTY": "", "TARGET": "x${EMPTY}y"},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["TARGET"].value == "xy"


def test_resolve_environment_marks_missing_references_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "TARGET": make_variable_spec(name="TARGET", type="string", required=True),
            "OPTIONAL": make_variable_spec(name="OPTIONAL", type="string", required=False),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"TARGET": "${OPTIONAL}"},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ("TARGET",)
    assert "Expansion reference error" in (report.values["TARGET"].detail or "")


def test_resolve_environment_marks_cycles_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "A": make_variable_spec(name="A", type="string", required=True),
            "B": make_variable_spec(name="B", type="string", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"A": "${B}", "B": "${A}"},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ("A", "B")
    assert "Expansion cycle error" in (report.values["A"].detail or "")
    assert report.values["A"].expansion_status == "error"


def test_resolve_environment_reports_syntax_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "TARGET": make_variable_spec(name="TARGET", type="string", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"TARGET": "prefix-${VAR"},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ("TARGET",)
    assert "Expansion syntax error" in (report.values["TARGET"].detail or "")


def test_resolve_environment_leaves_dollar_literals_untouched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "TARGET": make_variable_spec(name="TARGET", type="string", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"TARGET": "$HOME"},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["TARGET"].value == "$HOME"
    assert report.values["TARGET"].expansion_status == "none"


def test_resolve_environment_validates_types_after_expansion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    contract = make_contract(
        {
            "BASE_PORT": make_variable_spec(name="BASE_PORT", type="string", required=True),
            "PORT": make_variable_spec(name="PORT", type="int", required=True),
        }
    )
    context = make_project_context(vault_values_path="/tmp/vault.env")

    patch_loaded_profile_values(
        monkeypatch,
        context=context,
        values={"BASE_PORT": "3000", "PORT": "${BASE_PORT}"},
    )

    report = resolve_environment(context, contract, active_profile="local")

    assert report.invalid_keys == ()
    assert report.values["PORT"].value == "3000"
    assert report.values["PORT"].valid is True
