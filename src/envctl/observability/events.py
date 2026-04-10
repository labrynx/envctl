"""Canonical observability event names and stable families."""

from __future__ import annotations

COMMAND_START = "command.start"
COMMAND_FINISH = "command.finish"
COMMAND_ERROR = "command.error"

CONTEXT_RESOLVE_START = "context.resolve.start"
CONTEXT_RESOLVE_FINISH = "context.resolve.finish"
CONTEXT_RESOLVE_ERROR = "context.resolve.error"

CONTRACT_COMPOSE_START = "contract.compose.start"
CONTRACT_COMPOSE_FINISH = "contract.compose.finish"
CONTRACT_COMPOSE_ERROR = "contract.compose.error"

RESOLUTION_START = "resolution.start"
RESOLUTION_FINISH = "resolution.finish"
RESOLUTION_ERROR = "resolution.error"

RUN_EXEC_START = "run.exec.start"
RUN_EXEC_FINISH = "run.exec.finish"
RUN_EXEC_ERROR = "run.exec.error"

VAULT_START = "vault.start"
VAULT_FINISH = "vault.finish"
VAULT_ERROR = "vault.error"

ERROR_HANDLED = "error.handled"
ERROR_UNHANDLED = "error.unhandled"

# Minimal cross-module error taxonomy.
ERROR_VALIDATION = "error.validation"
ERROR_EXECUTION = "error.execution"
ERROR_CONFIGURATION = "error.configuration"
ERROR_SECURITY = "error.security"
ERROR_UNEXPECTED = "error.unexpected"

ALLOWED_EVENT_PREFIXES = frozenset(
    {
        "command",
        "config.load",
        "config.write",
        "context.resolve",
        "contract.compose",
        "contract.io",
        "profile.resolve",
        "profile.io",
        "profile.manage",
        "state.io",
        "resolution",
        "projection.validate",
        "projection.render",
        "variables.mutate",
        "binding.mutate",
        "vault",
        "run.exec",
        "subprocess.exec",
        "error",
        "error.handled",
        "error.unhandled",
    }
)


def event_prefix(event: str) -> str:
    """Return the stable family prefix for one event name."""
    if event in {ERROR_HANDLED, ERROR_UNHANDLED}:
        return event
    if event.startswith("error."):
        return "error"
    return event.rsplit(".", 1)[0]


def validate_event_name(event: str) -> None:
    """Reject events outside the allowed observable taxonomy."""
    prefix = event_prefix(event)
    if prefix not in ALLOWED_EVENT_PREFIXES:
        raise ValueError(f"Unsupported observability event prefix: {prefix}")
