"""Git secret guard command."""

from __future__ import annotations

import typer

from envctl.cli.command_support import build_json_command_payload
from envctl.cli.decorators import handle_errors
from envctl.cli.runtime import is_json_output
from envctl.cli.serializers import emit_json
from envctl.services.context_service import load_project_context
from envctl.services.git_secret_guard_service import GitSecretGuardResult, run_git_secret_guard
from envctl.utils.output import print_error, print_kv, print_success


def _serialize_guard_result(result: GitSecretGuardResult) -> dict[str, object]:
    findings = []
    for finding in result.findings:
        findings.append(
            {
                "path": str(finding.path),
                "kind": finding.kind,
                "message": finding.message,
                "actions": list(finding.actions),
            }
        )
    return {
        "scanned_paths": [str(path) for path in result.scanned_paths],
        "findings": findings,
    }


@handle_errors
def guard_secrets_command() -> None:
    """Block staged envctl vault artifacts and master keys."""
    _config, context = load_project_context()
    result = run_git_secret_guard(context)

    if is_json_output():
        emit_json(
            build_json_command_payload(
                command="guard secrets",
                ok=result.ok,
                data=_serialize_guard_result(result),
                command_warnings=context.runtime_warnings,
            )
        )
        if not result.ok:
            raise typer.Exit(code=1)
        return

    if context.runtime_warnings:
        for warning in context.runtime_warnings:
            print_error(warning.message)

    if result.ok:
        print_success("No staged envctl secrets detected")
        print_kv("scanned_paths", str(len(result.scanned_paths)))
        return

    for finding in result.findings:
        print_error(f"{finding.path}: {finding.message}")
        for action in finding.actions:
            print_kv("action", action)

    raise typer.Exit(code=1)
