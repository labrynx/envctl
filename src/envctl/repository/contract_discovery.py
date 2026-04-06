"""Root contract discovery helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from envctl.constants import LEGACY_CONTRACT_FILENAME, PRIMARY_CONTRACT_FILENAME
from envctl.domain.diagnostics import CommandWarning
from envctl.errors import ContractError
from envctl.services.error_diagnostics import ContractDiagnostics


@dataclass(frozen=True)
class RootContractDiscoveryResult:
    """Resolved root contract path with non-fatal discovery warnings."""

    path: Path
    warnings: tuple[CommandWarning, ...] = ()


def discover_root_contract_path(repo_root: Path) -> RootContractDiscoveryResult:
    """Discover the root contract at the repository root."""
    primary = repo_root / PRIMARY_CONTRACT_FILENAME
    legacy = repo_root / LEGACY_CONTRACT_FILENAME

    if primary.exists() and legacy.exists():
        return RootContractDiscoveryResult(
            path=primary,
            warnings=(
                CommandWarning(
                    kind="dual_root_contract",
                    message=(
                        "Both .envctl.yaml and .envctl.schema.yaml were found at the "
                        "repository root. envctl will use .envctl.yaml as the main project "
                        "contract. .envctl.schema.yaml is treated as a legacy contract and "
                        "should be migrated or removed."
                    ),
                ),
            ),
        )
    if primary.exists():
        return RootContractDiscoveryResult(path=primary)
    if legacy.exists():
        return RootContractDiscoveryResult(path=legacy)

    raise ContractError(
        "Main envctl contract not found at repository root.",
        diagnostics=ContractDiagnostics(
            category="root_contract_not_found",
            path=repo_root,
            suggested_actions=(
                "create .envctl.yaml",
                "or restore .envctl.schema.yaml",
            ),
        ),
    )
