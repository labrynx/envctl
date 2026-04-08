"""Sync service."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.projection_rendering import render_dotenv
from envctl.domain.deprecations import ContractDeprecationWarning
from envctl.domain.project import ProjectContext
from envctl.domain.selection import ContractSelection
from envctl.errors import ExecutionError
from envctl.services.context_service import load_project_context
from envctl.services.projection_validation import resolve_projectable_environment
from envctl.services.selection_filtering import (
    build_variable_groups,
    filter_projection_values,
)
from envctl.utils.atomic import write_text_atomic
from envctl.utils.logging import get_logger
from envctl.utils.project_paths import build_repo_sync_env_path, normalize_profile_name

logger = get_logger(__name__)


def run_sync(
    active_profile: str | None = None,
    *,
    output_path: Path | None = None,
    selection: ContractSelection | None = None,
) -> tuple[ProjectContext, str, Path, tuple[ContractDeprecationWarning, ...]]:
    """Materialize the resolved environment into the repository env file."""
    _config, context = load_project_context()
    resolved_profile = normalize_profile_name(active_profile)
    logger.debug(
        "Running sync",
        extra={
            "active_profile": resolved_profile,
            "selection": selection.describe() if selection is not None else "full contract",
            "repo_root": context.repo_root,
        },
    )

    contract, report, warnings = resolve_projectable_environment(
        context,
        active_profile=resolved_profile,
        selection=selection,
        operation="sync",
    )

    values = filter_projection_values(
        {key: item.value for key, item in sorted(report.values.items())},
        contract,
        selection=selection,
    )

    rendered = render_dotenv(
        values,
        include_header=True,
        variable_groups=build_variable_groups(contract, values),
    )
    target_path = output_path or build_repo_sync_env_path(context.repo_root, resolved_profile)
    logger.info(
        "Writing synced environment file",
        extra={
            "active_profile": resolved_profile,
            "target_path": target_path,
            "resolved_key_count": len(values),
        },
    )

    try:
        write_text_atomic(target_path, rendered)
    except IsADirectoryError as exc:
        raise ExecutionError(f"Output path must be a file, not a directory: {target_path}") from exc
    except OSError as exc:
        raise ExecutionError(
            f"Could not write synced environment file: {target_path}: {exc.strerror or exc}"
        ) from exc
    logger.info(
        "Synced environment file written",
        extra={
            "active_profile": resolved_profile,
            "target_path": target_path,
            "resolved_key_count": len(values),
        },
    )

    return context, resolved_profile, target_path, warnings
