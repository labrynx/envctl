from __future__ import annotations

from envctl.domain.resolution import ResolutionReport
from envctl.domain.selection import ContractSelection
from envctl.errors import ValidationError
from envctl.services.error_diagnostics import ProjectionOperation, ProjectionValidationDiagnostics


def raise_projection_error(
    *,
    operation: ProjectionOperation,
    profile: str,
    selection: ContractSelection | None,
    report: ResolutionReport,
    suggested_actions: tuple[str, ...],
) -> tuple[object, object]:
    raise ValidationError(
        f"Cannot {operation} because the environment contract is not satisfied.",
        diagnostics=ProjectionValidationDiagnostics(
            operation=operation,
            active_profile=profile,
            selection=selection or ContractSelection(),
            report=report,
            suggested_actions=suggested_actions,
        ),
    )
