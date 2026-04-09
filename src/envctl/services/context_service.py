"""Shared context helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from envctl.config.loader import load_config
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.observability import get_active_observability_context
from envctl.observability.events import (
    CONTEXT_RESOLVE_ERROR,
    CONTEXT_RESOLVE_FINISH,
    CONTEXT_RESOLVE_START,
)
from envctl.observability.recorder import duration_ms, record_event
from envctl.observability.timing import utcnow
from envctl.repository.project_context import build_project_context, persist_project_binding
from envctl.utils.logging import get_logger
from envctl.utils.project_ids import new_project_id

if TYPE_CHECKING:
    from envctl.vault_crypto import VaultCrypto


logger = get_logger(__name__)


def load_configured_vault_crypto(
    config: AppConfig,
    context: ProjectContext,
) -> VaultCrypto | None:
    """Return the configured vault crypto layer for the current project."""
    if not config.encryption_enabled:
        logger.debug(
            "Vault encryption disabled for project context",
            extra={"project_id": context.project_id},
        )
        return None

    from envctl.vault_crypto import VaultCrypto

    protected_paths = [context.vault_values_path]
    profiles_dir = context.vault_project_dir / "profiles"
    if profiles_dir.exists():
        protected_paths.extend(sorted(profiles_dir.glob("*.env")))

    logger.debug(
        "Preparing vault crypto for project context",
        extra={
            "project_id": context.project_id,
            "protected_path_count": len(protected_paths),
        },
    )
    return VaultCrypto.from_env_or_file(
        context.vault_key_path,
        protected_paths=protected_paths,
    )


def _with_crypto(context: ProjectContext, crypto: VaultCrypto | None) -> ProjectContext:
    """Attach vault crypto and runtime warnings to one project context."""
    return replace(
        context,
        vault_crypto=crypto,
        runtime_warnings=crypto.runtime_warnings if crypto is not None else (),
    )


def load_project_context(
    project_name: str | None = None,
    *,
    persist_binding: bool = False,
) -> tuple[AppConfig, ProjectContext]:
    """Load config and build the current project context."""
    started_at = utcnow()
    obs_context = get_active_observability_context()
    if obs_context is not None:
        record_event(
            obs_context,
            event=CONTEXT_RESOLVE_START,
            status="start",
            module=__name__,
            operation="load_project_context",
            fields={
                "persist_binding": persist_binding,
                "has_project_name": project_name is not None,
            },
        )
    logger.debug(
        "Loading project context",
        extra={
            "project_name": project_name or "-",
            "persist_binding": persist_binding,
        },
    )

    try:
        config = load_config()
        context = build_project_context(config, project_name=project_name)
    except Exception:
        if obs_context is not None:
            record_event(
                obs_context,
                event=CONTEXT_RESOLVE_ERROR,
                status="error",
                duration_ms=duration_ms(started_at),
                module=__name__,
                operation="load_project_context",
                fields={
                    "persist_binding": persist_binding,
                    "has_project_name": project_name is not None,
                },
            )
        raise
    logger.debug(
        "Built project context",
        extra={
            "project_id": context.project_id,
            "binding_source": context.binding_source,
            "repo_root": context.repo_root,
        },
    )
    context = _with_crypto(context, load_configured_vault_crypto(config, context))

    if context.runtime_warnings:
        logger.warning(
            "Project context has runtime warnings",
            extra={
                "project_id": context.project_id,
                "warning_count": len(context.runtime_warnings),
            },
        )

    if persist_binding:
        if context.binding_source == "derived":
            logger.debug("Project binding is derived; generating persistent project id")
            context = replace(context, project_id=new_project_id())

        context = persist_project_binding(config, context)
        logger.debug(
            "Persisted project binding",
            extra={
                "project_id": context.project_id,
                "binding_source": context.binding_source,
            },
        )
        context = _with_crypto(context, load_configured_vault_crypto(config, context))

    logger.debug(
        "Project context ready",
        extra={
            "project_id": context.project_id,
            "binding_source": context.binding_source,
            "encryption_enabled": config.encryption_enabled,
            "runtime_warning_count": len(context.runtime_warnings),
        },
    )
    if obs_context is not None:
        record_event(
            obs_context,
            event=CONTEXT_RESOLVE_FINISH,
            status="finish",
            duration_ms=duration_ms(started_at),
            module=__name__,
            operation="load_project_context",
            fields={
                "persist_binding": persist_binding,
                "has_runtime_warnings": bool(context.runtime_warnings),
                "runtime_warning_count": len(context.runtime_warnings),
            },
        )
    return config, context
