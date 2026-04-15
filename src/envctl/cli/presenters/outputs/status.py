"""Output builders for status commands."""

from __future__ import annotations

from typing import Any

from envctl.cli.presenters.common import (
    bullet_item,
    failure_message,
    field_item,
    raw_item,
    section,
    success_message,
)
from envctl.cli.presenters.formatters import (
    render_action_state,
    render_present_missing,
    render_valid_invalid,
)
from envctl.cli.presenters.models import CommandOutput, OutputItem
from envctl.cli.presenters.payloads import (
    build_command_warnings_payload,
    build_contract_selection_payload,
    build_diagnostic_summary_payload,
    build_project_context_payload,
    build_resolved_value_payload,
    path_to_str,
)
from envctl.domain.diagnostics import CheckResult, DiagnosticProblem
from envctl.domain.project import ProjectContext
from envctl.domain.status import StatusReport

_KIND_TITLES = {
    "missing_required": "Missing required keys",
    "invalid_value": "Invalid keys",
    "expansion_reference_error": "Expansion reference errors",
    "unknown_key": "Unknown keys",
}


def _build_problem_items(problem: DiagnosticProblem) -> list[OutputItem]:
    """Build display items for one status/check problem."""
    if problem.kind == "unknown_key":
        items: list[OutputItem] = [bullet_item(problem.key)]
    else:
        items = [bullet_item(f"{problem.key}: {problem.message}")]

    items.extend(raw_item(f"    action: {action}") for action in problem.actions)
    return items


def build_problem_payload(problem: DiagnosticProblem) -> dict[str, Any]:
    """Build one diagnostic problem payload."""
    return {
        "key": problem.key,
        "kind": problem.kind,
        "message": problem.message,
        "actions": list(problem.actions),
    }


def build_check_output(
    result: CheckResult,
    *,
    context: ProjectContext | None = None,
) -> CommandOutput:
    """Build one unified output model for ``check``."""
    sections = [
        section(
            "Context",
            field_item("profile", result.active_profile),
            field_item("scope", result.selection.describe()),
        )
    ]

    grouped_items: dict[str, list[OutputItem]] = {}
    for problem in result.problems:
        title = _KIND_TITLES.get(problem.kind, "Problems")
        grouped_items.setdefault(title, []).extend(_build_problem_items(problem))

    for title, items in grouped_items.items():
        sections.append(section(title, *items))

    sections.append(
        section(
            "Summary",
            field_item("total", str(result.summary.total)),
            field_item("valid", str(result.summary.valid)),
            field_item("invalid", str(result.summary.invalid)),
            field_item("unknown", str(result.summary.unknown)),
        )
    )

    messages = (
        [success_message("Environment contract satisfied")]
        if result.ok
        else [failure_message("Environment contract is not satisfied")]
    )

    metadata: dict[str, Any] = {
        "kind": "check",
        "ok": result.ok,
        "active_profile": result.active_profile,
        "selection": build_contract_selection_payload(result.selection),
        "summary": build_diagnostic_summary_payload(result.summary),
        "values": {item.key: build_resolved_value_payload(item) for item in result.values},
        "problems": [build_problem_payload(problem) for problem in result.problems],
        "warnings": build_command_warnings_payload(
            command_warnings=result.warnings,
        ),
    }
    if context is not None:
        metadata["context"] = build_project_context_payload(context)

    return CommandOutput(
        title=None,
        messages=messages,
        sections=sections,
        metadata=metadata,
    )


def _has_status_issues(report: StatusReport) -> bool:
    """Return whether the report indicates user-facing issues."""
    return bool(report.issues) or not report.contract_exists or not report.resolved_valid


def build_status_output(report: StatusReport) -> CommandOutput:
    """Build one unified output model for ``status``."""
    has_issues = _has_status_issues(report)

    sections = [
        section("Status", field_item("state", render_action_state(has_issues))),
        section(
            "Project",
            field_item("name", report.project_slug),
            field_item("id", report.project_id),
            field_item("repository", str(report.repo_root)),
        ),
        section(
            "Checks",
            field_item("contract", render_present_missing(report.contract_exists)),
            field_item("vault values", render_present_missing(report.vault_exists)),
            field_item("resolution", render_valid_invalid(report.resolved_valid)),
        ),
        section(
            "Summary",
            raw_item(report.summary),
        ),
    ]

    if report.issues:
        sections.append(
            section(
                "Issues",
                *(bullet_item(issue) for issue in report.issues),
            )
        )

    if report.suggested_action:
        sections.append(
            section(
                "Next step",
                raw_item(report.suggested_action),
            )
        )

    metadata: dict[str, Any] = {
        "kind": "status",
        "ok": not has_issues,
        "project_slug": report.project_slug,
        "project_id": report.project_id,
        "repo_root": path_to_str(report.repo_root),
        "contract_exists": report.contract_exists,
        "vault_exists": report.vault_exists,
        "resolved_valid": report.resolved_valid,
        "summary": report.summary,
        "issues": list(report.issues),
        "suggested_action": report.suggested_action,
    }

    return CommandOutput(
        title=None,
        messages=[],
        sections=sections,
        metadata=metadata,
    )


def build_status_view_output(
    *,
    profile: str,
    report: StatusReport,
) -> CommandOutput:
    """Build one unified output model for ``status`` including active profile."""
    output = build_status_output(report)
    context_section = section(
        "Context",
        field_item("profile", profile),
    )
    return CommandOutput(
        title=output.title,
        messages=output.messages,
        sections=[context_section, *output.sections],
        metadata={
            **output.metadata,
            "active_profile": profile,
        },
    )
