"""Run service."""

from __future__ import annotations

import os
import subprocess

from envctl.domain.operations import RunCommandResult
from envctl.domain.project import ProjectContext
from envctl.domain.selection import ContractSelection
from envctl.errors import ExecutionError
from envctl.services.context_service import load_project_context
from envctl.services.contract_selection_service import filter_projection_values
from envctl.services.projection_validation import resolve_projectable_environment
from envctl.utils.project_paths import normalize_profile_name


def _build_child_env(resolved_values: dict[str, str]) -> dict[str, str]:
    """Build the child process environment."""
    child_env = dict(os.environ)
    child_env.update(resolved_values)
    return child_env


def _docker_run_args(command: list[str]) -> list[str] | None:
    """Return docker run arguments when the command launches a container."""
    if command[:2] == ["docker", "run"]:
        return command[2:]

    if command[:3] == ["docker", "compose", "run"]:
        return command[3:]

    if command[:3] == ["docker", "container", "run"]:
        return command[3:]

    return None


def _has_explicit_docker_env_forwarding(args: list[str]) -> bool:
    """Return whether docker run explicitly forwards env vars to the container."""
    for token in args:
        if token == "--env-file":
            return True
        if token.startswith("--env-file="):
            return True
        if token in ("-e", "--env"):
            return True
        if token.startswith("--env="):
            return True

    return False


def _build_docker_warning(command: list[str]) -> tuple[str, ...]:
    """Return advisory warnings for docker run command shapes."""
    docker_args = _docker_run_args(command)
    if docker_args is None:
        return ()

    if "--env-file" in docker_args or any(token.startswith("--env-file=") for token in docker_args):
        return ()

    if _has_explicit_docker_env_forwarding(docker_args):
        return (
            "Docker only injects variables into the container when they are forwarded "
            "explicitly with -e, --env, or --env-file. Other envctl-resolved values stay "
            "in the host-side docker client process unless you forward them too. "
            "For container workflows, prefer an explicit env-file handoff such as "
            "'docker run --env-file <(envctl export --format dotenv) my-image'.",
        )

    return (
        "envctl injected the resolved environment into the host-side docker process, not "
        "the container. Forward required container variables explicitly with -e, --env, "
        "or --env-file. For container workflows, prefer an explicit env-file handoff "
        "such as 'docker run --env-file <(envctl export --format dotenv) my-image'.",
    )


def run_command(
    command: list[str],
    active_profile: str | None = None,
    *,
    selection: ContractSelection | None = None,
) -> tuple[ProjectContext, RunCommandResult, tuple[object, ...]]:
    """Run one command with the resolved environment injected."""
    if not command:
        raise ExecutionError("No command provided")

    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)

    contract, report, warnings = resolve_projectable_environment(
        context,
        active_profile=resolved_profile,
        selection=selection,
        operation="run",
    )

    resolved_values = filter_projection_values(
        {key: item.value for key, item in report.values.items()},
        contract,
        selection=selection,
    )

    try:
        completed = subprocess.run(
            command,
            check=False,
            env=_build_child_env(resolved_values),
        )
    except OSError as exc:
        raise ExecutionError(f"Failed to launch child process: {command[0]}") from exc

    return (
        context,
        RunCommandResult(
            active_profile=resolved_profile,
            exit_code=completed.returncode,
            warnings=_build_docker_warning(command),
        ),
        warnings,
    )
