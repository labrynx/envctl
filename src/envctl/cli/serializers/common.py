"""Shared serializer helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import typer


def emit_json(payload: Mapping[str, Any]) -> None:
    """Emit one structured JSON payload to stdout."""
    typer.echo(json.dumps(dict(payload), indent=2, sort_keys=True))


def path_to_str(path: Path) -> str:
    """Serialize one path to string."""
    return str(path)
