"""Contract domain models."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class VariableSpec:
    """Single variable declaration in the contract."""

    name: str
    type: str = "string"
    required: bool = True
    description: str = ""
    sensitive: bool = True
    default: str | int | bool | None = None
    provider: str | None = None
    example: str | None = None
    pattern: str | None = None
    choices: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Contract:
    """Repository environment contract."""

    version: int
    variables: dict[str, VariableSpec]
