"""Vault domain helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envctl.domain.operations import VaultAuditProjectResult


@dataclass(frozen=True)
class VaultAuditSummary:
    """Aggregate summary for vault audit results."""

    total_projects: int
    healthy_projects: int
    projects_with_issues: int
    missing_keys: int
    plaintext_files: int
    insecure_files: int
    missing_files: int

    @property
    def ok(self) -> bool:
        """Return whether the audit found no blocking issues."""
        return self.projects_with_issues == 0


def summarize_vault_audit(
    projects: tuple[VaultAuditProjectResult, ...],
) -> VaultAuditSummary:
    """Summarize vault audit results."""
    missing_keys = 0
    plaintext_files = 0
    insecure_files = 0
    missing_files = 0
    healthy_projects = 0
    projects_with_issues = 0

    for project in projects:
        project_has_issues = False

        if not project.key_exists:
            missing_keys += 1
            project_has_issues = True

        if not project.files:
            missing_files += 1
            project_has_issues = True

        for file_item in project.files:
            if file_item.state != "encrypted":
                plaintext_files += 1
                project_has_issues = True
            if not file_item.private_permissions:
                insecure_files += 1
                project_has_issues = True

        if project_has_issues:
            projects_with_issues += 1
        else:
            healthy_projects += 1

    return VaultAuditSummary(
        total_projects=len(projects),
        healthy_projects=healthy_projects,
        projects_with_issues=projects_with_issues,
        missing_keys=missing_keys,
        plaintext_files=plaintext_files,
        insecure_files=insecure_files,
        missing_files=missing_files,
    )
