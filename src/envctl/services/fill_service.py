"""Fill service."""

from __future__ import annotations

from envctl.adapters.dotenv import dump_env, load_env_file
from envctl.domain.project import ProjectContext, PromptFn
from envctl.services.context_service import load_project_context
from envctl.services.resolution_service import load_contract_for_context, resolve_environment
from envctl.utils.atomic import write_text_atomic
from envctl.utils.permissions import ensure_private_file_permissions


def run_fill(prompt: PromptFn) -> tuple[ProjectContext, list[str]]:
    """Interactively fill missing required values."""
    _config, context = load_project_context()
    contract = load_contract_for_context(context)
    report = resolve_environment(context, contract)
    data = load_env_file(context.vault_values_path)
    changed: list[str] = []

    for key in report.missing_required:
        spec = contract.variables[key]
        default_value = str(spec.default) if spec.default is not None else None
        question = spec.description or f"Provide a value for {key}"
        answer = prompt(f"{key}: {question}", spec.sensitive, default_value).strip()
        if not answer and default_value is not None:
            answer = default_value
        if not answer:
            continue
        data[key] = answer
        changed.append(key)

    if changed:
        write_text_atomic(context.vault_values_path, dump_env(data))
        ensure_private_file_permissions(context.vault_values_path)

    return context, changed
