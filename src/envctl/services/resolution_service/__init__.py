"""Public resolution service API."""

from envctl.services.resolution_service.resolution import (
    load_contract_for_context,
    resolve_environment,
)

__all__ = [
    "load_contract_for_context",
    "resolve_environment",
]
