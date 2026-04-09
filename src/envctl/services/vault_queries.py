"""Query-oriented vault service implementations."""

from __future__ import annotations

from collections.abc import Callable
from logging import Logger
from pathlib import Path

from envctl.domain.app_config import AppConfig
from envctl.domain.operations import VaultCheckResult, VaultShowResult
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.repository.contract_repository import load_contract_optional
from envctl.repository.profile_repository import load_profile_values
from envctl.vault_crypto import VaultFileState


def _resolve_sensitive_keys_for_values(
    context: ProjectContext,
    values: dict[str, str],
) -> dict[str, bool]:
    """Resolve whether each vault key should be treated as sensitive."""
    contract = load_contract_optional(context.repo_contract_path)
    contract_variables = contract.variables if contract is not None else {}

    sensitive_keys: dict[str, bool] = {}
    for key in values:
        spec = contract_variables.get(key)
        sensitive_keys[key] = True if spec is None else spec.sensitive

    return sensitive_keys


def run_vault_check_impl(
    *,
    active_profile: str | None,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    require_no_plaintext_in_strict_mode: Callable[..., None],
    resolve_selected_profile: Callable[[ProjectContext, str | None], tuple[str, Path]],
    classify_vault_file: Callable[[ProjectContext, Path], tuple[VaultFileState, str]],
    is_world_writable: Callable[[Path], bool],
    logger: Logger,
) -> tuple[ProjectContext, str, VaultCheckResult]:
    """Check the current physical vault file for the active profile."""
    config, context = load_project_context()
    require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = resolve_selected_profile(context, active_profile)
    logger.debug(
        "Running vault check",
        extra={
            "active_profile": resolved_profile,
            "path": profile_path,
            "strict": config.encryption_strict,
        },
    )

    state, detail = classify_vault_file(context, profile_path)
    if state == "missing":
        result = VaultCheckResult(
            path=profile_path,
            exists=False,
            parseable=False,
            private_permissions=False,
            key_count=0,
            state="missing",
            detail=detail,
        )
        logger.debug(
            "Vault check result ready",
            extra={"active_profile": resolved_profile, "state": state, "exists": False},
        )
        return context, resolved_profile, result

    try:
        _resolved_profile, _path, values = load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
            allow_plaintext=not config.encryption_strict,
        )
        parseable = True
        key_count = len(values)
    except (ExecutionError, OSError, ValueError):
        parseable = False
        key_count = 0

    result = VaultCheckResult(
        path=profile_path,
        exists=True,
        parseable=parseable,
        private_permissions=not is_world_writable(profile_path),
        key_count=key_count,
        state=state,
        detail=detail,
    )
    logger.debug(
        "Vault check result ready",
        extra={
            "active_profile": resolved_profile,
            "state": state,
            "parseable": parseable,
            "key_count": key_count,
        },
    )
    return context, resolved_profile, result


def run_vault_path_impl(
    *,
    active_profile: str | None,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    resolve_selected_profile: Callable[[ProjectContext, str | None], tuple[str, Path]],
    logger: Logger,
) -> tuple[ProjectContext, str, Path]:
    """Return the current physical vault path for the active profile."""
    _config, context = load_project_context()
    resolved_profile, profile_path = resolve_selected_profile(context, active_profile)
    logger.debug(
        "Resolved vault path",
        extra={"active_profile": resolved_profile, "path": profile_path},
    )
    return context, resolved_profile, profile_path


def run_vault_show_impl(
    *,
    active_profile: str | None,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    require_no_plaintext_in_strict_mode: Callable[..., None],
    resolve_selected_profile: Callable[[ProjectContext, str | None], tuple[str, Path]],
    classify_vault_file: Callable[[ProjectContext, Path], tuple[VaultFileState, str]],
    logger: Logger,
) -> tuple[ProjectContext, str, VaultShowResult]:
    """Return the current physical vault content for the active profile."""
    config, context = load_project_context()
    require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = resolve_selected_profile(context, active_profile)
    logger.debug(
        "Running vault show",
        extra={
            "active_profile": resolved_profile,
            "path": profile_path,
            "strict": config.encryption_strict,
        },
    )
    state, detail = classify_vault_file(context, profile_path)

    exists = profile_path.exists()
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
        allow_plaintext=not config.encryption_strict,
    )
    sensitive_keys = _resolve_sensitive_keys_for_values(context, values)
    logger.debug(
        "Vault show result ready",
        extra={
            "active_profile": resolved_profile,
            "state": state,
            "exists": exists,
            "key_count": len(values),
        },
    )

    return (
        context,
        resolved_profile,
        VaultShowResult(
            path=profile_path,
            exists=exists,
            values=values,
            sensitive_keys=sensitive_keys,
            state=state,
            detail=detail,
        ),
    )
