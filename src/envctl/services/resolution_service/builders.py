from __future__ import annotations

from envctl.domain.contract import VariableSpec
from envctl.domain.expansion import ExpansionResult
from envctl.domain.resolution import ResolvedValue
from envctl.services.resolution_service.expansion import format_expansion_error
from envctl.services.resolution_service.types import SelectedValue
from envctl.services.resolution_service.validation import validate_value_against_spec


def build_resolved_value(
    *,
    key: str,
    spec: VariableSpec,
    selected: SelectedValue,
    expanded: ExpansionResult,
    derived_sensitive: bool,
) -> tuple[ResolvedValue, bool]:
    """Build one final resolved value and report whether it is invalid."""
    valid = expanded.error is None
    detail: str | None = None

    if expanded.error is not None:
        detail = format_expansion_error(expanded.error)
    else:
        valid, detail = validate_value_against_spec(spec, expanded.value)

    raw_value = None if spec.sensitive or derived_sensitive else selected.raw_value
    resolved_value = ResolvedValue(
        key=key,
        raw_value=raw_value,
        value=expanded.value,
        source=selected.source,
        masked=selected.masked or derived_sensitive,
        expansion_status=expanded.status,
        expansion_refs=expanded.refs,
        expansion_error=expanded.error,
        valid=valid,
        detail=detail,
    )
    return resolved_value, not valid
