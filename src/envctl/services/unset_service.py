"""Unset service."""

from __future__ import annotations

from pathlib import Path

from envctl.domain.project import ProjectContext
from envctl.observability.timing import observe_span
from envctl.repository.profile_repository import load_profile_values, write_profile_values
from envctl.services.context_service import load_project_context
from envctl.utils.project_paths import normalize_profile_name


def run_unset(
    key: str,
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, Path, bool]:
    """Remove one key from the active profile."""
    with observe_span(
        "variables.mutate",
        module=__name__,
        operation="run_unset",
        fields={"updated": True},
    ) as span_fields:
        _config, context = load_project_context()
        resolved_profile = normalize_profile_name(active_profile)

        _resolved_profile, _profile_path, values = load_profile_values(
            context,
            resolved_profile,
            require_existing_explicit=True,
        )
        removed = key in values
        values.pop(key, None)

        _resolved_profile, profile_path = write_profile_values(
            context,
            resolved_profile,
            values,
            require_existing_explicit=True,
        )
        span_fields["selected_profile"] = resolved_profile
        span_fields["removed"] = removed
        return context, resolved_profile, profile_path, removed
