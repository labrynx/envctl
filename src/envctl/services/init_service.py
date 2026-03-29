"""Init service."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

import yaml

from envctl.adapters.dotenv import load_env_file
from envctl.constants import CONTRACT_VERSION, DEFAULT_ENV_EXAMPLE_FILENAME
from envctl.domain.project import ConfirmFn, ProjectContext
from envctl.repository.state_repository import write_state
from envctl.services.context_service import load_project_context
from envctl.utils.filesystem import ensure_dir, ensure_file
from envctl.utils.permissions import ensure_private_dir_permissions, ensure_private_file_permissions

InitContractMode = Literal["ask", "example", "starter", "skip"]
InitContractTemplate = Literal["example", "starter"] | None

_SECRET_KEY_PARTS = {
    "SECRET",
    "TOKEN",
    "PASSWORD",
    "PASS",
    "API_KEY",
    "PRIVATE_KEY",
    "ACCESS_KEY",
    "CLIENT_SECRET",
    "JWT",
}

_PUBLIC_URL_HINTS = {
    "PUBLIC_URL",
    "BASE_URL",
    "APP_URL",
    "SITE_URL",
}

_DESCRIPTION_MAP = {
    "APP_NAME": "Application name",
    "PORT": "Application port",
    "DEBUG": "Debug mode",
    "DATABASE_URL": "Primary database connection URL",
    "REDIS_URL": "Redis connection URL",
    "NODE_ENV": "Runtime environment",
    "ENVIRONMENT": "Runtime environment",
    "LOG_LEVEL": "Application log level",
    "HOST": "Application host",
}

_ENVIRONMENT_CHOICES = ("development", "test", "staging", "production")
_SHORT_ENVIRONMENT_CHOICES = ("dev", "staging", "prod")
_LOG_LEVEL_CHOICES = ("debug", "info", "warning", "error", "critical")

_PLACEHOLDER_VALUES = {
    "",
    "changeme",
    "change-me",
    "replace-me",
    "example",
    "todo",
    "tbd",
    "your-api-key-here",
    "your_api_key_here",
    "your-token-here",
    "your_token_here",
}


@dataclass(frozen=True)
class InitResult:
    """Outcome of project initialization."""

    contract_created: bool
    contract_template: InitContractTemplate = None
    contract_skipped: bool = False


def run_init(
    project_name: str | None = None,
    contract_mode: InitContractMode = "ask",
    confirm: ConfirmFn | None = None,
) -> tuple[ProjectContext, InitResult]:
    """Initialize the current project inside the local vault."""
    _config, context = load_project_context(project_name=project_name)

    ensure_dir(context.vault_project_dir)
    ensure_private_dir_permissions(context.vault_project_dir)

    ensure_file(context.vault_values_path, "")
    ensure_private_file_permissions(context.vault_values_path)

    write_state(
        context.vault_state_path,
        project_slug=context.project_slug,
        project_id=context.project_id,
        repo_root=str(context.repo_root),
    )
    ensure_private_file_permissions(context.vault_state_path)

    init_result = _ensure_contract(
        context=context,
        contract_mode=contract_mode,
        confirm=confirm,
    )

    return context, init_result


def _ensure_contract(
    *,
    context: ProjectContext,
    contract_mode: InitContractMode,
    confirm: ConfirmFn | None,
) -> InitResult:
    """Create a contract when it does not exist yet."""
    if context.repo_contract_path.exists():
        return InitResult(contract_created=False)

    resolved_mode = _resolve_contract_mode(
        context=context,
        contract_mode=contract_mode,
        confirm=confirm,
    )

    if resolved_mode == "skip":
        return InitResult(
            contract_created=False,
            contract_template=None,
            contract_skipped=True,
        )

    if resolved_mode == "example":
        contract_payload = _build_contract_from_example(context)
        _write_contract_payload(context, contract_payload)
        return InitResult(
            contract_created=True,
            contract_template="example",
        )

    contract_payload = _build_starter_contract(context)
    _write_contract_payload(context, contract_payload)
    return InitResult(
        contract_created=True,
        contract_template="starter",
    )


def _resolve_contract_mode(
    *,
    context: ProjectContext,
    contract_mode: InitContractMode,
    confirm: ConfirmFn | None,
) -> Literal["example", "starter", "skip"]:
    """Resolve the effective contract bootstrap mode."""
    if contract_mode in {"example", "starter", "skip"}:
        return contract_mode

    env_example_path = context.repo_root / DEFAULT_ENV_EXAMPLE_FILENAME
    has_example = env_example_path.exists()

    if confirm is None:
        return "example" if has_example else "starter"

    if has_example and confirm(
        f"No contract file found. Create one from {DEFAULT_ENV_EXAMPLE_FILENAME}?",
        True,
    ):
        return "example"

    if confirm("Create a starter contract scaffold instead?", True):
        return "starter"

    return "skip"


def _write_contract_payload(context: ProjectContext, payload: dict[str, object]) -> None:
    """Write a contract payload to the repository."""
    content = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    context.repo_contract_path.write_text(content, encoding="utf-8")


def _build_contract_from_example(context: ProjectContext) -> dict[str, object]:
    """Infer a contract from a repository .env.example file."""
    env_example_path = context.repo_root / DEFAULT_ENV_EXAMPLE_FILENAME
    example_values = load_env_file(env_example_path)

    if not example_values:
        return _build_starter_contract(context)

    variables: dict[str, dict[str, object]] = {}

    for key, raw_value in example_values.items():
        if not _is_valid_contract_key(key):
            continue
        variables[key] = _infer_variable_spec(key, raw_value)

    if not variables:
        return _build_starter_contract(context)

    return {
        "version": CONTRACT_VERSION,
        "variables": variables,
    }


def _build_starter_contract(context: ProjectContext) -> dict[str, object]:
    """Create a small starter contract scaffold."""
    return {
        "version": CONTRACT_VERSION,
        "variables": {
            "APP_NAME": {
                "type": "string",
                "required": True,
                "sensitive": False,
                "description": "Application name",
                "example": context.project_slug,
            },
            "PORT": {
                "type": "int",
                "required": True,
                "sensitive": False,
                "description": "Application port",
                "default": 3000,
            },
            "DATABASE_URL": {
                "type": "url",
                "required": True,
                "sensitive": True,
                "description": "Primary database connection URL",
                "example": "postgres://user:password@localhost:5432/app",
            },
            "DEBUG": {
                "type": "bool",
                "required": False,
                "sensitive": False,
                "description": "Debug mode",
                "default": False,
            },
        },
    }


def _infer_variable_spec(key: str, raw_value: str) -> dict[str, object]:
    """Infer a contract variable spec from a key and example value."""
    inferred_type = _infer_type(key, raw_value)
    sensitive = _infer_sensitive(key)
    description = _infer_description(key)

    spec: dict[str, object] = {
        "type": inferred_type,
        "required": True,
        "sensitive": sensitive,
        "description": description,
    }

    choices = _infer_choices(key, raw_value)
    if choices:
        spec["choices"] = list(choices)

    pattern = _infer_pattern(key, raw_value)
    if pattern:
        spec["pattern"] = pattern

    if _looks_like_placeholder(raw_value):
        return spec

    if inferred_type == "int":
        try:
            spec["default"] = int(raw_value)
        except ValueError:
            pass
        return spec

    if inferred_type == "bool":
        lowered = raw_value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            spec["default"] = True
        elif lowered in {"false", "0", "no"}:
            spec["default"] = False
        return spec

    if inferred_type == "url":
        spec["example"] = raw_value
        return spec

    if not sensitive and key.upper() in {
        "APP_NAME",
        "SERVICE_NAME",
        "HOST",
        "NODE_ENV",
        "ENVIRONMENT",
    }:
        spec["example"] = raw_value
        return spec

    if not sensitive and raw_value.strip():
        spec["example"] = raw_value

    return spec


def _infer_type(key: str, raw_value: str) -> str:
    """Infer the variable type."""
    upper_key = key.upper()
    stripped = raw_value.strip()

    if upper_key == "PORT" or upper_key.endswith("_PORT"):
        return "int"

    if upper_key == "DEBUG" or upper_key.startswith("ENABLE_") or upper_key.startswith("USE_"):
        return "bool"

    if stripped.lower() in {"true", "false", "1", "0", "yes", "no"}:
        return "bool"

    if re.fullmatch(r"-?\d+", stripped):
        return "int"

    if upper_key.endswith("_URL"):
        return "url"

    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", stripped):
        return "url"

    return "string"


def _infer_sensitive(key: str) -> bool:
    """Infer whether the variable is sensitive."""
    upper_key = key.upper()

    if upper_key in _PUBLIC_URL_HINTS:
        return False

    if upper_key.endswith("_URL"):
        return upper_key not in _PUBLIC_URL_HINTS

    return any(part in upper_key for part in _SECRET_KEY_PARTS)


def _infer_description(key: str) -> str:
    """Infer a human-readable description."""
    upper_key = key.upper()

    if upper_key in _DESCRIPTION_MAP:
        return _DESCRIPTION_MAP[upper_key]

    words = upper_key.split("_")
    human = " ".join(word.lower() for word in words)
    return human[:1].upper() + human[1:]


def _infer_choices(key: str, raw_value: str) -> tuple[str, ...]:
    """Infer choices for well-known variables."""
    upper_key = key.upper()
    lowered = raw_value.strip().lower()

    if upper_key == "NODE_ENV":
        return _ENVIRONMENT_CHOICES

    if upper_key == "ENVIRONMENT":
        if lowered in _SHORT_ENVIRONMENT_CHOICES:
            return _SHORT_ENVIRONMENT_CHOICES
        if lowered in _ENVIRONMENT_CHOICES:
            return _ENVIRONMENT_CHOICES

    if upper_key == "LOG_LEVEL":
        return _LOG_LEVEL_CHOICES

    return ()


def _infer_pattern(key: str, raw_value: str) -> str | None:
    """Infer a validation pattern when it is very obvious."""
    upper_key = key.upper()
    stripped = raw_value.strip()

    if upper_key in {"APP_NAME", "SERVICE_NAME", "SLUG"} and re.fullmatch(r"[a-z0-9-]+", stripped):
        return r"^[a-z0-9-]+$"

    return None


def _looks_like_placeholder(value: str) -> bool:
    """Return whether a value looks like a placeholder."""
    normalized = value.strip().lower()

    if normalized in _PLACEHOLDER_VALUES:
        return True

    if normalized.startswith("<") and normalized.endswith(">"):
        return True

    if normalized.startswith("your_") or normalized.startswith("your-"):
        return True

    if "changeme" in normalized or "replace" in normalized:
        return True

    return False


def _is_valid_contract_key(key: str) -> bool:
    """Return whether a key can be used in the contract."""
    return re.fullmatch(r"[A-Z][A-Z0-9_]*", key) is not None
