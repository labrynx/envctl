"""Explain service."""

from __future__ import annotations

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import InspectKeyResult
from envctl.domain.project import ProjectContext
from envctl.services.inspect_service import run_inspect_key


def run_explain(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, InspectKeyResult, tuple[ContractDeprecationWarning, ...]]:
    """Deprecated compatibility wrapper for ``inspect KEY``."""
    return run_inspect_key(key, active_profile)
