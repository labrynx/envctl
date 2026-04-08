"""Stable facade for vault-oriented services."""

from __future__ import annotations

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


def run_vault_check(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, VaultCheckResult]:
    """Check the current physical vault file for the active profile."""
    return run_vault_check_impl(
        active_profile=active_profile,
        load_project_context=load_project_context,
        require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
        resolve_selected_profile=resolve_selected_profile,
        classify_vault_file=classify_vault_file,
        is_world_writable=is_world_writable,
        logger=logger,
    )


def run_vault_path(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path]:
    """Return the current physical vault path for the active profile."""
    return run_vault_path_impl(
        active_profile=active_profile,
        load_project_context=load_project_context,
        resolve_selected_profile=resolve_selected_profile,
        logger=logger,
    )


def run_vault_show(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, VaultShowResult]:
    """Return the current physical vault content for the active profile."""
    return run_vault_show_impl(
        active_profile=active_profile,
        load_project_context=load_project_context,
        require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
        resolve_selected_profile=resolve_selected_profile,
        classify_vault_file=classify_vault_file,
        logger=logger,
    )


def run_vault_edit(
    active_profile: str | None = None,
) -> tuple[ProjectContext, VaultEditResult]:
    """Open the current physical vault file for the selected profile."""
    return run_vault_edit_impl(
        active_profile=active_profile,
        load_project_context=load_project_context,
        require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
        resolve_selected_profile=resolve_selected_profile,
        write_profile_values=write_profile_values,
        load_profile_values=load_profile_values,
        editor_open_file=editor_adapter.open_file,
        logger=logger,
    )


def get_unknown_vault_keys(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, tuple[str, ...]]:
    """Return unknown keys stored in the active profile vault."""
    return get_unknown_vault_keys_impl(
        active_profile=active_profile,
        load_project_context=load_project_context,
        require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
        resolve_selected_profile=resolve_selected_profile,
        load_contract_optional=load_contract_optional,
        load_profile_values=load_profile_values,
        logger=logger,
    )


def run_vault_prune(
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, VaultPruneResult]:
    """Remove unknown keys from the active profile vault."""
    return run_vault_prune_impl(
        active_profile=active_profile,
        load_project_context=load_project_context,
        require_no_plaintext_in_strict_mode=require_no_plaintext_in_strict_mode,
        resolve_selected_profile=resolve_selected_profile,
        load_contract_optional=load_contract_optional,
        load_profile_values=load_profile_values,
        write_profile_values=write_profile_values,
        logger=logger,
    )


def run_vault_encrypt_project(
    *,
    include_all_projects: bool = False,
) -> tuple[ProjectContext, VaultEncryptResult]:
    """Encrypt plaintext vault profile files for the current project or all projects."""
    return run_vault_encrypt_project_impl(
        include_all_projects=include_all_projects,
        load_project_context=load_project_context,
        iter_project_dirs=iter_project_dirs,
        build_project_audit_context=build_project_audit_context,
        run_encrypt_for_context=run_encrypt_for_context,
        logger=logger,
    )


def run_vault_decrypt_project(
    *,
    include_all_projects: bool = False,
) -> tuple[ProjectContext, VaultDecryptResult]:
    """Decrypt encrypted vault profile files for the current project or all projects."""
    return run_vault_decrypt_project_impl(
        include_all_projects=include_all_projects,
        load_project_context=load_project_context,
        iter_project_dirs=iter_project_dirs,
        build_project_audit_context=build_project_audit_context,
        run_decrypt_for_context=run_decrypt_for_context,
        logger=logger,
    )


def run_vault_audit() -> tuple[ProjectContext, tuple[VaultAuditProjectResult, ...]]:
    """Audit all project vaults and report plaintext or inconsistent files."""
    return run_vault_audit_impl(
        load_project_context=load_project_context,
        iter_project_dirs=iter_project_dirs,
        audit_project=audit_project,
        logger=logger,
    )
