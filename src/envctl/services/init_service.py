"""Init service."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import ValidationError as PydanticValidationError

from envctl.adapters.dotenv import load_env_file
from envctl.adapters.git import get_local_git_config, is_git_repository, set_local_git_config
from envctl.constants import CONTRACT_VERSION, DEFAULT_ENV_EXAMPLE_FILENAME
from envctl.domain.contract_inference import infer_spec
from envctl.domain.operations import InitResult
from envctl.domain.project import ConfirmFn, ProjectContext
from envctl.repository.contract_repository import ensure_contract_metadata, load_contract_optional
from envctl.services.context_service import load_project_context
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir, ensure_file

InitContractMode = Literal["ask", "example", "starter", "skip"]
ResolvedInitContractMode = Literal["example", "starter", "skip"]

_HOOKS_DIRNAME = ".githooks"
_PRE_COMMIT_PATH = Path(_HOOKS_DIRNAME) / "pre-commit"
_HOOKS_PATH_CONFIG = "core.hooksPath"
_ENVCTL_HOOK_MARKER = "# managed-by: envctl"
_PRE_COMMIT_SCRIPT = "#!/bin/sh\nset -eu\n\n# managed-by: envctl\nenvctl guard secrets\n"
_GITIGNORE_ENTRY = "master.key"


def run_init(
    project_name: str | None = None,
    contract_mode: InitContractMode = "ask",
    confirm: ConfirmFn | None = None,
) -> tuple[ProjectContext, InitResult]:
    """Initialize the current project inside the local vault."""
    _config, context = load_project_context(
        project_name=project_name,
        persist_binding=True,
    )

    ensure_dir(context.vault_project_dir)
    ensure_file(context.vault_values_path, "")

    init_result = _ensure_contract(
        context=context,
        contract_mode=contract_mode,
        confirm=confirm,
    )
    git_guard_installed, git_guard_reason = _install_git_guard(context)
    _ensure_gitignore(context)

    return context, InitResult(
        contract_created=init_result.contract_created,
        contract_template=init_result.contract_template,
        contract_skipped=init_result.contract_skipped,
        git_guard_installed=git_guard_installed,
        git_guard_reason=git_guard_reason,
        runtime_warnings=tuple(warning.message for warning in context.runtime_warnings),
    )


def _ensure_contract(
    *,
    context: ProjectContext,
    contract_mode: InitContractMode,
    confirm: ConfirmFn | None,
) -> InitResult:
    """Create a contract when it does not exist yet."""
    existing_contract = load_contract_optional(context.repo_contract_path)
    if existing_contract is not None:
        updated_contract = ensure_contract_metadata(
            existing_contract,
            project_key=context.project_key,
            project_name=context.project_slug,
        )
        if updated_contract != existing_contract:
            _write_contract_payload(context, updated_contract.to_contract_payload())
        return InitResult(contract_created=False)

    resolved_mode = _resolve_contract_mode(
        context=context,
        contract_mode=contract_mode,
        confirm=confirm,
    )

    if resolved_mode == "skip":
        return InitResult(
            contract_created=False,
            contract_template=None,
            contract_skipped=True,
        )

    if resolved_mode == "example":
        contract_payload = _build_contract_from_example(context)
        _write_contract_payload(context, contract_payload)
        return InitResult(
            contract_created=True,
            contract_template="example",
        )

    contract_payload = _build_starter_contract(context)
    _write_contract_payload(context, contract_payload)
    return InitResult(
        contract_created=True,
        contract_template="starter",
    )


def _install_git_guard(context: ProjectContext) -> tuple[bool, str | None]:
    """Install the managed pre-commit hook when Git configuration is safe to change."""
    if not is_git_repository(context.repo_root):
        return False, None

    existing_hooks_path = get_local_git_config(context.repo_root, _HOOKS_PATH_CONFIG)
    if existing_hooks_path and existing_hooks_path != _HOOKS_DIRNAME:
        return (
            False,
            f"Git already uses core.hooksPath={existing_hooks_path}; envctl did not overwrite it.",
        )

    hook_path = context.repo_root / _PRE_COMMIT_PATH
    if hook_path.exists():
        content = hook_path.read_text(encoding="utf-8")
        if _ENVCTL_HOOK_MARKER not in content:
            return False, f"Existing hook at '{_PRE_COMMIT_PATH}' is not managed by envctl."

    hook_path.parent.mkdir(parents=True, exist_ok=True)
    write_text_atomic(hook_path, _PRE_COMMIT_SCRIPT, mode=0o755)
    set_local_git_config(context.repo_root, _HOOKS_PATH_CONFIG, _HOOKS_DIRNAME)
    return True, None


def _ensure_gitignore(context: ProjectContext) -> None:
    """Ensure sensitive envctl artifacts stay ignored by default."""
    gitignore_path = context.repo_root / ".gitignore"
    block = f"# envctl\n{_GITIGNORE_ENTRY}\n"
    if not gitignore_path.exists():
        write_text_atomic(gitignore_path, block)
        return

    lines = gitignore_path.read_text(encoding="utf-8").splitlines()
    if _GITIGNORE_ENTRY in lines:
        return

    content = gitignore_path.read_text(encoding="utf-8")
    if content and not content.endswith("\n"):
        content += "\n"
    content += block
    write_text_atomic(gitignore_path, content)


def _resolve_contract_mode(
    *,
    context: ProjectContext,
    contract_mode: InitContractMode,
    confirm: ConfirmFn | None,
) -> ResolvedInitContractMode:
    """Resolve the effective contract bootstrap mode."""
    if contract_mode == "example":
        return "example"
    if contract_mode == "starter":
        return "starter"
    if contract_mode == "skip":
        return "skip"

    env_example_path = context.repo_root / DEFAULT_ENV_EXAMPLE_FILENAME
    has_example = env_example_path.exists()

    if confirm is None:
        return "example" if has_example else "starter"

    if has_example and confirm(
        f"No contract file found. Create one from {DEFAULT_ENV_EXAMPLE_FILENAME}?",
        True,
    ):
        return "example"

    if confirm("Create a starter contract scaffold instead?", True):
        return "starter"

    return "skip"


def _write_contract_payload(context: ProjectContext, payload: dict[str, object]) -> None:
    """Write a contract payload to the repository."""
    content = yaml.safe_dump(payload, sort_keys=False, allow_unicode=True)
    write_text_atomic(context.repo_contract_path, content)


def _build_contract_from_example(context: ProjectContext) -> dict[str, object]:
    """Infer a contract from a repository .env.example file."""
    env_example_path = context.repo_root / DEFAULT_ENV_EXAMPLE_FILENAME
    example_values = load_env_file(env_example_path)

    if not example_values:
        return _build_starter_contract(context)

    variables: dict[str, dict[str, object]] = {}

    for key, raw_value in example_values.items():
        try:
            spec = infer_spec(key, raw_value)
        except (PydanticValidationError, ValueError, TypeError):
            continue
        variables[key] = spec.to_contract_payload()

    if not variables:
        return _build_starter_contract(context)

    return {
        "version": CONTRACT_VERSION,
        "meta": {
            "project_key": context.project_key,
            "project_name": context.project_slug,
        },
        "variables": variables,
    }


def _build_starter_contract(context: ProjectContext) -> dict[str, object]:
    """Create a small starter contract scaffold."""
    return {
        "version": CONTRACT_VERSION,
        "meta": {
            "project_key": context.project_key,
            "project_name": context.project_slug,
        },
        "variables": {
            "APP_NAME": {
                "type": "string",
                "required": True,
                "sensitive": False,
                "description": "Application name",
                "example": context.project_slug,
            },
            "PORT": {
                "type": "int",
                "required": True,
                "sensitive": False,
                "description": "Application port",
                "default": 3000,
            },
            "DATABASE_URL": {
                "type": "url",
                "required": True,
                "sensitive": True,
                "description": "Primary database connection URL",
                "example": "postgres://user:password@localhost:5432/app",
            },
            "DEBUG": {
                "type": "bool",
                "required": False,
                "sensitive": False,
                "description": "Debug mode",
                "default": False,
            },
        },
    }
