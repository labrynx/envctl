"""Export service."""

from __future__ import annotations

from typing import Literal

from envctl.adapters.projection_rendering import render_dotenv, render_shell_exports
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.project import ProjectContext
from envctl.domain.selection import ContractSelection
from envctl.observability.fields import selection_scope
from envctl.observability.timing import observe_span
from envctl.services.context_service import load_project_context
from envctl.services.projection_validation import resolve_projectable_environment
from envctl.services.selection_filtering import (
    build_variable_groups,
    filter_projection_values,
)
from envctl.utils.project_paths import normalize_profile_name


def run_export(
    active_profile: str | None = None,
    *,
    format: Literal["shell", "dotenv"] = "shell",
    selection: ContractSelection | None = None,
) -> tuple[
    ProjectContext,
    str,
    dict[str, str],
    str,
    tuple[ContractDeprecationWarning, ...],
]:
    """Render the resolved environment as shell export lines."""
    with observe_span(
        "projection.render",
        module=__name__,
        operation="run_export",
        fields={"selection_scope": selection_scope(selection)},
    ) as span_fields:
        _config, context = load_project_context()
        resolved_profile = normalize_profile_name(active_profile)

        contract, report, warnings = resolve_projectable_environment(
            context,
            active_profile=resolved_profile,
            selection=selection,
            operation="export",
        )

        values = filter_projection_values(
            {key: item.value for key, item in sorted(report.values.items())},
            contract,
            selection=selection,
        )

        if format == "dotenv":
            rendered = render_dotenv(
                values,
                include_header=False,
                variable_groups=build_variable_groups(contract, values),
            )
        else:
            rendered = render_shell_exports(values)
        span_fields["selected_profile"] = resolved_profile
        span_fields["resolved_key_count"] = len(values)
        span_fields["warning_count"] = len(warnings)
        return context, resolved_profile, values, rendered, warnings
