"""Operation result models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AddResult:
    """Result of adding a key to vault and contract."""

    key: str
    value_written: bool
    contract_created: bool
    contract_updated: bool
    contract_entry_created: bool
    declared_in_contract: bool
    inferred_spec: dict[str, Any] | None


@dataclass(frozen=True)
class SetResult:
    """Result of setting a key in the local vault only."""

    key: str
    created: bool
    updated: bool
    declared_in_contract: bool


@dataclass(frozen=True)
class UnsetResult:
    """Result of removing a key from the local vault only."""

    key: str
    removed_from_vault: bool
    declared_in_contract: bool


@dataclass(frozen=True)
class RemoveResult:
    """Result of removing a key from vault and contract."""

    key: str
    removed_from_vault: bool
    removed_from_contract: bool


@dataclass(frozen=True)
class EditResult:
    """Result of editing the local vault file."""

    path: Path
    created: bool


@dataclass(frozen=True)
class VaultCheckResult:
    """Result of checking the vault artifact."""

    path: Path
    exists: bool
    parseable: bool
    private_permissions: bool
    key_count: int


@dataclass(frozen=True)
class VaultShowResult:
    """Result of showing the vault artifact."""

    path: Path
    exists: bool
    values: dict[str, str]


@dataclass(frozen=True)
class VaultPruneResult:
    """Result of pruning unknown keys from the vault."""

    path: Path
    removed_keys: tuple[str, ...]
    kept_keys: int
