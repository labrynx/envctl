"""Doctor domain models."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DoctorCheck:
    """Single doctor check result."""

    name: str
    status: str
    detail: str
