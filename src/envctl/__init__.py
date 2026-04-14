"""envctl package."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("envctl")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = ["__version__"]
