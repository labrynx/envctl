"""Contract selection scope models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

SelectionMode = Literal["full", "group", "set", "var"]

_MUTUAL_EXCLUSIVITY_MESSAGE = (
    "Contract scope selectors are mutually exclusive: "
    "--set, --group, and --var cannot be used together."
)


@dataclass(frozen=True)
class ContractSelection:
    """Normalized contract selection scope."""

    mode: SelectionMode = "full"
    group: str | None = None
    set_name: str | None = None
    variable: str | None = None

    @classmethod
    def from_selectors(
        cls,
        *,
        group: str | None = None,
        set_name: str | None = None,
        variable: str | None = None,
    ) -> ContractSelection:
        """Build one normalized selection from optional CLI selectors."""
        normalized_group = _normalize_optional_selector(group)
        normalized_set = _normalize_optional_selector(set_name)
        normalized_var = _normalize_optional_selector(variable)

        active = [
            name
            for name, value in (
                ("group", normalized_group),
                ("set", normalized_set),
                ("var", normalized_var),
            )
            if value is not None
        ]
        if len(active) > 1:
            raise ValueError(_MUTUAL_EXCLUSIVITY_MESSAGE)

        if normalized_group is not None:
            return cls(mode="group", group=normalized_group)
        if normalized_set is not None:
            return cls(mode="set", set_name=normalized_set)
        if normalized_var is not None:
            return cls(mode="var", variable=normalized_var)
        return cls()

    def describe(self) -> str:
        """Return a compact human-readable scope label."""
        if self.mode == "group":
            return f"group={self.group}"
        if self.mode == "set":
            return f"set={self.set_name}"
        if self.mode == "var":
            return f"var={self.variable}"
        return "full contract"


def _normalize_optional_selector(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def full_selection() -> ContractSelection:
    return ContractSelection()


def group_selection(name: str) -> ContractSelection:
    return ContractSelection.from_selectors(group=name)


def set_selection(name: str) -> ContractSelection:
    return ContractSelection.from_selectors(set_name=name)


def var_selection(name: str) -> ContractSelection:
    return ContractSelection.from_selectors(variable=name)


def get_selection_exclusivity_message() -> str:
    return _MUTUAL_EXCLUSIVITY_MESSAGE
