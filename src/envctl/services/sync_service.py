"""Sync service."""

from __future__ import annotations

from envctl.constants import MATERIALIZED_ENV_HEADER
from envctl.domain.project import ProjectContext
from envctl.domain.resolution import ResolutionReport
from envctl.errors import ValidationError
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.atomic import write_text_atomic
from envctl.utils.dotenv import dump_env


def run_sync() -> tuple[ProjectContext, ResolutionReport]:
    """Materialize the resolved environment into the repository env file."""
    _config, context = load_project_context()
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract)

    if not report.is_valid:
        raise ValidationError("Cannot sync because the resolved environment is invalid")

    plain = {key: value.value for key, value in report.values.items()}
    write_text_atomic(context.repo_env_path, dump_env(plain, header=MATERIALIZED_ENV_HEADER))
    return context, report
