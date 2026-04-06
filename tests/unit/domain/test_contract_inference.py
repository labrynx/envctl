from __future__ import annotations

from envctl.domain.contract_inference import (
    infer_choices,
    infer_default,
    infer_description,
    infer_example,
    infer_pattern,
    infer_sensitive,
    infer_spec,
    infer_type,
    looks_like_placeholder,
)


def test_infer_type_detects_int_from_port_key() -> None:
    assert infer_type("PORT", "8080") == "int"
    assert infer_type("HTTP_PORT", "3000") == "int"


def test_infer_type_detects_bool_from_key_and_value() -> None:
    assert infer_type("DEBUG", "false") == "bool"
    assert infer_type("ENABLE_CACHE", "anything") == "bool"
    assert infer_type("FEATURE_FLAG", "true") == "bool"


def test_infer_type_detects_url() -> None:
    assert infer_type("DATABASE_URL", "postgres://localhost/db") == "url"
    assert infer_type("APP_ENDPOINT", "https://example.com") == "url"


def test_infer_type_falls_back_to_string() -> None:
    assert infer_type("APP_NAME", "demo") == "string"


def test_infer_sensitive_detects_public_url_hints() -> None:
    assert infer_sensitive("PUBLIC_URL") is False
    assert infer_sensitive("APP_URL") is False


def test_infer_sensitive_detects_secret_like_keys() -> None:
    assert infer_sensitive("API_KEY") is True
    assert infer_sensitive("JWT_SECRET") is True
    assert infer_sensitive("DATABASE_URL") is True


def test_infer_description_uses_known_mapping() -> None:
    assert infer_description("PORT") == "Application port"


def test_infer_description_humanizes_unknown_key() -> None:
    assert infer_description("MY_CUSTOM_VALUE") == "My custom value"


def test_infer_choices_detects_node_env() -> None:
    assert infer_choices("NODE_ENV", "development") == (
        "development",
        "test",
        "staging",
        "production",
    )


def test_infer_choices_detects_environment_short_values() -> None:
    assert infer_choices("ENVIRONMENT", "dev") == ("dev", "staging", "prod")


def test_infer_choices_detects_log_level() -> None:
    assert infer_choices("LOG_LEVEL", "info") == (
        "debug",
        "info",
        "warning",
        "error",
        "critical",
    )


def test_infer_choices_returns_empty_for_unknown_keys() -> None:
    assert infer_choices("APP_NAME", "demo") == ()


def test_infer_pattern_detects_slug_like_values() -> None:
    assert infer_pattern("APP_NAME", "demo-app") == r"^[a-z0-9-]+$"
    assert infer_pattern("SERVICE_NAME", "api-service") == r"^[a-z0-9-]+$"


def test_infer_pattern_returns_none_when_not_safe() -> None:
    assert infer_pattern("APP_NAME", "Demo App") is None
    assert infer_pattern("PORT", "3000") is None


def test_looks_like_placeholder_detects_common_placeholders() -> None:
    assert looks_like_placeholder("changeme") is True
    assert looks_like_placeholder("<secret>") is True
    assert looks_like_placeholder("your-api-key-here") is True
    assert looks_like_placeholder("replace-this") is True


def test_looks_like_placeholder_returns_false_for_real_values() -> None:
    assert looks_like_placeholder("demo") is False
    assert looks_like_placeholder("https://example.com") is False


def test_infer_default_handles_int_bool_and_placeholder() -> None:
    assert infer_default("PORT", "3000", "int") == 3000
    assert infer_default("DEBUG", "true", "bool") is True
    assert infer_default("DEBUG", "no", "bool") is False
    assert infer_default("API_KEY", "changeme", "string") is None


def test_infer_example_returns_none_for_placeholder() -> None:
    assert (
        infer_example(
            "API_KEY",
            "changeme",
            inferred_type="string",
            sensitive=True,
        )
        is None
    )


def test_infer_example_returns_url_and_safe_values() -> None:
    assert (
        infer_example(
            "DATABASE_URL",
            "postgres://localhost/db",
            inferred_type="url",
            sensitive=True,
        )
        == "postgres://localhost/db"
    )
    assert (
        infer_example(
            "APP_NAME",
            "demo",
            inferred_type="string",
            sensitive=False,
        )
        == "demo"
    )


def test_infer_example_returns_none_for_sensitive_non_url_values() -> None:
    assert (
        infer_example(
            "API_KEY",
            "super-secret",
            inferred_type="string",
            sensitive=True,
        )
        is None
    )


def test_infer_spec_builds_complete_spec() -> None:
    spec = infer_spec("NODE_ENV", "development")

    assert spec.name == "NODE_ENV"
    assert spec.type == "string"
    assert spec.required is True
    assert spec.sensitive is False
    assert spec.description == "Runtime environment"
    assert spec.default is None
    assert spec.example == "development"
    assert spec.choices == ("development", "production", "staging", "test")
