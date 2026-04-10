"""Shared context helpers."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from envctl.config.loader import load_config
from envctl.domain.app_config import AppConfig
from envctl.domain.project import ProjectContext
from envctl.observability.timing import observe_span
from envctl.repository.project_context import build_project_context, persist_project_binding
from envctl.utils.project_ids import new_project_id

if TYPE_CHECKING:
    from envctl.vault_crypto import VaultCrypto


def load_configured_vault_crypto(
    config: AppConfig,
    context: ProjectContext,
) -> VaultCrypto | None:
    """Return the configured vault crypto layer for the current project."""
    if not config.encryption_enabled:
        return None

    from envctl.vault_crypto import VaultCrypto

    protected_paths = [context.vault_values_path]
    profiles_dir = context.vault_project_dir / "profiles"
    if profiles_dir.exists():
        protected_paths.extend(sorted(profiles_dir.glob("*.env")))

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
    span_fields: dict[str, Any] = {
        "persist_binding": persist_binding,
        "has_project_name": project_name is not None,
    }
    with observe_span(
        "context.resolve",
        module=__name__,
        operation="load_project_context",
        fields=span_fields,
    ):
        config = load_config()
        context = build_project_context(config, project_name=project_name)
        context = _with_crypto(context, load_configured_vault_crypto(config, context))

        if persist_binding:
            if context.binding_source == "derived":
                context = replace(context, project_id=new_project_id())
                span_fields["created"] = True

            context = persist_project_binding(config, context)
            span_fields["updated"] = True
            context = _with_crypto(context, load_configured_vault_crypto(config, context))

        span_fields["project_id"] = context.project_id
        span_fields["binding_source"] = context.binding_source
        span_fields["warning_count"] = len(context.runtime_warnings)
        span_fields["encryption_enabled"] = config.encryption_enabled
        span_fields["has_runtime_warnings"] = bool(context.runtime_warnings)
        span_fields["runtime_warning_count"] = len(context.runtime_warnings)
    return config, context
