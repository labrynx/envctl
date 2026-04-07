from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest
import yaml

import envctl.services.init_service as init_service
from envctl.domain.contract_inference import (
    infer_choices,
    infer_description,
    infer_pattern,
    infer_sensitive,
    infer_spec,
    infer_type,
    looks_like_placeholder,
)
from envctl.domain.operations import InitResult
from envctl.domain.project import ProjectContext
from tests.support.contexts import make_project_context


def make_context(tmp_path: Path) -> ProjectContext:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    return make_project_context(
        project_slug="demo",
        project_key="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=repo_root,
        repo_remote=None,
        binding_source="local",
        repo_contract_path=repo_root / ".envctl.yaml",
        vault_project_dir=tmp_path / "vault" / "projects" / "demo--prj_aaaaaaaaaaaaaaaa",
        repo_env_path=repo_root / ".env.local",
    )


def load_yaml(path: Path) -> dict[str, Any]:
    return cast(dict[str, Any], yaml.safe_load(path.read_text(encoding="utf-8")))


def test_run_init_creates_vault_files_and_preserves_existing_contract(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    context.repo_contract_path.write_text(
        "version: 1\nvariables:\n  APP_NAME: {}\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    result_context, result = init_service.run_init()

    assert result_context == context
    assert result == InitResult(contract_created=False)

    assert context.vault_project_dir.exists()
    assert context.vault_values_path.exists()
    assert context.vault_values_path.read_text(encoding="utf-8") == ""


def test_run_init_creates_starter_contract_when_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    result_context, result = init_service.run_init(contract_mode="starter")

    assert result_context == context
    assert result == InitResult(
        contract_created=True,
        contract_template="starter",
        contract_skipped=False,
    )

    contract = load_yaml(context.repo_contract_path)
    assert contract["version"] == 1
    assert set(cast(dict[str, Any], contract["variables"])) == {
        "APP_NAME",
        "PORT",
        "DATABASE_URL",
        "DEBUG",
    }

    variables = cast(dict[str, Any], contract["variables"])

    app_name = cast(dict[str, Any], variables["APP_NAME"])
    assert app_name["type"] == "string"
    assert app_name["required"] is True
    assert app_name["sensitive"] is False
    assert app_name["example"] == "demo"

    port = cast(dict[str, Any], variables["PORT"])
    assert port["type"] == "int"
    assert port["default"] == 3000

    database_url = cast(dict[str, Any], variables["DATABASE_URL"])
    assert database_url["type"] == "url"
    assert database_url["sensitive"] is True

    debug = cast(dict[str, Any], variables["DEBUG"])
    assert debug["type"] == "bool"
    assert debug["default"] is False


def test_run_init_skips_contract_when_requested(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    result_context, result = init_service.run_init(contract_mode="skip")

    assert result_context == context
    assert result == InitResult(
        contract_created=False,
        contract_template=None,
        contract_skipped=True,
    )
    assert not context.repo_contract_path.exists()


def test_run_init_creates_contract_from_env_example(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    (context.repo_root / ".env.example").write_text(
        "\n".join(
            [
                'APP_NAME="demo-app"',
                'PORT="3001"',
                'DEBUG="true"',
                'DATABASE_URL="postgres://user:pass@localhost:5432/app"',
                'NODE_ENV="development"',
                'PUBLIC_URL="https://example.com"',
                'SLUG="demo-app"',
                'API_KEY="changeme"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    _, result = init_service.run_init(contract_mode="example")

    assert result == InitResult(
        contract_created=True,
        contract_template="example",
        contract_skipped=False,
    )

    contract = load_yaml(context.repo_contract_path)
    variables = cast(dict[str, Any], contract["variables"])

    assert cast(dict[str, Any], variables["APP_NAME"])["type"] == "string"
    assert cast(dict[str, Any], variables["APP_NAME"])["example"] == "demo-app"

    assert cast(dict[str, Any], variables["PORT"])["type"] == "int"
    assert cast(dict[str, Any], variables["PORT"])["default"] == 3001

    assert cast(dict[str, Any], variables["DEBUG"])["type"] == "bool"
    assert cast(dict[str, Any], variables["DEBUG"])["default"] is True

    assert cast(dict[str, Any], variables["DATABASE_URL"])["type"] == "url"
    assert (
        cast(dict[str, Any], variables["DATABASE_URL"])["example"]
        == "postgres://user:pass@localhost:5432/app"
    )
    assert cast(dict[str, Any], variables["DATABASE_URL"])["sensitive"] is True

    assert cast(dict[str, Any], variables["NODE_ENV"])["choices"] == [
        "development",
        "production",
        "staging",
        "test",
    ]

    assert cast(dict[str, Any], variables["PUBLIC_URL"])["type"] == "url"
    assert cast(dict[str, Any], variables["PUBLIC_URL"])["sensitive"] is False
    assert cast(dict[str, Any], variables["PUBLIC_URL"])["example"] == "https://example.com"

    assert cast(dict[str, Any], variables["SLUG"])["pattern"] == "^[a-z0-9-]+$"

    assert cast(dict[str, Any], variables["API_KEY"])["sensitive"] is True
    assert "example" not in cast(dict[str, Any], variables["API_KEY"])
    assert "default" not in cast(dict[str, Any], variables["API_KEY"])


def test_run_init_example_mode_falls_back_to_starter_when_example_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    _, result = init_service.run_init(contract_mode="example")

    assert result == InitResult(
        contract_created=True,
        contract_template="example",
        contract_skipped=False,
    )

    contract = load_yaml(context.repo_contract_path)
    assert set(cast(dict[str, Any], contract["variables"])) == {
        "APP_NAME",
        "PORT",
        "DATABASE_URL",
        "DEBUG",
    }


def test_run_init_ask_mode_uses_example_when_confirm_accepts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    (context.repo_root / ".env.example").write_text(
        'APP_NAME="demo"\n',
        encoding="utf-8",
    )

    confirmations: list[tuple[str, bool]] = []

    def fake_confirm(message: str, default: bool) -> bool:
        confirmations.append((message, default))
        return True

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    _, result = init_service.run_init(contract_mode="ask", confirm=fake_confirm)

    assert result == InitResult(
        contract_created=True,
        contract_template="example",
        contract_skipped=False,
    )
    assert len(confirmations) == 1
    assert ".env.example" in confirmations[0][0]


def test_run_init_ask_mode_uses_starter_after_declining_example(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    (context.repo_root / ".env.example").write_text(
        'APP_NAME="demo"\n',
        encoding="utf-8",
    )

    answers = iter([False, True])
    confirmations: list[str] = []

    def fake_confirm(message: str, default: bool) -> bool:
        confirmations.append(message)
        return next(answers)

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    _, result = init_service.run_init(contract_mode="ask", confirm=fake_confirm)

    assert result == InitResult(
        contract_created=True,
        contract_template="starter",
        contract_skipped=False,
    )
    assert len(confirmations) == 2
    assert ".env.example" in confirmations[0]
    assert "starter contract scaffold" in confirmations[1]


def test_run_init_ask_mode_skips_after_declining_all_prompts(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    confirmations: list[str] = []

    def fake_confirm(message: str, default: bool) -> bool:
        confirmations.append(message)
        return False

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    _, result = init_service.run_init(contract_mode="ask", confirm=fake_confirm)

    assert result == InitResult(
        contract_created=False,
        contract_template=None,
        contract_skipped=True,
    )
    assert len(confirmations) == 1
    assert "starter contract scaffold" in confirmations[0]
    assert not context.repo_contract_path.exists()


def test_run_init_ask_mode_without_confirm_uses_example_when_available(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    (context.repo_root / ".env.example").write_text(
        'APP_NAME="demo"\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    _, result = init_service.run_init(contract_mode="ask", confirm=None)

    assert result == InitResult(
        contract_created=True,
        contract_template="example",
        contract_skipped=False,
    )


def test_run_init_ask_mode_without_confirm_uses_starter_when_example_is_missing(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )

    _, result = init_service.run_init(contract_mode="ask", confirm=None)

    assert result == InitResult(
        contract_created=True,
        contract_template="starter",
        contract_skipped=False,
    )


def test_build_contract_from_example_skips_invalid_keys(tmp_path: Path) -> None:
    context = make_context(tmp_path)
    (context.repo_root / ".env.example").write_text(
        "\n".join(
            [
                'APP_NAME="demo-app"',
                'app_name="bad"',
                '1INVALID="bad"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    contract = init_service._build_contract_from_example(context)

    assert contract["version"] == 1
    assert set(cast(dict[str, Any], contract["variables"])) == {"APP_NAME", "app_name"}


def test_build_contract_from_example_falls_back_to_starter_when_no_valid_keys(
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)
    (context.repo_root / ".env.example").write_text(
        "\n".join(
            [
                'app_name="bad"',
                '1INVALID="bad"',
                "",
            ]
        ),
        encoding="utf-8",
    )

    contract = init_service._build_contract_from_example(context)

    assert set(cast(dict[str, Any], contract["variables"])) == {"app_name"}


def test_infer_type_does_not_mark_non_numeric_port_like_value_as_int() -> None:
    assert infer_type("WORKERS", "12x") == "string"


def test_infer_spec_bool_false_default() -> None:
    spec = infer_spec("DEBUG", "false")

    assert spec.type == "bool"
    assert spec.default is False


def test_infer_spec_url_sets_example() -> None:
    spec = infer_spec("PUBLIC_URL", "https://example.com")

    assert spec.type == "url"
    assert spec.example == "https://example.com"


def test_infer_spec_known_non_sensitive_key_sets_example() -> None:
    spec = infer_spec("HOST", "localhost")

    assert spec.type == "string"
    assert spec.sensitive is False
    assert spec.example == "localhost"


def test_infer_spec_generic_non_sensitive_value_sets_example() -> None:
    spec = infer_spec("REGION", "eu-west-1")

    assert spec.type == "string"
    assert spec.sensitive is False
    assert spec.example == "eu-west-1"


def test_infer_type_detects_bool_from_enable_prefix() -> None:
    assert infer_type("ENABLE_CACHE", "maybe") == "bool"


def test_infer_type_detects_int_from_numeric_value() -> None:
    assert infer_type("WORKERS", "42") == "int"


def test_infer_sensitive_recognizes_public_url_hints() -> None:
    assert infer_sensitive("PUBLIC_URL") is False
    assert infer_sensitive("DATABASE_URL") is True


def test_infer_description_falls_back_to_humanized_text() -> None:
    assert infer_description("SERVICE_ACCOUNT_NAME") == "Service account name"


def test_infer_choices_for_environment_short_values() -> None:
    assert infer_choices("ENVIRONMENT", "prod") == ("dev", "staging", "prod")


def test_infer_choices_for_environment_long_values() -> None:
    assert infer_choices("ENVIRONMENT", "production") == (
        "development",
        "test",
        "staging",
        "production",
    )


def test_infer_choices_for_log_level() -> None:
    assert infer_choices("LOG_LEVEL", "info") == (
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    )


def test_infer_pattern_returns_none_when_not_obvious() -> None:
    assert infer_pattern("APP_NAME", "My App") is None


def test_looks_like_placeholder_detects_angle_brackets() -> None:
    assert looks_like_placeholder("<your-token>") is True


def test_looks_like_placeholder_detects_replace_marker() -> None:
    assert looks_like_placeholder("replace_this_value") is True


def test_infer_spec_port_without_numeric_value_has_no_default() -> None:
    spec = infer_spec("PORT", "not-a-number")

    assert spec.type == "int"
    assert spec.default is None


def test_infer_type_detects_bool_from_boolean_like_value() -> None:
    assert infer_type("FEATURE_FLAG", "yes") == "bool"


def test_infer_type_detects_url_from_scheme_pattern() -> None:
    assert infer_type("SERVICE_ENDPOINT", "postgres://localhost/app") == "url"


def test_looks_like_placeholder_detects_your_prefix_variants() -> None:
    assert looks_like_placeholder("your_token_here") is True
    assert looks_like_placeholder("your-token-here") is True


def test_looks_like_placeholder_detects_your_prefix_only() -> None:
    assert looks_like_placeholder("your-custom-value") is True
    assert looks_like_placeholder("your_custom_value") is True


def test_run_init_installs_managed_git_hook_when_repo_is_git(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(init_service, "is_git_repository", lambda repo_root: True)
    monkeypatch.setattr(init_service, "get_local_git_config", lambda repo_root, key: None)

    captured: dict[str, str] = {}
    monkeypatch.setattr(
        init_service,
        "set_local_git_config",
        lambda repo_root, key, value: captured.update({"key": key, "value": value}),
    )

    _, result = init_service.run_init(contract_mode="skip")

    hook_path = context.repo_root / ".githooks" / "pre-commit"
    assert result.git_guard_installed is True
    assert hook_path.exists()
    assert "envctl guard secrets" in hook_path.read_text(encoding="utf-8")
    assert captured == {"key": "core.hooksPath", "value": ".githooks"}


def test_run_init_does_not_overwrite_foreign_hooks_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    context = make_context(tmp_path)

    monkeypatch.setattr(
        init_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(init_service, "is_git_repository", lambda repo_root: True)
    monkeypatch.setattr(init_service, "get_local_git_config", lambda repo_root, key: ".husky")

    _, result = init_service.run_init(contract_mode="skip")

    assert result.git_guard_installed is False
    assert result.git_guard_reason is not None
    assert "core.hooksPath=.husky" in result.git_guard_reason
