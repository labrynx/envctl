"""Shared builders for resolution-based diagnostic commands."""

from __future__ import annotations

from envctl.domain.diagnostics import DiagnosticProblem, DiagnosticSummary, ProblemKind
from envctl.domain.resolution import ResolutionReport
from envctl.services.diagnostics_actions import actions_for_problem


def extract_referenced_key(message: str) -> str | None:
    """Extract one referenced key name from a known expansion error detail."""
    marker = "referenced key '"
    if marker not in message:
        return None
    start = message.find(marker) + len(marker)
    end = message.find("'", start)
    if end == -1:
        return None
    return message[start:end]


def build_diagnostic_problems(report: ResolutionReport) -> tuple[DiagnosticProblem, ...]:
    """Build one stable list of actionable diagnostic problems from a report."""
    problems: list[DiagnosticProblem] = []

    for key in report.missing_required:
        problems.append(
            DiagnosticProblem(
                key=key,
                kind="missing_required",
                message="missing required value",
                actions=actions_for_problem("missing_required", key=key),
            )
        )

    for key in report.invalid_keys:
        item = report.values.get(key)
        kind: ProblemKind
        if item is not None and item.expansion_error is not None:
            message = item.expansion_error.detail
            kind = "expansion_reference_error"
            referenced_key = extract_referenced_key(message)
            actions = actions_for_problem(kind, key=key, referenced_key=referenced_key)
        else:
            message = item.detail if item is not None and item.detail else "invalid value"
            kind = "invalid_value"
            actions = actions_for_problem(kind, key=key)
        problems.append(
            DiagnosticProblem(
                key=key,
                kind=kind,
                message=message,
                actions=actions,
            )
        )

    for key in report.unknown_keys:
        problems.append(
            DiagnosticProblem(
                key=key,
                kind="unknown_key",
                message="unknown key",
                actions=actions_for_problem("unknown_key", key=key),
            )
        )

    return tuple(problems)


def build_diagnostic_summary(report: ResolutionReport) -> DiagnosticSummary:
    """Build one compact summary from a resolution report."""
    total = len(report.values) + len(report.missing_required)
    invalid = len(report.missing_required) + len(report.invalid_keys)
    unknown = len(report.unknown_keys)
    valid = max(total - invalid, 0)
    return DiagnosticSummary(total=total, valid=valid, invalid=invalid, unknown=unknown)
