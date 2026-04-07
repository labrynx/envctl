"""Helpers for contract scope selection."""

from __future__ import annotations

from envctl.domain.contract import Contract
from envctl.domain.selection import ContractSelection
from envctl.errors import ContractError


def resolve_selected_variable_names(
    contract: Contract,
    selection: ContractSelection | None,
) -> tuple[str, ...]:
    """Resolve one normalized list of variable names for the active selection."""
    active_selection = selection or ContractSelection()

    if active_selection.mode == "full":
        return tuple(sorted(contract.variables))
    if active_selection.mode == "group":
        return resolve_variable_names_for_group(contract, active_selection.group or "")
    if active_selection.mode == "set":
        return resolve_variable_names_for_set(contract, active_selection.set_name or "")
    if active_selection.mode == "var":
        return resolve_variable_names_for_var(contract, active_selection.variable or "")

    raise ValueError(f"Unsupported selection mode: {active_selection.mode}")


def resolve_variable_names_for_group(contract: Contract, group_name: str) -> tuple[str, ...]:
    normalized_group = group_name.strip()
    if not normalized_group:
        raise ContractError("Group selector cannot be empty")

    matches = sorted(
        key
        for key, spec in contract.variables.items()
        if normalized_group in spec.normalized_groups
    )
    if not matches:
        raise ContractError(f"Unknown contract group: {normalized_group}")
    return tuple(matches)


def resolve_variable_names_for_var(contract: Contract, var_name: str) -> tuple[str, ...]:
    normalized_var = var_name.strip()
    if normalized_var not in contract.variables:
        raise ContractError(f"Unknown contract variable: {normalized_var}")
    return (normalized_var,)


def resolve_variable_names_for_set(contract: Contract, set_name: str) -> tuple[str, ...]:
    normalized_set = set_name.strip()
    if normalized_set not in contract.sets:
        raise ContractError(f"Unknown contract set: {normalized_set}")
    return _resolve_set_variable_names(contract, normalized_set, stack=())


def _resolve_set_variable_names(
    contract: Contract,
    set_name: str,
    *,
    stack: tuple[str, ...],
) -> tuple[str, ...]:
    if set_name in stack:
        cycle = " -> ".join((*stack, set_name))
        raise ContractError(f"Set resolution cycle detected: {cycle}")

    spec = contract.sets[set_name]
    names: set[str] = set(spec.variables)

    for group_name in spec.groups:
        names.update(
            key
            for key, variable in contract.variables.items()
            if group_name in variable.normalized_groups
        )

    for nested_set in spec.sets:
        names.update(_resolve_set_variable_names(contract, nested_set, stack=(*stack, set_name)))

    return tuple(sorted(names))
