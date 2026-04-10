"""Project-wide crypto and audit implementations for vault services."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from envctl.domain.app_config import AppConfig
from envctl.domain.operations import (
    VaultAuditProjectResult,
    VaultDecryptResult,
    VaultEncryptResult,
)
from envctl.domain.project import ProjectContext


def run_vault_encrypt_project_impl(
    *,
    include_all_projects: bool,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    iter_project_dirs: Callable[[Path], tuple[Path, ...]],
    build_project_audit_context: Callable[[AppConfig, Path], ProjectContext],
    run_encrypt_for_context: Callable[[ProjectContext], VaultEncryptResult],
) -> tuple[ProjectContext, VaultEncryptResult]:
    """Encrypt plaintext vault profile files for the current project or all projects."""
    config, context = load_project_context()

    if include_all_projects:
        encrypted: list[Path] = []
        skipped: list[Path] = []

        for project_dir in iter_project_dirs(config.projects_dir):
            audit_context = build_project_audit_context(config, project_dir)
            result = run_encrypt_for_context(audit_context)
            encrypted.extend(result.encrypted_files)
            skipped.extend(result.skipped_files)

        return context, VaultEncryptResult(
            encrypted_files=tuple(encrypted),
            skipped_files=tuple(skipped),
        )

    result = run_encrypt_for_context(context)
    return context, result


def run_vault_decrypt_project_impl(
    *,
    include_all_projects: bool,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    iter_project_dirs: Callable[[Path], tuple[Path, ...]],
    build_project_audit_context: Callable[[AppConfig, Path], ProjectContext],
    run_decrypt_for_context: Callable[[ProjectContext], VaultDecryptResult],
) -> tuple[ProjectContext, VaultDecryptResult]:
    """Decrypt encrypted vault profile files for the current project or all projects."""
    config, context = load_project_context()

    if include_all_projects:
        decrypted: list[Path] = []
        skipped: list[Path] = []

        for project_dir in iter_project_dirs(config.projects_dir):
            audit_context = build_project_audit_context(config, project_dir)
            result = run_decrypt_for_context(audit_context)
            decrypted.extend(result.decrypted_files)
            skipped.extend(result.skipped_files)

        return context, VaultDecryptResult(
            decrypted_files=tuple(decrypted),
            skipped_files=tuple(skipped),
        )

    result = run_decrypt_for_context(context)
    return context, result


def run_vault_audit_impl(
    *,
    load_project_context: Callable[..., tuple[AppConfig, ProjectContext]],
    iter_project_dirs: Callable[[Path], tuple[Path, ...]],
    audit_project: Callable[[AppConfig, Path], VaultAuditProjectResult],
) -> tuple[ProjectContext, tuple[VaultAuditProjectResult, ...]]:
    """Audit all project vaults and report plaintext or inconsistent files."""
    config, context = load_project_context()
    projects = tuple(
        audit_project(config, project_dir) for project_dir in iter_project_dirs(config.projects_dir)
    )
    return context, projects
