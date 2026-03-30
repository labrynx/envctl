"""Runtime and CLI output models."""

from __future__ import annotations

from enum import Enum


class RuntimeMode(str, Enum):
    """Supported runtime modes."""

    LOCAL = "local"
    CI = "ci"


class OutputFormat(str, Enum):
    """Supported CLI output formats."""

    TEXT = "text"
    JSON = "json"
