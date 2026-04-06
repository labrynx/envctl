"""Runtime and CLI output models."""

from __future__ import annotations

from enum import StrEnum


class RuntimeMode(StrEnum):
    """Supported runtime modes."""

    LOCAL = "local"
    CI = "ci"


class OutputFormat(StrEnum):
    """Supported CLI output formats."""

    TEXT = "text"
    JSON = "json"
