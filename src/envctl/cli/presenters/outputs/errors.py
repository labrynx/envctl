"""Output builders for error diagnostics."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from envctl.cli.presenters.common import (
    action_list_section,
    bullet_item,
    error_message,
    field_item,
    raw_item,
    section,
)
from envctl.cli.presenters.models import CommandOutput, OutputItem, OutputSection
from envctl.cli.presenters.payloads import (
    build_contract_selection_payload,
    build_resolution_problem_lines,
    build_resolution_report_payload,
    path_to_str,
)
from envctl.domain.error_diagnostics import (
    ConfigDiagnostics,
    ContractDiagnostics,
    ErrorDiagnostics,
    ProjectBindingDiagnostics,
    ProjectionValidationDiagnostics,
    RepositoryDiscoveryDiagnostics,
    StateDiagnostics,
)


def build_projection_validation_diagnostics_payload(
    diagnostics: ProjectionValidationDiagnostics,
) -> dict[str, Any]:
    """Build structured payload for one blocked projection command."""
    return {
        "category": diagnostics.category,
        "operation": diagnostics.operation,
        "active_profile": diagnostics.active_profile,
        "selection": build_contract_selection_payload(diagnostics.selection),
        "report": build_resolution_report_payload(diagnostics.report),
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def build_contract_diagnostics_payload(
    diagnostics: ContractDiagnostics,
) -> dict[str, Any]:
    """Build structured payload for one contract failure."""
    return {
        "category": diagnostics.category,
        "path": path_to_str(diagnostics.path),
        "key": diagnostics.key,
        "field": diagnostics.field,
        "issues": [
            {
                "field": issue.field,
                "detail": issue.detail,
            }
            for issue in diagnostics.issues
        ],
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def build_config_diagnostics_payload(
    diagnostics: ConfigDiagnostics,
) -> dict[str, Any]:
    """Build structured payload for one configuration failure."""
    return {
        "category": diagnostics.category,
        "path": path_to_str(diagnostics.path) if diagnostics.path is not None else None,
        "key": diagnostics.key,
        "field": diagnostics.field,
        "source_label": diagnostics.source_label,
        "value": diagnostics.value,
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def build_state_diagnostics_payload(
    diagnostics: StateDiagnostics,
) -> dict[str, Any]:
    """Build structured payload for one state failure."""
    return {
        "category": diagnostics.category,
        "path": path_to_str(diagnostics.path),
        "field": diagnostics.field,
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def build_repository_discovery_diagnostics_payload(
    diagnostics: RepositoryDiscoveryDiagnostics,
) -> dict[str, Any]:
    """Build structured payload for repository discovery failures."""
    return {
        "category": diagnostics.category,
        "repo_root": path_to_str(diagnostics.repo_root) if diagnostics.repo_root else None,
        "cwd": path_to_str(diagnostics.cwd) if diagnostics.cwd else None,
        "git_args": list(diagnostics.git_args),
        "git_stdout": diagnostics.git_stdout,
        "git_stderr": diagnostics.git_stderr,
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def build_project_binding_diagnostics_payload(
    diagnostics: ProjectBindingDiagnostics,
) -> dict[str, Any]:
    """Build structured payload for project binding failures."""
    return {
        "category": diagnostics.category,
        "repo_root": path_to_str(diagnostics.repo_root) if diagnostics.repo_root else None,
        "project_id": diagnostics.project_id,
        "matching_ids": list(diagnostics.matching_ids),
        "matching_directories": [path_to_str(path) for path in diagnostics.matching_directories],
        "suggested_actions": list(diagnostics.suggested_actions),
    }


def build_error_diagnostics_payload(diagnostics: ErrorDiagnostics) -> dict[str, Any]:
    """Build one known structured error diagnostics payload."""
    if isinstance(diagnostics, ProjectionValidationDiagnostics):
        return build_projection_validation_diagnostics_payload(diagnostics)
    if isinstance(diagnostics, ContractDiagnostics):
        return build_contract_diagnostics_payload(diagnostics)
    if isinstance(diagnostics, ConfigDiagnostics):
        return build_config_diagnostics_payload(diagnostics)
    if isinstance(diagnostics, StateDiagnostics):
        return build_state_diagnostics_payload(diagnostics)
    if isinstance(diagnostics, RepositoryDiscoveryDiagnostics):
        return build_repository_discovery_diagnostics_payload(diagnostics)
    if isinstance(diagnostics, ProjectBindingDiagnostics):
        return build_project_binding_diagnostics_payload(diagnostics)

    raise TypeError(f"Unsupported diagnostics type: {type(diagnostics).__name__}")


def _error_metadata(
    *,
    error_type: str,
    message: str,
    details: Mapping[str, Any] | dict[str, Any] | None,
    command: str | None = None,
) -> dict[str, Any]:
    """Build one standard metadata envelope for command errors."""
    metadata: dict[str, Any] = {
        "ok": False,
        "error": {
            "type": error_type,
            "message": message,
            "details": dict(details) if details is not None else None,
        },
    }
    if command is not None:
        metadata["command"] = command
    return metadata


def _context_section(
    items: Iterable[OutputItem],
    *,
    err: bool = True,
    title: str = "Context",
) -> OutputSection | None:
    """Build one context section when items are available."""
    rendered = list(items)
    if not rendered:
        return None
    return section(title, *rendered, err=err)


def _next_steps_section(
    actions: Iterable[str],
    *,
    err: bool = True,
) -> OutputSection | None:
    """Build one next-steps section when actions are available."""
    return action_list_section(actions, err=err)


def _finalize_error_output(
    *,
    message: str,
    error_type: str,
    details: Mapping[str, Any] | dict[str, Any] | None,
    sections: list[OutputSection],
    command: str | None = None,
) -> CommandOutput:
    """Build one final structured error output."""
    return CommandOutput(
        messages=[error_message(message, err=True)],
        sections=sections,
        metadata=_error_metadata(
            error_type=error_type,
            message=message,
            details=details,
            command=command,
        ),
    )


def _append_if_present(sections: list[OutputSection], candidate: OutputSection | None) -> None:
    """Append one section when it exists."""
    if candidate is not None:
        sections.append(candidate)


def build_error_output(
    *,
    error_type: str,
    message: str,
    command: str | None,
    details: Mapping[str, Any] | None = None,
) -> CommandOutput:
    """Build one generic command error output."""
    return _finalize_error_output(
        message=message,
        error_type=error_type,
        details=details,
        sections=[],
        command=command,
    )


def build_config_error_output(
    diagnostics: ConfigDiagnostics,
    *,
    message: str,
) -> CommandOutput:
    """Build one unified output model for a structured config error."""
    context_items: list[OutputItem] = []
    if diagnostics.path is not None:
        context_items.append(field_item("path", str(diagnostics.path), err=True))
    if diagnostics.source_label is not None:
        context_items.append(field_item("source", diagnostics.source_label, err=True))
    if diagnostics.key is not None:
        context_items.append(field_item("key", diagnostics.key, err=True))
    if diagnostics.field is not None:
        context_items.append(field_item("field", diagnostics.field, err=True))
    if diagnostics.value is not None:
        context_items.append(field_item("value", diagnostics.value, err=True))

    sections: list[OutputSection] = []
    _append_if_present(sections, _context_section(context_items))
    _append_if_present(sections, _next_steps_section(diagnostics.suggested_actions))

    return _finalize_error_output(
        message=message,
        error_type=diagnostics.category,
        details=build_config_diagnostics_payload(diagnostics),
        sections=sections,
    )


def build_contract_error_output(
    diagnostics: ContractDiagnostics,
    *,
    message: str,
) -> CommandOutput:
    """Build one unified output model for a structured contract error."""
    context_items: list[OutputItem] = [
        field_item("path", str(diagnostics.path), err=True),
    ]
    if diagnostics.field is not None:
        context_items.append(field_item("field", diagnostics.field, err=True))
    if diagnostics.key is not None:
        context_items.append(field_item("key", diagnostics.key, err=True))

    sections: list[OutputSection] = []
    _append_if_present(sections, _context_section(context_items))

    if diagnostics.issues:
        sections.append(
            section(
                "Contract issues",
                *(field_item(issue.field, issue.detail, err=True) for issue in diagnostics.issues),
                err=True,
            )
        )

    _append_if_present(sections, _next_steps_section(diagnostics.suggested_actions))

    return _finalize_error_output(
        message=message,
        error_type=diagnostics.category,
        details=build_contract_diagnostics_payload(diagnostics),
        sections=sections,
    )


def build_projection_validation_failure_output(
    diagnostics: ProjectionValidationDiagnostics,
    *,
    message: str,
) -> CommandOutput:
    """Build one unified output model for a projection validation failure."""
    problem_items: list[OutputItem] = []
    for line in build_resolution_problem_lines(
        diagnostics.report,
        unknown_keys_title="Unknown keys in vault for the current contract",
    ):
        if not line:
            continue
        if line.startswith("  - "):
            problem_items.append(bullet_item(line[4:], err=True))
        else:
            problem_items.append(raw_item(line, err=True))

    sections: list[OutputSection] = [
        section(
            "Context",
            field_item("profile", diagnostics.active_profile, err=True),
            field_item("scope", diagnostics.selection.describe(), err=True),
            err=True,
        )
    ]

    if problem_items:
        sections.append(section("Problems", *problem_items, err=True))

    _append_if_present(sections, _next_steps_section(diagnostics.suggested_actions))

    return _finalize_error_output(
        message=message,
        error_type=diagnostics.category,
        details=build_projection_validation_diagnostics_payload(diagnostics),
        sections=sections,
    )


def build_repository_discovery_error_output(
    diagnostics: RepositoryDiscoveryDiagnostics,
    *,
    message: str,
) -> CommandOutput:
    """Build one unified output model for a repository discovery error."""
    context_items: list[OutputItem] = []
    if diagnostics.repo_root is not None:
        context_items.append(field_item("repo_root", str(diagnostics.repo_root), err=True))
    if diagnostics.cwd is not None:
        context_items.append(field_item("cwd", str(diagnostics.cwd), err=True))
    if diagnostics.git_args:
        context_items.append(field_item("git_args", " ".join(diagnostics.git_args), err=True))
    if diagnostics.git_stdout is not None:
        context_items.append(field_item("git_stdout", diagnostics.git_stdout, err=True))
    if diagnostics.git_stderr is not None:
        context_items.append(field_item("git_stderr", diagnostics.git_stderr, err=True))

    sections: list[OutputSection] = []
    _append_if_present(sections, _context_section(context_items))
    _append_if_present(sections, _next_steps_section(diagnostics.suggested_actions))

    return _finalize_error_output(
        message=message,
        error_type=diagnostics.category,
        details=build_repository_discovery_diagnostics_payload(diagnostics),
        sections=sections,
    )


def build_project_binding_error_output(
    diagnostics: ProjectBindingDiagnostics,
    *,
    message: str,
) -> CommandOutput:
    """Build one unified output model for a project binding error."""
    context_items: list[OutputItem] = []
    if diagnostics.repo_root is not None:
        context_items.append(field_item("repo_root", str(diagnostics.repo_root), err=True))
    if diagnostics.project_id is not None:
        context_items.append(field_item("project_id", diagnostics.project_id, err=True))
    if diagnostics.matching_ids:
        context_items.append(
            field_item("matching_ids", ", ".join(diagnostics.matching_ids), err=True)
        )

    sections: list[OutputSection] = []
    _append_if_present(sections, _context_section(context_items))

    if diagnostics.matching_directories:
        sections.append(
            section(
                "Matching directories",
                *(bullet_item(str(path), err=True) for path in diagnostics.matching_directories),
                err=True,
            )
        )

    _append_if_present(sections, _next_steps_section(diagnostics.suggested_actions))

    return _finalize_error_output(
        message=message,
        error_type=diagnostics.category,
        details=build_project_binding_diagnostics_payload(diagnostics),
        sections=sections,
    )


def build_state_error_output(
    diagnostics: StateDiagnostics,
    *,
    message: str,
) -> CommandOutput:
    """Build one unified output model for a structured state error."""
    context_items: list[OutputItem] = [
        field_item("path", str(diagnostics.path), err=True),
    ]
    if diagnostics.field is not None:
        context_items.append(field_item("field", diagnostics.field, err=True))

    sections: list[OutputSection] = []
    _append_if_present(sections, _context_section(context_items))
    _append_if_present(sections, _next_steps_section(diagnostics.suggested_actions))

    return _finalize_error_output(
        message=message,
        error_type=diagnostics.category,
        details=build_state_diagnostics_payload(diagnostics),
        sections=sections,
    )
