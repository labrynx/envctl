"""Managed Git hook domain models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class HookName(StrEnum):
    """Supported managed Git hook names."""

    PRE_COMMIT = "pre-commit"
    PRE_PUSH = "pre-push"


class HookStatus(StrEnum):
    """Inspection status for one supported hook."""

    HEALTHY = "healthy"
    MISSING = "missing"
    DRIFTED = "drifted"
    FOREIGN = "foreign"
    NOT_EXECUTABLE = "not_executable"
    UNSUPPORTED = "unsupported"


class HookAction(StrEnum):
    """Stable action names for hook operations."""

    NOOP = "noop"
    CREATED = "created"
    REWRITTEN = "rewritten"
    FIXED_PERMISSIONS = "fixed_permissions"
    REMOVED = "removed"
    SKIPPED_FOREIGN = "skipped_foreign"
    SKIPPED_UNSUPPORTED = "skipped_unsupported"
    WARNING_LEGACY_CLEANUP = "warning_legacy_cleanup"
    ERROR = "error"


class HooksStatusLevel(StrEnum):
    """Stable aggregate hook health levels."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CONFLICT = "conflict"


class HooksReason(StrEnum):
    """Stable init-time managed hook outcome reasons."""

    INSTALLED = "installed"
    ALREADY_HEALTHY = "already_healthy"
    PARTIAL_CONFLICT = "partial_conflict"
    UNSUPPORTED_HOOKS_PATH = "unsupported_hooks_path"
    FOREIGN_HOOK_PRESENT = "foreign_hook_present"
    INSTALL_FAILED = "install_failed"


@dataclass(frozen=True)
class ManagedHookSpec:
    """Canonical specification for one envctl-managed hook."""

    name: HookName
    version: int
    command: tuple[str, ...]


@dataclass(frozen=True)
class HookInspectionResult:
    """Inspection result for one supported hook."""

    name: HookName
    path: Path
    status: HookStatus
    managed: bool
    is_executable: bool | None
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class HooksStatusReport:
    """Aggregate inspection report for managed hooks."""

    hooks_path: Path
    overall_status: HooksStatusLevel
    results: tuple[HookInspectionResult, ...]
    details: tuple[str, ...] = ()

    @property
    def is_healthy(self) -> bool:
        """Return whether the managed hook set is healthy."""
        return self.overall_status == HooksStatusLevel.HEALTHY


@dataclass(frozen=True)
class HookOperationResult:
    """Operation result for one supported hook."""

    name: HookName
    path: Path
    before_status: HookStatus
    after_status: HookStatus
    action: HookAction
    changed: bool
    managed: bool
    details: tuple[str, ...] = ()


@dataclass(frozen=True)
class HookOperationReport:
    """Aggregate report for one managed hooks operation."""

    hooks_path: Path
    final_status: HooksStatusLevel
    changed: bool
    results: tuple[HookOperationResult, ...]
    details: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        """Return whether the operation finished with a healthy final state."""
        return self.final_status == HooksStatusLevel.HEALTHY
