"""Application-specific errors."""

from __future__ import annotations


class EnvctlError(Exception):
    """Base application error."""


class ConfigError(EnvctlError):
    """Raised when configuration is invalid."""


class ProjectDetectionError(EnvctlError):
    """Raised when a project cannot be resolved safely."""


class LinkError(EnvctlError):
    """Raised when a link operation cannot proceed safely."""


class VaultError(EnvctlError):
    """Raised when vault operations fail."""


class ValidationError(EnvctlError):
    """Raised when user input is invalid."""