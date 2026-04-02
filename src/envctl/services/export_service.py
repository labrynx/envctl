"""Export service."""

from __future__ import annotations

from typing import Literal

from envctl.domain.project import ProjectContext
from envctl.errors import ValidationError
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import (
    load_contract_for_context,
    resolve_environment,
)
from envctl.utils.project_paths import normalize_profile_name
from envctl.utils.projection_rendering import render_dotenv, render_shell_exports


def run_export(
    active_profile: str | None = None,
    *,
    format: Literal["shell", "dotenv"] = "shell",
) -> tuple[ProjectContext, str, str]:
    """Render the resolved environment as shell export lines."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)

    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract, active_profile=resolved_profile)

    if not report.is_valid:
        raise ValidationError("Environment contract is not satisfied")

    if report.unknown_keys:
        raise ValidationError("Vault contains unknown keys")

    values = {key: item.value for key, item in sorted(report.values.items())}

    if format == "dotenv":
        rendered = render_dotenv(values, include_header=False)
    else:
        rendered = render_shell_exports(values)
    return context, resolved_profile, rendered
