"""Output builders for inspect-style commands."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from envctl.cli.presenters.common import bullet_item, field_item, raw_item, section
from envctl.cli.presenters.models import CommandOutput, OutputItem
from envctl.cli.presenters.payloads import (
    build_command_warnings_payload,
    build_contract_selection_payload,
    build_diagnostic_summary_payload,
    build_project_context_payload,
    build_resolved_value_payload,
)
from envctl.domain.diagnostics import (
    DiagnosticProblem,
    InspectContractGraph,
    InspectKeyResult,
    InspectResult,
)
from envctl.domain.resolution import ResolvedValue
from envctl.utils.masking import mask_value


def _format_resolved_value(item: ResolvedValue) -> str:
    """Format one resolved value for human-readable output."""
    if item.value == "":
        return "[missing]"
    return str(mask_value(item.value) if item.masked else item.value)


def _build_problem_payload(problem: DiagnosticProblem) -> dict[str, Any]:
    """Build one diagnostic problem payload."""
    return {
        "key": problem.key,
        "kind": problem.kind,
        "message": problem.message,
        "actions": list(problem.actions),
    }


def _build_contract_graph_payload(graph: InspectContractGraph) -> dict[str, Any]:
    """Build one inspect contract graph payload."""
    return {
        "root_path": str(graph.root_path),
        "contract_paths": [str(path) for path in graph.contract_paths],
        "contracts_total": graph.contracts_total,
        "variables_total": graph.variables_total,
        "sets_total": graph.sets_total,
        "groups_total": graph.groups_total,
        "import_graph": {
            str(path): [str(child) for child in children]
            for path, children in graph.import_graph.items()
        },
        "declared_in": {key: str(path) for key, path in graph.declared_in.items()},
        "sets_index": {key: list(value) for key, value in graph.sets_index.items()},
        "groups_index": {key: list(value) for key, value in graph.groups_index.items()},
    }


def _build_variables_section(result: InspectResult) -> list[OutputItem]:
    """Build section items for resolved variables."""
    if not result.variables:
        return [raw_item("None")]

    items: list[OutputItem] = []
    for item in result.variables:
        suffixes: list[str] = []

        if item.expansion_status == "expanded":
            refs = ", ".join(item.expansion_refs)
            suffixes.append(f"expanded{': ' + refs if refs else ''}")
        elif item.expansion_status == "error" and item.expansion_error is not None:
            suffixes.append(f"expansion error: {item.expansion_error.detail}")

        if item.detail:
            suffixes.append(item.detail)

        declared_in = result.contract_graph.declared_in.get(item.key)
        if declared_in is not None:
            suffixes.append(f"declared in {declared_in}")

        suffix = f" — {' — '.join(suffixes)}" if suffixes else ""
        items.append(
            bullet_item(f"{item.key} = {_format_resolved_value(item)} ({item.source}){suffix}")
        )

    return items


def _build_problem_section(problems: Sequence[DiagnosticProblem]) -> list[OutputItem]:
    """Build section items for inspect problems."""
    if not problems:
        return [raw_item("None")]

    items: list[OutputItem] = []
    for problem in problems:
        items.append(bullet_item(f"{problem.key}: {problem.message}"))
        items.extend(raw_item(f"    action: {action}") for action in problem.actions)
    return items


def _build_contracts_items(result: InspectResult) -> list[OutputItem]:
    """Build section items for resolved contracts."""
    items: list[OutputItem] = [field_item("root", str(result.contract_graph.root_path))]

    if not result.contract_graph.contract_paths:
        items.append(raw_item("None"))
        return items

    for path in result.contract_graph.contract_paths:
        items.append(bullet_item(str(path)))
        children = result.contract_graph.import_graph.get(path, ())
        items.extend(raw_item(f"    imports: {child}") for child in children)

    return items


def _build_named_index_items(index: Mapping[str, Sequence[str]]) -> list[OutputItem]:
    """Build one summary list for sets/groups style indexes."""
    if not index:
        return [raw_item("None")]

    return [bullet_item(f"{name} ({len(keys)})") for name, keys in index.items()]


def _build_named_members_items(values: Sequence[str]) -> list[OutputItem]:
    """Build one member list for a selected set/group."""
    if not values:
        return [raw_item("None")]

    return [bullet_item(value) for value in values]


def build_inspect_output(result: InspectResult) -> CommandOutput:
    """Build one unified output model for ``inspect``."""
    sections = [
        section(
            "Project",
            field_item("repo_root", str(result.project.repo_root)),
            field_item("project_slug", result.project.project_slug),
            field_item("project_id", result.project.project_id),
            field_item("binding", result.project.binding_source),
            field_item("vault_dir", str(result.project.vault_project_dir)),
        ),
        section(
            "Contract composition",
            field_item("root", str(result.contract_graph.root_path)),
            field_item("contracts", str(result.contract_graph.contracts_total)),
            field_item("variables", str(result.contract_graph.variables_total)),
            field_item("sets", str(result.contract_graph.sets_total)),
            field_item("groups", str(result.contract_graph.groups_total)),
            raw_item("Resolved contracts:"),
            *(bullet_item(str(path)) for path in result.contract_graph.contract_paths),
        ),
        section(
            "Runtime",
            field_item("profile", result.active_profile),
            field_item("scope", result.selection.describe()),
            field_item("contract", result.contract_path),
            field_item("values", result.values_path),
        ),
        section(
            "Summary",
            field_item("total", str(result.summary.total)),
            field_item("valid", str(result.summary.valid)),
            field_item("invalid", str(result.summary.invalid)),
            field_item("unknown", str(result.summary.unknown)),
        ),
        build_contract_sets_summary_output(result).sections[0],
        build_contract_groups_summary_output(result).sections[0],
        section("Variables", *_build_variables_section(result)),
    ]

    if result.problems:
        sections.append(section("Problems", *_build_problem_section(result.problems)))

    return CommandOutput(
        sections=sections,
        metadata={
            "kind": "inspect",
            "project": {
                "repo_root": str(result.project.repo_root),
                "project_slug": result.project.project_slug,
                "project_id": result.project.project_id,
                "binding_source": result.project.binding_source,
                "vault_dir": str(result.project.vault_project_dir),
            },
            "runtime": {
                "active_profile": result.active_profile,
                "selection": build_contract_selection_payload(result.selection),
                "contract_path": result.contract_path,
                "values_path": result.values_path,
            },
            "contract_graph": _build_contract_graph_payload(result.contract_graph),
            "summary": build_diagnostic_summary_payload(result.summary),
            "variables": {
                item.key: build_resolved_value_payload(item) for item in result.variables
            },
            "problems": [_build_problem_payload(problem) for problem in result.problems],
            "warnings": build_command_warnings_payload(
                command_warnings=result.warnings,
            ),
            "context": build_project_context_payload(result.project),
        },
    )


def build_contracts_output(result: InspectResult) -> CommandOutput:
    """Build one unified output model for ``inspect contracts``."""
    return CommandOutput(
        title="Resolved contracts",
        sections=[section("Contracts", *_build_contracts_items(result))],
        metadata={
            "kind": "inspect_contracts",
            "contract_graph": _build_contract_graph_payload(result.contract_graph),
        },
    )


def build_contract_sets_summary_output(result: InspectResult) -> CommandOutput:
    """Build one unified output model for contract sets summary."""
    return CommandOutput(
        sections=[
            section(
                "Sets",
                *_build_named_index_items(result.contract_graph.sets_index),
            )
        ],
        metadata={
            "kind": "inspect_sets_summary",
            "sets_index": {
                name: list(keys) for name, keys in result.contract_graph.sets_index.items()
            },
        },
    )


def build_contract_set_output(result: InspectResult, name: str) -> CommandOutput:
    """Build one unified output model for one selected contract set."""
    keys = result.contract_graph.sets_index[name]

    return CommandOutput(
        title=f"Set: {name}",
        sections=[section("Set", *_build_named_members_items(keys))],
        metadata={
            "kind": "inspect_set",
            "name": name,
            "keys": list(keys),
        },
    )


def build_contract_groups_summary_output(result: InspectResult) -> CommandOutput:
    """Build one unified output model for contract groups summary."""
    return CommandOutput(
        sections=[
            section(
                "Groups",
                *_build_named_index_items(result.contract_graph.groups_index),
            )
        ],
        metadata={
            "kind": "inspect_groups_summary",
            "groups_index": {
                name: list(keys) for name, keys in result.contract_graph.groups_index.items()
            },
        },
    )


def build_contract_group_output(result: InspectResult, name: str) -> CommandOutput:
    """Build one unified output model for one selected contract group."""
    keys = result.contract_graph.groups_index[name]

    return CommandOutput(
        title=f"Group: {name}",
        sections=[section("Group", *_build_named_members_items(keys))],
        metadata={
            "kind": "inspect_group",
            "name": name,
            "keys": list(keys),
        },
    )


def build_inspect_key_output(result: InspectKeyResult) -> CommandOutput:
    """Build one unified output model for ``inspect KEY``."""
    item = result.item

    sections = [
        section(
            "Variable",
            field_item("key", item.key),
            field_item("status", "valid" if item.valid else "invalid"),
            field_item("source", item.source),
            field_item("sensitive", "yes" if result.sensitive else "no"),
            field_item("value", _format_resolved_value(item)),
            *([field_item("detail", item.detail)] if item.detail else []),
        ),
        section(
            "Contract",
            field_item("declared_in", str(result.declared_in)),
            field_item("type", result.contract_type),
            field_item("format", result.contract_format or "none"),
            field_item("sets", ", ".join(result.sets) if result.sets else "none"),
            field_item("groups", ", ".join(result.groups) if result.groups else "none"),
            field_item("default", "none" if result.default is None else str(result.default)),
        ),
        section(
            "Resolution",
            field_item("expanded", "yes" if item.expansion_status == "expanded" else "no"),
            *(
                [field_item("expansion_refs", ", ".join(item.expansion_refs))]
                if item.expansion_refs
                else []
            ),
            *(
                [field_item("expansion_error", item.expansion_error.detail)]
                if item.expansion_error is not None
                else []
            ),
        ),
    ]

    return CommandOutput(
        sections=sections,
        metadata={
            "kind": "inspect_key",
            "active_profile": result.active_profile,
            "context": build_project_context_payload(result.project),
            "item": build_resolved_value_payload(result.item),
            "contract": {
                "declared_in": str(result.declared_in),
                "type": result.contract_type,
                "format": result.contract_format,
                "sets": list(result.sets),
                "groups": list(result.groups),
                "default": result.default,
                "sensitive": result.sensitive,
            },
        },
    )
