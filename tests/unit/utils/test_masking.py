from __future__ import annotations

from envctl.utils.masking import mask_value


def test_mask_value_returns_empty_string_for_empty_value() -> None:
    assert mask_value("") == ""


def test_mask_value_masks_short_values_fully() -> None:
    assert mask_value("a") == "*"
    assert mask_value("ab") == "**"
    assert mask_value("abcd") == "****"


def test_mask_value_preserves_edges_for_longer_values() -> None:
    assert mask_value("super-secret") == "su********et"
