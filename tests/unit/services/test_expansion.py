from __future__ import annotations

from envctl.domain.expansion import LiteralSegment, PlaceholderSegment, parse_placeholder_segments


def test_parse_placeholder_segments_returns_literals_when_no_placeholders() -> None:
    segments, error = parse_placeholder_segments("plain-text")

    assert error is None
    assert segments == (LiteralSegment("plain-text"),)


def test_parse_placeholder_segments_parses_multiple_placeholders() -> None:
    segments, error = parse_placeholder_segments("prefix-${USER}-${PASSWORD}")

    assert error is None
    assert segments == (
        LiteralSegment("prefix-"),
        PlaceholderSegment("USER"),
        LiteralSegment("-"),
        PlaceholderSegment("PASSWORD"),
    )


def test_parse_placeholder_segments_rejects_unclosed_placeholder() -> None:
    _segments, error = parse_placeholder_segments("prefix-${USER")

    assert error is not None
    assert error.kind == "syntax_error"


def test_parse_placeholder_segments_rejects_invalid_names() -> None:
    _segments, error = parse_placeholder_segments("${A-B}")

    assert error is not None
    assert error.kind == "syntax_error"


def test_parse_placeholder_segments_rejects_unsupported_shell_syntax() -> None:
    _segments, error = parse_placeholder_segments("${USER:-default}")

    assert error is not None
    assert error.kind == "syntax_error"
