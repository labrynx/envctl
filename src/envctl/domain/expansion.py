"""Expansion grammar and result models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from envctl.domain.contract import is_valid_variable_name

ExpansionStatus = Literal["none", "expanded", "error"]
ExpansionErrorType = Literal[
    "syntax_error",
    "reference_resolution_error",
    "cycle_error",
    "depth_exceeded_error",
]

MAX_EXPANSION_DEPTH = 32


@dataclass(frozen=True)
class LiteralSegment:
    """One literal segment of a template."""

    value: str


@dataclass(frozen=True)
class PlaceholderSegment:
    """One placeholder segment of a template."""

    name: str


Segment = LiteralSegment | PlaceholderSegment


@dataclass(frozen=True)
class ExpansionErrorInfo:
    """Structured expansion error details."""

    kind: ExpansionErrorType
    detail: str


@dataclass(frozen=True)
class ExpansionResult:
    """Expansion result for one selected value."""

    value: str
    status: ExpansionStatus
    refs: tuple[str, ...]
    error: ExpansionErrorInfo | None = None


def parse_placeholder_segments(value: str) -> tuple[tuple[Segment, ...], ExpansionErrorInfo | None]:
    """Parse one raw value into literal and placeholder segments."""
    if "${" not in value:
        return ((LiteralSegment(value),), None)

    segments: list[Segment] = []
    current: list[str] = []
    index = 0

    while index < len(value):
        char = value[index]
        if char == "$" and index + 1 < len(value) and value[index + 1] == "{":
            if current:
                segments.append(LiteralSegment("".join(current)))
                current = []

            end_index = value.find("}", index + 2)
            if end_index == -1:
                return (), ExpansionErrorInfo(
                    kind="syntax_error",
                    detail="Invalid expansion syntax: missing closing '}'",
                )

            placeholder = value[index + 2 : end_index]
            if not placeholder:
                return (), ExpansionErrorInfo(
                    kind="syntax_error",
                    detail="Invalid expansion syntax: empty placeholder name",
                )
            if not is_valid_variable_name(placeholder):
                return (), ExpansionErrorInfo(
                    kind="syntax_error",
                    detail=f"Invalid expansion syntax: unsupported placeholder '{placeholder}'",
                )

            segments.append(PlaceholderSegment(placeholder))
            index = end_index + 1
            continue

        current.append(char)
        index += 1

    if current:
        segments.append(LiteralSegment("".join(current)))

    return tuple(segments), None
