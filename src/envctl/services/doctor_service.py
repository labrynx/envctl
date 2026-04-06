"""Doctor service."""

from __future__ import annotations

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.diagnostics import InspectResult
from envctl.domain.project import ProjectContext
from envctl.services.inspect_service import run_inspect


def run_doctor(
    active_profile: str | None = None,
) -> tuple[ProjectContext, InspectResult, tuple[ContractDeprecationWarning, ...]]:
    """Deprecated compatibility wrapper for ``inspect``."""
    return run_inspect(active_profile)
