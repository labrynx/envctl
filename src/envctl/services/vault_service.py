"""Stable facade for vault-oriented services."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import envctl.adapters.editor as editor_adapter
from envctl.domain.operations import (
    VaultAuditProjectResult,
    VaultCheckResult,
    VaultDecryptResult,
    VaultEditResult,
    VaultEncryptResult,
    VaultPruneResult,
    VaultShowResult,
)
from envctl.domain.project import ProjectContext
from envctl.observability import get_active_observability_context
from envctl.observability.events import VAULT_ERROR, VAULT_FINISH, VAULT_START
from envctl.observability.recorder import duration_ms, record_event
from envctl.observability.timing import utcnow
from envctl.repository.contract_repository import load_contract_optional
from envctl.repository.profile_repository import load_profile_values, write_profile_values
from envctl.services.context_service import load_project_context
from envctl.services.vault_mutations import (
    get_unknown_vault_keys_impl,
    run_vault_edit_impl,
    run_vault_prune_impl,
)
from envctl.services.vault_project_crypto import (
    run_vault_audit_impl,
    run_vault_decrypt_project_impl,
    run_vault_encrypt_project_impl,
)
from envctl.services.vault_queries import (
    run_vault_check_impl,
    run_vault_path_impl,
    run_vault_show_impl,
)
from envctl.services.vault_support import (
    audit_project,
    build_project_audit_context,
    classify_vault_file,
    iter_project_dirs,
    require_no_plaintext_in_strict_mode,
    resolve_selected_profile,
    run_decrypt_for_context,
    run_encrypt_for_context,
)
from envctl.utils.filesystem import is_world_writable
from envctl.utils.logging import get_logger

logger = get_logger(__name__)


def _record_vault_start(operation: str, *, include_all_projects: bool | None = None) -> None:
    obs_context = get_active_observability_context()
    if obs_context is None:
        return
    fields: dict[str, object] = {}
    if include_all_projects is not None:
        fields["include_all_projects"] = include_all_projects
    record_event(
        obs_context,
        event=VAULT_START,
        status="start",
        module=__name__,
        operation=operation,
        fields=fields,
    )


def _record_vault_finish(
    operation: str,
    started_at: datetime,
    *,
    fields: dict[str, object] | None = None,
) -> None:
    obs_context = get_active_observability_context()
    if obs_context is None:
        return
    record_event(
        obs_context,
        event=VAULT_FINISH,
        status="finish",
        duration_ms=duration_ms(started_at),
        module=__name__,
        operation=operation,
        fields=fields or {},
    )


def _record_vault_error(
    operation: str,
    started_at: datetime,
    *,
    fields: dict[str, object] | None = None,
) -> None:
    obs_context = get_active_observability_context()
    if obs_context is None:
        return
    record_event(
        obs_context,
        event=VAULT_ERROR,
        status="error",
        duration_ms=duration_ms(started_at),
        module=__name__,
        operation=operation,
        fields=fields or {},
    )


def run_vault_check(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, VaultCheckResult]:
    """Check the current physical vault file for the active profile."""
    started_at = utcnow()
    _record_vault_start("run_vault_check")
    try:
        result = run_vault_check_impl(
            active_profile=active_profile,
            load_project_context=load_project_context,
            require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
            resolve_selected_profile=resolve_selected_profile,
            classify_vault_file=classify_vault_file,
            is_world_writable=is_world_writable,
            logger=logger,
        )
    except Exception:
        _record_vault_error("run_vault_check", started_at)
        raise
    _context, _profile, check_result = result
    _record_vault_finish(
        "run_vault_check",
        started_at,
        fields={
            "exists": check_result.exists,
            "parseable": check_result.parseable,
            "key_count": check_result.key_count,
        },
    )
    return result


def run_vault_path(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path]:
    """Return the current physical vault path for the active profile."""
    started_at = utcnow()
    _record_vault_start("run_vault_path")
    try:
        result = run_vault_path_impl(
            active_profile=active_profile,
            load_project_context=load_project_context,
            resolve_selected_profile=resolve_selected_profile,
            logger=logger,
        )
    except Exception:
        _record_vault_error("run_vault_path", started_at)
        raise
    _record_vault_finish("run_vault_path", started_at, fields={})
    return result


def run_vault_show(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, VaultShowResult]:
    """Return the current physical vault content for the active profile."""
    started_at = utcnow()
    _record_vault_start("run_vault_show")
    try:
        result = run_vault_show_impl(
            active_profile=active_profile,
            load_project_context=load_project_context,
            require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
            resolve_selected_profile=resolve_selected_profile,
            classify_vault_file=classify_vault_file,
            logger=logger,
        )
    except Exception:
        _record_vault_error("run_vault_show", started_at)
        raise
    _context, _profile, show_result = result
    _record_vault_finish(
        "run_vault_show",
        started_at,
        fields={"exists": show_result.exists, "key_count": len(show_result.values)},
    )
    return result


def run_vault_edit(
    active_profile: str | None = None,
) -> tuple[ProjectContext, VaultEditResult]:
    """Open the current physical vault file for the selected profile."""
    started_at = utcnow()
    _record_vault_start("run_vault_edit")
    try:
        result = run_vault_edit_impl(
            active_profile=active_profile,
            load_project_context=load_project_context,
            require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
            resolve_selected_profile=resolve_selected_profile,
            write_profile_values=write_profile_values,
            load_profile_values=load_profile_values,
            editor_open_file=editor_adapter.open_file,
            logger=logger,
        )
    except Exception:
        _record_vault_error("run_vault_edit", started_at)
        raise
    _context, edit_result = result
    _record_vault_finish("run_vault_edit", started_at, fields={"created": edit_result.created})
    return result


def get_unknown_vault_keys(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, tuple[str, ...]]:
    """Return unknown keys stored in the active profile vault."""
    started_at = utcnow()
    _record_vault_start("get_unknown_vault_keys")
    try:
        result = get_unknown_vault_keys_impl(
            active_profile=active_profile,
            load_project_context=load_project_context,
            require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
            resolve_selected_profile=resolve_selected_profile,
            load_contract_optional=load_contract_optional,
            load_profile_values=load_profile_values,
            logger=logger,
        )
    except Exception:
        _record_vault_error("get_unknown_vault_keys", started_at)
        raise
    _context, _profile, _path, unknown_keys = result
    _record_vault_finish(
        "get_unknown_vault_keys",
        started_at,
        fields={"unknown_key_count": len(unknown_keys)},
    )
    return result


def run_vault_prune(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, VaultPruneResult]:
    """Remove unknown keys from the active profile vault."""
    started_at = utcnow()
    _record_vault_start("run_vault_prune")
    try:
        result = run_vault_prune_impl(
            active_profile=active_profile,
            load_project_context=load_project_context,
            require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
            resolve_selected_profile=resolve_selected_profile,
            load_contract_optional=load_contract_optional,
            load_profile_values=load_profile_values,
            write_profile_values=write_profile_values,
            logger=logger,
        )
    except Exception:
        _record_vault_error("run_vault_prune", started_at)
        raise
    _context, _profile, _path, prune_result = result
    _record_vault_finish(
        "run_vault_prune",
        started_at,
        fields={
            "removed_key_count": len(prune_result.removed_keys),
            "kept_keys": prune_result.kept_keys,
        },
    )
    return result


def run_vault_encrypt_project(
    *,
    include_all_projects: bool = False,
) -> tuple[ProjectContext, VaultEncryptResult]:
    """Encrypt plaintext vault profile files for the current project or all projects."""
    started_at = utcnow()
    _record_vault_start("run_vault_encrypt_project", include_all_projects=include_all_projects)
    try:
        result = run_vault_encrypt_project_impl(
            include_all_projects=include_all_projects,
            load_project_context=load_project_context,
            iter_project_dirs=iter_project_dirs,
            build_project_audit_context=build_project_audit_context,
            run_encrypt_for_context=run_encrypt_for_context,
            logger=logger,
        )
    except Exception:
        _record_vault_error(
            "run_vault_encrypt_project",
            started_at,
            fields={"include_all_projects": include_all_projects},
        )
        raise
    _context, encrypt_result = result
    _record_vault_finish(
        "run_vault_encrypt_project",
        started_at,
        fields={
            "include_all_projects": include_all_projects,
            "encrypted_file_count": len(encrypt_result.encrypted_files),
            "skipped_file_count": len(encrypt_result.skipped_files),
        },
    )
    return result


def run_vault_decrypt_project(
    *,
    include_all_projects: bool = False,
) -> tuple[ProjectContext, VaultDecryptResult]:
    """Decrypt encrypted vault profile files for the current project or all projects."""
    started_at = utcnow()
    _record_vault_start("run_vault_decrypt_project", include_all_projects=include_all_projects)
    try:
        result = run_vault_decrypt_project_impl(
            include_all_projects=include_all_projects,
            load_project_context=load_project_context,
            iter_project_dirs=iter_project_dirs,
            build_project_audit_context=build_project_audit_context,
            run_decrypt_for_context=run_decrypt_for_context,
            logger=logger,
        )
    except Exception:
        _record_vault_error(
            "run_vault_decrypt_project",
            started_at,
            fields={"include_all_projects": include_all_projects},
        )
        raise
    _context, decrypt_result = result
    _record_vault_finish(
        "run_vault_decrypt_project",
        started_at,
        fields={
            "include_all_projects": include_all_projects,
            "decrypted_file_count": len(decrypt_result.decrypted_files),
            "skipped_file_count": len(decrypt_result.skipped_files),
        },
    )
    return result


def run_vault_audit() -> tuple[ProjectContext, tuple[VaultAuditProjectResult, ...]]:
    """Audit all project vaults and report plaintext or inconsistent files."""
    started_at = utcnow()
    _record_vault_start("run_vault_audit")
    try:
        result = run_vault_audit_impl(
            load_project_context=load_project_context,
            iter_project_dirs=iter_project_dirs,
            audit_project=audit_project,
            logger=logger,
        )
    except Exception:
        _record_vault_error("run_vault_audit", started_at)
        raise
    _context, audit_results = result
    _record_vault_finish(
        "run_vault_audit",
        started_at,
        fields={"project_count": len(audit_results)},
    )
    return result
