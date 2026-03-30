"""Run service."""

from __future__ import annotations

import os
import subprocess

from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError, ValidationError
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import (
    load_contract_for_context,
    resolve_environment,
)
from envctl.utils.project_paths import normalize_profile_name


def _build_child_env(resolved_values: dict[str, str]) -> dict[str, str]:
    """Build the child process environment."""
    child_env = dict(os.environ)
    child_env.update(resolved_values)
    return child_env


def run_command(
    command: list[str],
    active_profile: str | None = None,
) -> tuple[ProjectContext, str, int]:
    """Run one command with the resolved environment injected."""
    if not command:
        raise ExecutionError("No command provided")

    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)

    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract, active_profile=resolved_profile)

    if not report.is_valid:
        raise ValidationError("Environment contract is not satisfied")

    if report.unknown_keys:
        raise ValidationError("Vault contains unknown keys")

    resolved_values = {key: item.value for key, item in report.values.items()}

    try:
        completed = subprocess.run(
            command,
            check=False,
            env=_build_child_env(resolved_values),
        )
    except OSError as exc:
        raise ExecutionError(f"Failed to launch child process: {command[0]}") from exc

    return context, resolved_profile, completed.returncode
