"""Access to process environment variables."""

from __future__ import annotations

import os
from collections.abc import Mapping


class ProcessEnvironmentProvider:
    """Resolve variables from the current process environment."""

    def __init__(self, environ: Mapping[str, str] | None = None) -> None:
        self._environ = environ if environ is not None else os.environ

    def get(self, key: str) -> str | None:
        """Return one process environment value."""
        return self._environ.get(key)
