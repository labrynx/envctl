from __future__ import annotations

from collections.abc import Callable

from envctl.domain.contract import Contract
from envctl.domain.expansion import (
    MAX_EXPANSION_DEPTH,
    ExpansionErrorInfo,
    ExpansionErrorType,
    ExpansionResult,
    LiteralSegment,
    PlaceholderResolution,
    Segment,
    parse_placeholder_segments,
)
from envctl.services.resolution_service.types import SelectedValue


def format_expansion_error(error: ExpansionErrorInfo) -> str:
    """Render one expansion error for user-facing output."""
    labels = {
        "syntax_error": "Expansion syntax error",
        "reference_resolution_error": "Expansion reference error",
        "cycle_error": "Expansion cycle error",
        "depth_exceeded_error": "Expansion depth error",
    }
    return f"{labels[error.kind]}: {error.detail}"


def _make_expansion_error_result(
    *,
    value: str,
    kind: ExpansionErrorType,
    detail: str,
    refs: tuple[str, ...] = (),
) -> ExpansionResult:
    """Build one failed expansion result."""
    return ExpansionResult(
        value=value,
        status="error",
        refs=refs,
        error=ExpansionErrorInfo(kind=kind, detail=detail),
    )


def _resolve_placeholder_value(
    *,
    contract: Contract,
    selected_values: dict[str, SelectedValue],
    derived_sensitive: dict[str, bool],
    resolve_key: Callable[[str, int, tuple[str, ...]], ExpansionResult],
    current_key: str,
    placeholder_name: str,
    refs: list[str],
    depth: int,
    path: tuple[str, ...],
) -> PlaceholderResolution:
    """Resolve one placeholder to a string or an error result."""
    if placeholder_name not in contract.variables:
        return PlaceholderResolution(
            value=None,
            error_result=_make_expansion_error_result(
                value=selected_values[current_key].raw_value,
                kind="reference_resolution_error",
                detail=f"Unknown placeholder '{placeholder_name}'",
                refs=tuple(refs),
            ),
            inherited_sensitive=False,
        )

    referenced = selected_values.get(placeholder_name)
    if referenced is None:
        return PlaceholderResolution(
            value=None,
            error_result=_make_expansion_error_result(
                value=selected_values[current_key].raw_value,
                kind="reference_resolution_error",
                detail=f"Missing value for referenced key '{placeholder_name}'",
                refs=tuple(refs),
            ),
            inherited_sensitive=False,
        )

    nested = resolve_key(placeholder_name, depth + 1, path)
    if nested.error is not None:
        propagated_refs = (
            nested.refs if nested.error.kind == "cycle_error" else tuple(refs + list(nested.refs))
        )
        return PlaceholderResolution(
            value=None,
            error_result=ExpansionResult(
                value=selected_values[current_key].raw_value,
                status="error",
                refs=propagated_refs,
                error=nested.error,
            ),
            inherited_sensitive=False,
        )

    inherited_sensitive = referenced.masked or derived_sensitive.get(
        placeholder_name,
        False,
    )
    return PlaceholderResolution(
        value=nested.value,
        error_result=None,
        inherited_sensitive=inherited_sensitive,
    )


def _get_cached_or_guarded_result(
    *,
    key: str,
    depth: int,
    path: tuple[str, ...],
    selected_values: dict[str, SelectedValue],
    states: dict[str, str],
    expanded: dict[str, ExpansionResult],
) -> ExpansionResult | None:
    """Return one cached or immediate guard error before expanding."""
    if key in expanded:
        return expanded[key]

    if depth > MAX_EXPANSION_DEPTH:
        result = _make_expansion_error_result(
            value=selected_values[key].raw_value,
            kind="depth_exceeded_error",
            detail=f"Expansion depth exceeded for '{key}'",
        )
        expanded[key] = result
        return result

    state = states[key]
    if state == "visiting":
        cycle_path = (*path, key)
        result = _make_expansion_error_result(
            value=selected_values[key].raw_value,
            kind="cycle_error",
            detail=f"Cycle detected: {' -> '.join(cycle_path)}",
            refs=cycle_path,
        )
        expanded[key] = result
        return result

    if state == "resolved":
        return expanded[key]

    return None


def _expand_segments(
    *,
    contract: Contract,
    current_key: str,
    segments: tuple[Segment, ...],
    selected_values: dict[str, SelectedValue],
    derived_sensitive: dict[str, bool],
    resolve_key: Callable[[str, int, tuple[str, ...]], ExpansionResult],
    depth: int,
    path: tuple[str, ...],
) -> tuple[ExpansionResult, bool]:
    """Expand one parsed segment sequence."""
    parts: list[str] = []
    refs: list[str] = []
    inherited_sensitive = False

    for segment in segments:
        if isinstance(segment, LiteralSegment):
            parts.append(segment.value)
            continue

        refs.append(segment.name)
        resolution = _resolve_placeholder_value(
            contract=contract,
            selected_values=selected_values,
            derived_sensitive=derived_sensitive,
            resolve_key=resolve_key,
            current_key=current_key,
            placeholder_name=segment.name,
            refs=refs,
            depth=depth,
            path=path,
        )
        if resolution.error_result is not None:
            return resolution.error_result, inherited_sensitive

        inherited_sensitive = inherited_sensitive or resolution.inherited_sensitive
        parts.append(resolution.value or "")

    return (
        ExpansionResult(value="".join(parts), status="expanded", refs=tuple(refs)),
        inherited_sensitive,
    )


def expand_selected_values(
    contract: Contract,
    selected_values: dict[str, SelectedValue],
) -> tuple[dict[str, ExpansionResult], dict[str, bool]]:
    """Expand all selected values using contract-aware references."""
    states: dict[str, str] = {key: "unvisited" for key in selected_values}
    expanded: dict[str, ExpansionResult] = {}
    derived_sensitive: dict[str, bool] = {key: False for key in selected_values}

    def resolve_key(key: str, depth: int, path: tuple[str, ...]) -> ExpansionResult:
        cached = _get_cached_or_guarded_result(
            key=key,
            depth=depth,
            path=path,
            selected_values=selected_values,
            states=states,
            expanded=expanded,
        )
        if cached is not None:
            return cached

        states[key] = "visiting"
        current = selected_values[key]
        segments, parse_error = parse_placeholder_segments(current.raw_value)

        if parse_error is not None:
            result = ExpansionResult(
                value=current.raw_value,
                status="error",
                refs=(),
                error=parse_error,
            )
            expanded[key] = result
            states[key] = "resolved"
            return result

        if all(isinstance(segment, LiteralSegment) for segment in segments):
            result = ExpansionResult(value=current.raw_value, status="none", refs=())
            expanded[key] = result
            states[key] = "resolved"
            return result

        result, inherited_sensitive = _expand_segments(
            contract=contract,
            current_key=key,
            segments=segments,
            selected_values=selected_values,
            derived_sensitive=derived_sensitive,
            resolve_key=resolve_key,
            depth=depth,
            path=(*path, key),
        )
        derived_sensitive[key] = inherited_sensitive
        expanded[key] = result
        states[key] = "resolved"
        return result

    for key in sorted(selected_values):
        resolve_key(key, 0, ())

    return expanded, derived_sensitive
