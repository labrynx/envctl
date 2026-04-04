"""Export service."""

from __future__ import annotations

from typing import Literal

from envctl.domain.project import ProjectContext
from envctl.services.context_service import load_project_context
from envctl.services.group_selection_service import (
    build_variable_groups,
    filter_projection_values,
)
from envctl.services.projection_validation import resolve_projectable_environment
from envctl.utils.project_paths import normalize_profile_name
from envctl.utils.projection_rendering import render_dotenv, render_shell_exports


def run_export(
    active_profile: str | None = None,
    *,
    format: Literal["shell", "dotenv"] = "shell",
    group: str | None = None,
) -> tuple[ProjectContext, str, str]:
    """Render the resolved environment as shell export lines."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)

    contract, report = resolve_projectable_environment(
        context,
        active_profile=resolved_profile,
        group=group,
        operation="export",
    )

    values = filter_projection_values(
        {key: item.value for key, item in sorted(report.values.items())},
        contract,
        group=group,
    )

    if format == "dotenv":
        rendered = render_dotenv(
            values,
            include_header=False,
            variable_groups=build_variable_groups(contract, values),
        )
    else:
        rendered = render_shell_exports(values)
    return context, resolved_profile, rendered
