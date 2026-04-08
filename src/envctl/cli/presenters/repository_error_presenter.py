"""Presenters for structured repository detection errors."""

from __future__ import annotations

from envctl.cli.presenters.common import (
    print_action_list,
    print_bullet_list,
    print_error_title,
    print_kv_line,
    print_section,
)
from envctl.domain.error_diagnostics import (
    ProjectBindingDiagnostics,
    RepositoryDiscoveryDiagnostics,
)


def render_repository_discovery_error(
    diagnostics: RepositoryDiscoveryDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured repository discovery error to stderr."""
    print_error_title(message)

    if (
        diagnostics.repo_root is not None
        or diagnostics.cwd is not None
        or diagnostics.git_args
        or diagnostics.git_stdout is not None
        or diagnostics.git_stderr is not None
    ):
        print_section("Context", err=True)

    if diagnostics.repo_root is not None:
        print_kv_line("repo_root", str(diagnostics.repo_root), err=True)
    if diagnostics.cwd is not None:
        print_kv_line("cwd", str(diagnostics.cwd), err=True)
    if diagnostics.git_args:
        print_kv_line("git_args", " ".join(diagnostics.git_args), err=True)
    if diagnostics.git_stdout is not None:
        print_kv_line("git_stdout", diagnostics.git_stdout, err=True)
    if diagnostics.git_stderr is not None:
        print_kv_line("git_stderr", diagnostics.git_stderr, err=True)

    print_action_list(diagnostics.suggested_actions, err=True)


def render_project_binding_error(
    diagnostics: ProjectBindingDiagnostics,
    *,
    message: str,
) -> None:
    """Render a structured project binding error to stderr."""
    print_error_title(message)
    has_details = any(
        (
            diagnostics.repo_root is not None,
            diagnostics.project_id is not None,
            bool(diagnostics.matching_ids),
            bool(diagnostics.matching_directories),
        )
    )
    if has_details:
        print_section("Context", err=True)
    if diagnostics.repo_root is not None:
        print_kv_line("repo_root", str(diagnostics.repo_root), err=True)
    if diagnostics.project_id is not None:
        print_kv_line("project_id", diagnostics.project_id, err=True)
    if diagnostics.matching_ids:
        print_kv_line("matching_ids", ", ".join(diagnostics.matching_ids), err=True)
    if diagnostics.matching_directories:
        print_section("Matching directories", err=True)
        print_bullet_list((str(path) for path in diagnostics.matching_directories), err=True)

    print_action_list(diagnostics.suggested_actions, err=True)
