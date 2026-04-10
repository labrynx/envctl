"""Run service."""

from __future__ import annotations

import os
import subprocess

from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.operations import RunCommandResult
from envctl.domain.project import ProjectContext
from envctl.domain.selection import ContractSelection
from envctl.errors import ExecutionError
from envctl.observability.fields import command_preview, selection_scope
from envctl.observability.timing import observe_span
from envctl.services.context_service import load_project_context
from envctl.services.projection_validation import resolve_projectable_environment
from envctl.services.selection_filtering import filter_projection_values
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


def _has_docker_env_file_handoff(args: list[str]) -> bool:
    """Return whether docker run uses an explicit env-file handoff."""
    for arg in args:
        if arg == "--env-file":
            return True
        if arg.startswith("--env-file="):
            return True
    return False


def _has_explicit_docker_env_forwarding(args: list[str]) -> bool:
    """Return whether docker run explicitly forwards env vars to the container."""
    for arg in args:
        if arg in ("-e", "--env", "--env-file"):
            return True
        if arg.startswith("--env="):
            return True
        if arg.startswith("--env-file="):
            return True
    return False


def _build_docker_warning(command: list[str]) -> tuple[str, ...]:
    """Return advisory warnings for docker run command shapes."""
    docker_args = _docker_run_args(command)
    if docker_args is None:
        return ()

    if _has_docker_env_file_handoff(docker_args):
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
) -> tuple[ProjectContext, RunCommandResult, tuple[ContractDeprecationWarning, ...]]:
    """Run one command with the resolved environment injected."""
    command_head = command[0] if command else "-"
    span_fields = {
        "arg_count": len(command),
        "command_head": command_head,
        "selection_scope": selection_scope(selection),
    }
    with observe_span(
        "run.exec",
        module=__name__,
        operation="run_command",
        fields=span_fields,
    ):
        if not command:
            span_fields["reason"] = "empty_command"
            raise ExecutionError("No command provided")

        _config, context = load_project_context()
        resolved_profile = normalize_profile_name(active_profile)
        span_fields["selected_profile"] = resolved_profile

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
        span_fields["command"] = command_preview(command)
        span_fields["resolved_key_count"] = len(resolved_values)

        try:
            subprocess_fields = {
                "arg_count": len(command),
                "command_head": command_head,
                "selected_profile": resolved_profile,
            }
            with observe_span(
                "subprocess.exec",
                module=__name__,
                operation="run_command",
                fields=subprocess_fields,
            ) as child_fields:
                # Intentional: envctl run executes a user-requested command.
                completed = subprocess.run(  # nosec  # noqa: S603
                    command,
                    check=False,
                    env=_build_child_env(resolved_values),
                )
                child_fields["exit_code"] = completed.returncode
        except OSError as exc:
            raise ExecutionError(f"Failed to launch child process: {command[0]}") from exc

        docker_warnings = _build_docker_warning(command)
        span_fields["warning_count"] = len(docker_warnings)
        span_fields["exit_code"] = completed.returncode

        return (
            context,
            RunCommandResult(
                active_profile=resolved_profile,
                exit_code=completed.returncode,
                warnings=docker_warnings,
            ),
            warnings,
        )
