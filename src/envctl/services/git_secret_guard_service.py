"""Detect staged envctl secrets before they reach Git history."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from envctl.adapters.git import is_git_repository, list_staged_paths, read_staged_file
from envctl.constants import MASTER_KEY_FORMAT_VERSION, VAULT_ENCRYPTION_FORMAT_VERSION
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.vault_crypto import MasterKeyMaterial, parse_master_key_material

_MAX_INSPECTED_BYTES = 512 * 1024
_VAULT_PREFIX = f"{VAULT_ENCRYPTION_FORMAT_VERSION}:".encode()
_MASTER_KEY_PREFIX = f"{MASTER_KEY_FORMAT_VERSION}:".encode()


@dataclass(frozen=True)
class GitSecretFinding:
    """One staged secret finding."""

    path: Path
    kind: str
    message: str
    actions: tuple[str, ...]


@dataclass(frozen=True)
class GitSecretGuardResult:
    """Structured staged-secret scan result."""

    scanned_paths: tuple[Path, ...]
    findings: tuple[GitSecretFinding, ...]

    @property
    def ok(self) -> bool:
        return not self.findings


def run_git_secret_guard(context: ProjectContext) -> GitSecretGuardResult:
    """Scan the staged Git index for envctl-specific secrets."""
    if not is_git_repository(context.repo_root):
        raise ExecutionError("The current project is not inside a Git repository.")

    staged_paths = list_staged_paths(context.repo_root)
    legacy_key_material = _load_legacy_project_key_material(context)
    findings: list[GitSecretFinding] = []

    for path in staged_paths:
        payload = read_staged_file(context.repo_root, path)
        findings.extend(
            _scan_staged_payload(path, payload, legacy_key_material=legacy_key_material)
        )

    return GitSecretGuardResult(scanned_paths=staged_paths, findings=tuple(findings))


def _load_legacy_project_key_material(context: ProjectContext) -> MasterKeyMaterial | None:
    if not context.vault_key_path.exists():
        return None

    try:
        material = parse_master_key_material(context.vault_key_path.read_bytes())
    except ExecutionError:
        return None

    return material if material.is_legacy else None


def _scan_staged_payload(
    path: Path,
    payload: bytes,
    *,
    legacy_key_material: MasterKeyMaterial | None,
) -> list[GitSecretFinding]:
    findings: list[GitSecretFinding] = []
    sample = payload[:_MAX_INSPECTED_BYTES]

    if sample.startswith(_VAULT_PREFIX):
        findings.append(
            GitSecretFinding(
                path=path,
                kind="vault_payload",
                message="Staged content contains an envctl encrypted vault payload.",
                actions=_build_actions(path),
            )
        )

    if sample.startswith(_MASTER_KEY_PREFIX):
        findings.append(
            GitSecretFinding(
                path=path,
                kind="master_key",
                message="Staged content contains an envctl master key in canonical format.",
                actions=_build_actions(path, rotate_hint=True),
            )
        )

    if legacy_key_material is not None and sample.strip() == legacy_key_material.key_bytes:
        findings.append(
            GitSecretFinding(
                path=path,
                kind="legacy_master_key",
                message="Staged content matches the current project's legacy envctl master key.",
                actions=_build_actions(path, rotate_hint=True),
            )
        )

    return findings


def _build_actions(path: Path, *, rotate_hint: bool = False) -> tuple[str, ...]:
    actions = [
        f"git restore --staged -- '{path.as_posix()}'",
        "move the secret outside the repository",
    ]
    if rotate_hint:
        actions.append("rotate the key if it was already exposed")
    return tuple(actions)
