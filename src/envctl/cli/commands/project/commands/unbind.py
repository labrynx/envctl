"""Unbind command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors, requires_writable_runtime
from envctl.cli.presenters import present
from envctl.cli.presenters.outputs.actions import build_project_unbind_output
from envctl.cli.runtime import is_json_output


@handle_errors
@requires_writable_runtime("project unbind")
def project_unbind_command() -> None:
    """Remove the local repo-to-vault binding for the current checkout."""
    from envctl.services.unbind_service import run_unbind

    repo_root, result = run_unbind()

    present(
        build_project_unbind_output(
            removed=result.removed,
            repo_root=repo_root,
            previous_project_id=result.previous_project_id,
        ),
        output_format="json" if is_json_output() else "text",
    )
