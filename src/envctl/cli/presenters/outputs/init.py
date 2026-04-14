from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from envctl.cli.presenters.models import CommandOutput
from envctl.cli.presenters.outputs.actions import build_init_output as build_actions_init_output


@dataclass(frozen=True)
class _InitResultAdapter:
    contract_created: bool
    contract_template: str | None
    contract_skipped: bool
    hooks_installed: bool
    hooks_reason: Any
    runtime_warnings: tuple[str, ...]


def build_init_output(context: Any, init_result: Any) -> CommandOutput:
    """Compatibility adapter for legacy imports.

    Prefer importing `build_init_output` from `outputs.actions`.
    """
    contract_path = getattr(context, "repo_contract_path", None)
    if contract_path is None:
        return CommandOutput(
            metadata={
                "kind": "init",
                "project": {
                    "key": getattr(context, "project_key", None),
                    "id": getattr(context, "project_id", None),
                    "display_name": getattr(context, "display_name", None),
                },
                "repository": {
                    "root": str(getattr(context, "repo_root", "")),
                    "binding_source": getattr(context, "binding_source", None),
                },
                "vault": {
                    "dir": str(getattr(context, "vault_project_dir", "")),
                    "values_path": str(getattr(context, "vault_values_path", "")),
                    "state_path": str(getattr(context, "vault_state_path", "")),
                },
                "result": {
                    "contract_created": getattr(init_result, "contract_created", False),
                    "contract_template": getattr(init_result, "contract_template", None),
                    "contract_skipped": getattr(init_result, "contract_skipped", False),
                    "hooks_installed": getattr(init_result, "hooks_installed", False),
                    "hooks_reason": (
                        getattr(getattr(init_result, "hooks_reason", None), "value", None)
                    ),
                    "runtime_warnings": list(getattr(init_result, "runtime_warnings", ())),
                },
            }
        )

    adapted_result = _InitResultAdapter(
        contract_created=getattr(init_result, "contract_created", False),
        contract_template=getattr(init_result, "contract_template", None),
        contract_skipped=getattr(init_result, "contract_skipped", False),
        hooks_installed=getattr(init_result, "hooks_installed", False),
        hooks_reason=getattr(init_result, "hooks_reason", None),
        runtime_warnings=tuple(getattr(init_result, "runtime_warnings", ())),
    )

    return build_actions_init_output(
        project_key=getattr(context, "project_key"),
        binding_source=getattr(context, "binding_source"),
        repo_root=getattr(context, "repo_root"),
        contract_path=contract_path,
        vault_dir=getattr(context, "vault_project_dir"),
        vault_values_path=getattr(context, "vault_values_path"),
        vault_state_path=getattr(context, "vault_state_path"),
        init_result=adapted_result,
        display_name=getattr(context, "display_name"),
    )