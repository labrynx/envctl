"""Operation result models."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from envctl.vault_crypto import VaultFileState

InitContractTemplate = Literal["example", "starter"] | None


@dataclass(frozen=True)
class InitResult:
    """Outcome of project initialization."""

    contract_created: bool
    contract_template: InitContractTemplate = None
    contract_skipped: bool = False


@dataclass(frozen=True)
class AddVariableRequest:
    """Request payload for adding or updating one variable."""

    key: str
    value: str
    override_type: str | None = None
    override_required: bool | None = None
    override_sensitive: bool | None = None
    override_description: str | None = None
    override_default: str | int | bool | None = None
    override_example: str | None = None
    override_format: str | None = None
    override_pattern: str | None = None
    override_choices: tuple[str, ...] | None = None


@dataclass(frozen=True)
class AddVariableResult:
    """Result of adding one variable to the contract and active profile."""

    key: str
    active_profile: str
    profile_path: Path
    value_written: bool
    contract_created: bool
    contract_updated: bool
    contract_entry_created: bool
    inferred_spec: dict[str, Any] | None
    inferred_fields_used: tuple[str, ...]


@dataclass(frozen=True)
class FillPlanItem:
    """Description of one missing required value to be collected by the CLI."""

    key: str
    description: str
    sensitive: bool
    default_value: str | None


@dataclass(frozen=True)
class RemovePlan:
    """Planned effects of removing one variable."""

    key: str
    declared_in_contract: bool
    present_in_active_profile: bool
    present_in_other_profiles: tuple[str, ...]
    absent_in_other_profiles: tuple[str, ...] = ()

    @property
    def requires_confirmation(self) -> bool:
        """Return whether the CLI should ask for confirmation."""
        return self.declared_in_contract


@dataclass(frozen=True)
class RemoveVariableResult:
    """Result of removing one variable globally."""

    key: str
    removed_from_contract: bool
    removed_from_profiles: tuple[str, ...]
    repo_contract_path: Path
    affected_paths: tuple[Path, ...]
    inspected_profiles: tuple[str, ...] = ()
    missing_from_profiles: tuple[str, ...] = ()


@dataclass(frozen=True)
class VaultEditResult:
    """Result of opening one profile vault file in the editor."""

    path: Path
    profile: str
    created: bool


@dataclass(frozen=True)
class VaultCheckResult:
    """Result of checking the vault artifact."""

    path: Path
    exists: bool
    parseable: bool
    private_permissions: bool
    key_count: int
    state: VaultFileState
    detail: str | None = None


@dataclass(frozen=True)
class VaultShowResult:
    """Result of showing the vault artifact."""

    path: Path
    exists: bool
    values: dict[str, str]
    state: VaultFileState
    detail: str | None = None


@dataclass(frozen=True)
class VaultPruneResult:
    """Result of pruning unknown keys from the vault."""

    path: Path
    removed_keys: tuple[str, ...]
    kept_keys: int


@dataclass(frozen=True)
class VaultEncryptResult:
    """Result of encrypting vault profile files."""

    encrypted_files: tuple[Path, ...]
    skipped_files: tuple[Path, ...]


@dataclass(frozen=True)
class VaultDecryptResult:
    """Result of decrypting vault profile files."""

    decrypted_files: tuple[Path, ...]
    skipped_files: tuple[Path, ...]


@dataclass(frozen=True)
class VaultAuditFileResult:
    """One audited vault file."""

    path: Path
    state: VaultFileState
    detail: str
    private_permissions: bool


@dataclass(frozen=True)
class VaultAuditProjectResult:
    """Audit summary for one project vault."""

    project_slug: str
    project_id: str
    key_path: Path
    key_exists: bool
    files: tuple[VaultAuditFileResult, ...]


@dataclass(frozen=True)
class BindResult:
    """Result of binding the current repository to an existing project id."""

    project_id: str
    changed: bool


@dataclass(frozen=True)
class UnbindResult:
    """Result of removing the local repo-to-vault binding."""

    removed: bool
    previous_project_id: str | None


@dataclass(frozen=True)
class RebindResult:
    """Result of rebinding the current checkout to a fresh project id."""

    previous_project_id: str | None
    new_project_id: str
    copied_values: bool


@dataclass(frozen=True)
class RepairResult:
    """Result of repairing local identity state."""

    status: str
    detail: str
    project_id: str | None = None


@dataclass(frozen=True)
class ProfileListResult:
    """List of available profiles for one project."""

    active_profile: str
    profiles: tuple[str, ...]


@dataclass(frozen=True)
class ProfileCreateResult:
    """Result of creating one profile."""

    profile: str
    path: Path
    created: bool


@dataclass(frozen=True)
class ProfileCopyResult:
    """Result of copying one profile into another."""

    source_profile: str
    target_profile: str
    source_path: Path
    target_path: Path
    copied_keys: int


@dataclass(frozen=True)
class ProfileRemoveResult:
    """Result of removing one explicit profile."""

    profile: str
    path: Path
    removed: bool


@dataclass(frozen=True)
class ProfilePathResult:
    """Resolved path for one profile."""

    profile: str
    path: Path


@dataclass(frozen=True)
class RunCommandResult:
    """Result of running one child command with the resolved environment."""

    active_profile: str
    exit_code: int
    warnings: tuple[str, ...] = ()
