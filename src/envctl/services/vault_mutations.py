"""Mutation-oriented vault service implementations."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from contextlib import suppress
from logging import Logger
from pathlib import Path
from typing import Any

from envctl.domain.app_config import AppConfig
from envctl.domain.operations import VaultEditResult, VaultPruneResult
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.observability import get_active_observability_context
from envctl.observability.error_mapping import map_exception_to_error_event
from envctl.observability.events import VAULT_ERROR, VAULT_FINISH, VAULT_START
from envctl.observability.recorder import duration_ms, record_event
from envctl.observability.timing import utcnow


def _run_vault_edit_encrypted(
    profile_path: Path,
    *,
    context: ProjectContext,
    editor_open_file: Callable[[str], None],
) -> None:
    """Open a vault file through a decrypted temporary file and re-encrypt it."""
    crypto = context.vault_crypto
    if crypto is None:  # pragma: no cover
        raise ExecutionError("Vault edit requested encrypted mode without an active key.")

    content = crypto.read_file(profile_path, allow_plaintext=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=".edit-",
        suffix=".tmp",
        dir=str(profile_path.parent),
    )
    tmp_path = Path(tmp_name)

    try:
        with suppress(AttributeError):
            os.fchmod(fd, 0o600)

        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)

        editor_open_file(str(tmp_path))

        edited_content = tmp_path.read_text(encoding="utf-8")
        crypto.write_encrypted_file(profile_path, edited_content)
    finally:
        with suppress(OSError):
            tmp_path.unlink(missing_ok=True)


def get_unknown_vault_keys_impl(
    *,
    active_profile: str | None,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    require_no_plaintext_in_strict_mode: Callable[..., None],
    resolve_selected_profile: Callable[[ProjectContext, str | None], tuple[str, Path]],
    load_contract_optional: Callable[[Path], Any],
    load_profile_values: Callable[..., tuple[str, Path, dict[str, str]]],
    logger: Logger,
) -> tuple[ProjectContext, str, Path, tuple[str, ...]]:
    """Return unknown keys stored in the active profile vault."""
    started_at = utcnow()
    obs_context = get_active_observability_context()
    if obs_context is not None:
        record_event(
            obs_context,
            event=VAULT_START,
            status="start",
            module=__name__,
            operation="get_unknown_vault_keys_impl",
            fields={},
        )
    try:
        config, context = load_project_context()
    except Exception as exc:
        if obs_context is not None:
            mapping = map_exception_to_error_event(exc)
            record_event(
                obs_context,
                event=VAULT_ERROR,
                status="error",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="get_unknown_vault_keys_impl",
                fields={
                    "message_safe": mapping.message_safe,
                    "phase": "vault_unknown_keys",
                    "recoverable": mapping.recoverable,
                },
            )
            record_event(
                obs_context,
                event=mapping.event,
                status="error",
                module=__name__,
                operation="get_unknown_vault_keys_impl",
                fields={
                    "message_safe": mapping.message_safe,
                    "phase": "vault_unknown_keys",
                    "recoverable": mapping.recoverable,
                },
            )
        raise
    require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = resolve_selected_profile(context, active_profile)
    logger.debug(
        "Collecting unknown vault keys",
        extra={"active_profile": resolved_profile, "path": profile_path},
    )

    contract = load_contract_optional(context.repo_contract_path)
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
        allow_plaintext=not config.encryption_strict,
    )

    if contract is None:
        logger.debug(
            "All vault keys are unknown because contract is missing",
            extra={"active_profile": resolved_profile, "unknown_key_count": len(values)},
        )
        result = context, resolved_profile, profile_path, tuple(sorted(values))
        if obs_context is not None:
            record_event(
                obs_context,
                event=VAULT_FINISH,
                status="finish",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="get_unknown_vault_keys_impl",
                fields={"unknown_key_count": len(values)},
            )
        return result

    unknown_keys = tuple(sorted(set(values) - set(contract.variables)))
    logger.debug(
        "Collected unknown vault keys",
        extra={"active_profile": resolved_profile, "unknown_key_count": len(unknown_keys)},
    )
    result = context, resolved_profile, profile_path, unknown_keys
    if obs_context is not None:
        record_event(
            obs_context,
            event=VAULT_FINISH,
            status="finish",
            duration_ms=duration_ms(started_at),
            module=__name__,
            operation="get_unknown_vault_keys_impl",
            fields={"unknown_key_count": len(unknown_keys)},
        )
    return result


def run_vault_edit_impl(
    *,
    active_profile: str | None,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    require_no_plaintext_in_strict_mode: Callable[..., None],
    resolve_selected_profile: Callable[[ProjectContext, str | None], tuple[str, Path]],
    write_profile_values: Callable[..., Any],
    load_profile_values: Callable[..., tuple[str, Path, dict[str, str]]],
    editor_open_file: Callable[[str], None],
    logger: Logger,
) -> tuple[ProjectContext, VaultEditResult]:
    """Open the current physical vault file for the selected profile."""
    started_at = utcnow()
    obs_context = get_active_observability_context()
    if obs_context is not None:
        record_event(
            obs_context,
            event=VAULT_START,
            status="start",
            module=__name__,
            operation="run_vault_edit_impl",
            fields={},
        )
    try:
        config, context = load_project_context()
    except Exception as exc:
        if obs_context is not None:
            mapping = map_exception_to_error_event(exc)
            record_event(
                obs_context,
                event=VAULT_ERROR,
                status="error",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="run_vault_edit_impl",
                fields={
                    "message_safe": mapping.message_safe,
                    "phase": "vault_edit",
                    "recoverable": mapping.recoverable,
                },
            )
            record_event(
                obs_context,
                event=mapping.event,
                status="error",
                module=__name__,
                operation="run_vault_edit_impl",
                fields={
                    "message_safe": mapping.message_safe,
                    "phase": "vault_edit",
                    "recoverable": mapping.recoverable,
                },
            )
        raise
    require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = resolve_selected_profile(context, active_profile)
    logger.debug(
        "Running vault edit",
        extra={
            "active_profile": resolved_profile,
            "path": profile_path,
            "strict": config.encryption_strict,
        },
    )

    created = False
    if not profile_path.exists():
        write_profile_values(context, resolved_profile, {})
        created = True
        logger.debug(
            "Created missing vault file before edit",
            extra={"active_profile": resolved_profile, "path": profile_path},
        )

    if context.vault_crypto is not None:
        _run_vault_edit_encrypted(
            profile_path,
            context=context,
            editor_open_file=editor_open_file,
        )
    else:
        editor_open_file(str(profile_path))

    try:
        load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
            allow_plaintext=not config.encryption_strict,
        )
    except Exception as exc:  # pragma: no cover
        raise ExecutionError(f"Edited vault file is no longer parseable: {profile_path}") from exc
    logger.info(
        "Vault edit completed",
        extra={
            "active_profile": resolved_profile,
            "path": profile_path,
            "vault_created": created,
        },
    )

    result = (
        context,
        VaultEditResult(
            path=profile_path,
            profile=resolved_profile,
            created=created,
        ),
    )
    if obs_context is not None:
        record_event(
            obs_context,
            event=VAULT_FINISH,
            status="finish",
            duration_ms=duration_ms(started_at),
            module=__name__,
            operation="run_vault_edit_impl",
            fields={"created": created},
        )
    return result


def run_vault_prune_impl(
    *,
    active_profile: str | None,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    require_no_plaintext_in_strict_mode: Callable[..., None],
    resolve_selected_profile: Callable[[ProjectContext, str | None], tuple[str, Path]],
    load_contract_optional: Callable[[Path], Any],
    load_profile_values: Callable[..., tuple[str, Path, dict[str, str]]],
    write_profile_values: Callable[..., Any],
    logger: Logger,
) -> tuple[ProjectContext, str, Path, VaultPruneResult]:
    """Remove unknown keys from the active profile vault."""
    started_at = utcnow()
    obs_context = get_active_observability_context()
    if obs_context is not None:
        record_event(
            obs_context,
            event=VAULT_START,
            status="start",
            module=__name__,
            operation="run_vault_prune_impl",
            fields={},
        )
    try:
        config, context = load_project_context()
    except Exception as exc:
        if obs_context is not None:
            mapping = map_exception_to_error_event(exc)
            record_event(
                obs_context,
                event=VAULT_ERROR,
                status="error",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="run_vault_prune_impl",
                fields={
                    "message_safe": mapping.message_safe,
                    "phase": "vault_prune",
                    "recoverable": mapping.recoverable,
                },
            )
            record_event(
                obs_context,
                event=mapping.event,
                status="error",
                module=__name__,
                operation="run_vault_prune_impl",
                fields={
                    "message_safe": mapping.message_safe,
                    "phase": "vault_prune",
                    "recoverable": mapping.recoverable,
                },
            )
        raise
    require_no_plaintext_in_strict_mode(context, strict=config.encryption_strict)
    resolved_profile, profile_path = resolve_selected_profile(context, active_profile)
    logger.debug(
        "Running vault prune",
        extra={
            "active_profile": resolved_profile,
            "path": profile_path,
            "strict": config.encryption_strict,
        },
    )

    contract = load_contract_optional(context.repo_contract_path)
    _resolved_profile, _path, values = load_profile_values(
        context,
        resolved_profile,
        require_existing_explicit=True,
        allow_plaintext=not config.encryption_strict,
    )

    if contract is None:
        removed_keys = tuple(sorted(values))
        kept: dict[str, str] = {}
    else:
        removed_keys = tuple(sorted(set(values) - set(contract.variables)))
        kept = {key: value for key, value in values.items() if key in contract.variables}

    write_profile_values(
        context,
        resolved_profile,
        kept,
        require_existing_explicit=True,
    )
    logger.debug(
        "Vault prune result ready",
        extra={
            "active_profile": resolved_profile,
            "removed_key_count": len(removed_keys),
            "kept_key_count": len(kept),
            "path": profile_path,
        },
    )
    logger.info(
        "Vault prune completed",
        extra={
            "active_profile": resolved_profile,
            "removed_key_count": len(removed_keys),
            "path": profile_path,
        },
    )

    result = (
        context,
        resolved_profile,
        profile_path,
        VaultPruneResult(
            path=profile_path,
            removed_keys=removed_keys,
            kept_keys=len(kept),
        ),
    )
    if obs_context is not None:
        record_event(
            obs_context,
            event=VAULT_FINISH,
            status="finish",
            duration_ms=duration_ms(started_at),
            module=__name__,
            operation="run_vault_prune_impl",
            fields={"removed_key_count": len(removed_keys), "kept_key_count": len(kept)},
        )
    return result
