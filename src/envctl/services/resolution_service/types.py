from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SelectedValue:
    """One raw selected value before expansion."""

    key: str
    raw_value: str
    source: str
    masked: bool
