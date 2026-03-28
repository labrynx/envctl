"""Application-specific errors."""


class EnvctlError(Exception):
    """Base application error."""


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
