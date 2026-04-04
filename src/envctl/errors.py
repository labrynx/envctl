"""Application-specific errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from envctl.services.error_diagnostics import ErrorDiagnostics


class EnvctlError(Exception):
    """Base application error."""

    def __init__(
        self,
        message: str,
        *,
        diagnostics: ErrorDiagnostics | None = None,
    ) -> None:
        """Initialize an application error with optional structured diagnostics."""
        super().__init__(message)
        self.diagnostics = diagnostics


class ConfigError(EnvctlError):
    """Raised when configuration is invalid."""


class ProjectDetectionError(EnvctlError):
    """Raised when a project cannot be detected safely."""


class ContractError(EnvctlError):
    """Raised when the project contract is invalid."""


class ValidationError(EnvctlError):
    """Raised when resolved values do not satisfy the contract."""


class ResolutionError(EnvctlError):
    """Raised when environment resolution fails."""


class ExecutionError(EnvctlError):
    """Raised when command execution fails."""


class StateError(EnvctlError):
    """Raised when persisted state is invalid or cannot be read safely."""
