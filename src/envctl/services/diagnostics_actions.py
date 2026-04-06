"""Stable action suggestions for diagnostic problems."""

from __future__ import annotations

from envctl.domain.diagnostics import ProblemKind


def actions_for_problem(
    kind: ProblemKind,
    *,
    key: str,
    referenced_key: str | None = None,
) -> tuple[str, ...]:
    """Return deterministic actions for one problem kind."""
    if kind == "missing_required":
        return ("envctl fill", f"envctl set {key} <value>")
    if kind == "invalid_value":
        return (f"envctl set {key} <value>", f"envctl inspect {key}")
    if kind == "expansion_reference_error":
        if referenced_key is not None:
            return (
                f"envctl inspect {referenced_key}",
                f"envctl set {referenced_key} <value>",
            )
        return (f"envctl inspect {key}",)
    if kind == "unknown_key":
        return ("envctl vault prune", "remove manually from the active profile")
    return ("envctl check", "fix .envctl.schema.yaml")
