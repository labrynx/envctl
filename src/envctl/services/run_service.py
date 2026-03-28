"""Run service."""

from __future__ import annotations

import os
import subprocess

from envctl.errors import ExecutionError, ValidationError
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment


def run_command(command: list[str]) -> int:
    """Run a child process with the resolved environment injected."""
    if not command:
        raise ExecutionError("A command is required after '--'")

    _config, context = load_project_context()
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract)

    if not report.is_valid:
        raise ValidationError("Cannot run command because the resolved environment is invalid")

    env = os.environ.copy()
    env.update({key: value.value for key, value in report.values.items()})

    completed = subprocess.run(command, env=env, check=False)
    return completed.returncode
