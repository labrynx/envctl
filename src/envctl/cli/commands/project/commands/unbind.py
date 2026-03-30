"""Unbind command."""

from __future__ import annotations

from envctl.cli.decorators import handle_errors
from envctl.services.unbind_service import run_unbind
from envctl.utils.output import print_kv, print_success, print_warning


@handle_errors
def project_unbind_command() -> None:
    """Remove the local repo-to-vault binding for the current checkout."""
    repo_root, result = run_unbind()

    if result.removed:
        print_success("Removed local repository binding")
    else:
        print_warning("No local repository binding was present")

    print_kv("repo_root", str(repo_root))
    if result.previous_project_id is not None:
        print_kv("previous_project_id", result.previous_project_id)
