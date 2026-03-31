"""Unbind command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, requires_writable_runtime, text_output_only
from envctl.cli.presenters import render_project_unbind_result
from envctl.services.unbind_service import run_unbind


@handle_errors
@requires_writable_runtime("project unbind")
@text_output_only("project unbind")
def project_unbind_command() -> None:
    """Remove the local repo-to-vault binding for the current checkout."""
    repo_root, result = run_unbind()

    render_project_unbind_result(
        removed=result.removed,
        repo_root=repo_root,
        previous_project_id=result.previous_project_id,
    )
