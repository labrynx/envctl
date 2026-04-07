"""Atomic file writing helpers."""

from __future__ import annotations

import json
import os
import tempfile
from contextlib import suppress
from pathlib import Path
from typing import Any


def write_text_atomic(
    path: Path,
    content: str,
    *,
    mode: int = 0o600,
) -> None:
    """Write text atomically using a restrictive file mode from creation time."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    tmp_path = Path(tmp_name)

    try:
        with suppress(AttributeError):
            os.fchmod(fd, mode)

        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(tmp_path, path)

        with suppress(OSError):
            path.chmod(mode)
    except Exception:
        with suppress(OSError):
            tmp_path.unlink(missing_ok=True)
        raise


def write_json_atomic(
    path: Path,
    payload: dict[str, Any],
    *,
    mode: int = 0o600,
) -> None:
    """Write JSON to a file atomically."""
    content = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    write_text_atomic(path, content, mode=mode)


def write_bytes_atomic(
    path: Path,
    content: bytes,
    *,
    mode: int = 0o600,
) -> None:
    """Write bytes atomically using a restrictive file mode from creation time."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp_path = Path(tmp_name)

    try:
        with suppress(AttributeError):
            os.fchmod(fd, mode)

        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(tmp_path, path)

        with suppress(OSError):
            path.chmod(mode)
    except Exception:
        with suppress(OSError):
            tmp_path.unlink(missing_ok=True)
        raise
