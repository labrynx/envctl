"""Profile vault persistence helpers."""

from __future__ import annotations

from pathlib import Path

from envctl.adapters.dotenv import dump_env, load_env_file, parse_env_text
from envctl.constants import DEFAULT_PROFILE, DEFAULT_VALUES_FILENAME
from envctl.domain.project import ProjectContext
from envctl.errors import ExecutionError
from envctl.utils.atomic import write_text_atomic
from envctl.utils.filesystem import ensure_dir
from envctl.utils.project_paths import (
    build_profile_env_path,
    build_profiles_dir,
    is_local_profile,
    normalize_profile_name,
)
from envctl.vault_crypto import VaultCrypto


def _load_env_text(path: Path, *, context: ProjectContext, allow_plaintext: bool = True) -> str:
    """Read vault file content, decrypting when the context is encrypted."""
    if not path.exists():
        return ""

    if context.vault_crypto is not None:
        return context.vault_crypto.read_file(path, allow_plaintext=allow_plaintext)

    raw = path.read_bytes()
    if VaultCrypto.looks_encrypted(raw):
        raise ExecutionError(
            "Vault file is encrypted, but encryption is disabled. Enable encryption in config "
            "or run 'envctl vault decrypt' with the correct key first."
        )

    return raw.decode("utf-8")


def _write_env_text(path: Path, content: str, *, context: ProjectContext) -> None:
    """Write vault file content, encrypting when the context is encrypted."""
    if context.vault_crypto is not None:
        context.vault_crypto.write_encrypted_file(path, content)
    else:
        write_text_atomic(path, content)


def resolve_profile_path(
    context: ProjectContext,
    profile: str | None,
) -> tuple[str, Path]:
    """Resolve the normalized profile name and its backing vault file path."""
    resolved_profile = normalize_profile_name(profile)

    if is_local_profile(resolved_profile):
        return resolved_profile, context.vault_values_path

    return resolved_profile, build_profile_env_path(context.vault_project_dir, resolved_profile)


def require_persisted_profile(
    context: ProjectContext,
    profile: str | None,
) -> tuple[str, Path]:
    """Require the selected profile to exist when it is explicit.

    The implicit ``local`` profile stays virtual until first write.
    """
    resolved_profile, path = resolve_profile_path(context, profile)
    if is_local_profile(resolved_profile):
        return resolved_profile, path

    if not path.exists():
        raise ExecutionError(
            f"Profile does not exist: {resolved_profile}. "
            f"Create it with 'envctl profile create {resolved_profile}'."
        )

    return resolved_profile, path


def list_explicit_profiles(context: ProjectContext) -> tuple[str, ...]:
    """Return explicit profiles persisted in the vault."""
    profiles_dir = build_profiles_dir(context.vault_project_dir)
    if not profiles_dir.exists():
        return ()

    profiles: list[str] = []
    for item in sorted(profiles_dir.glob("*.env")):
        if item.is_file():
            profiles.append(item.stem)

    return tuple(profiles)


def list_persisted_profiles(context: ProjectContext) -> tuple[str, ...]:
    """Return every currently persisted profile."""
    profiles: list[str] = []
    if context.vault_values_path.exists():
        profiles.append(DEFAULT_PROFILE)

    profiles.extend(list_explicit_profiles(context))
    return tuple(profiles)


def load_local_profile_values_from_vault_dir(
    vault_project_dir: Path,
    *,
    crypto: object | None = None,
    key_path: Path | None = None,
) -> dict[str, str]:
    """Load the implicit local profile directly from one vault directory."""
    path = vault_project_dir / DEFAULT_VALUES_FILENAME
    context = ProjectContext(
        project_slug="vault",
        project_key="vault",
        project_id="vault",
        repo_root=vault_project_dir,
        repo_remote=None,
        binding_source="local",
        repo_env_path=vault_project_dir / ".env.local",
        repo_contract_path=vault_project_dir / ".envctl.yaml",
        vault_project_dir=vault_project_dir,
        vault_values_path=path,
        vault_state_path=vault_project_dir / "state.json",
        vault_key_path=key_path or (vault_project_dir / "master.key"),
        vault_crypto=crypto,  # type: ignore[arg-type]
    )
    return parse_env_text(_load_env_text(path, context=context))


def load_profile_values(
    context: ProjectContext,
    profile: str | None,
    *,
    require_existing_explicit: bool = False,
    allow_plaintext: bool = True,
) -> tuple[str, Path, dict[str, str]]:
    """Load values for one profile."""
    if require_existing_explicit:
        resolved_profile, path = require_persisted_profile(context, profile)
    else:
        resolved_profile, path = resolve_profile_path(context, profile)

    return (
        resolved_profile,
        path,
        parse_env_text(_load_env_text(path, context=context, allow_plaintext=allow_plaintext)),
    )


def write_profile_values(
    context: ProjectContext,
    profile: str | None,
    values: dict[str, str],
    *,
    require_existing_explicit: bool = False,
) -> tuple[str, Path]:
    """Persist values for one profile."""
    if require_existing_explicit:
        resolved_profile, path = require_persisted_profile(context, profile)
    else:
        resolved_profile, path = resolve_profile_path(context, profile)

    ensure_dir(path.parent)
    _write_env_text(path, dump_env(values), context=context)
    return resolved_profile, path


def remove_key_from_profile(
    context: ProjectContext,
    profile: str | None,
    key: str,
    *,
    require_existing_explicit: bool = False,
) -> tuple[str, Path, bool]:
    """Remove one key from one profile when present."""
    resolved_profile, path, values = load_profile_values(
        context,
        profile,
        require_existing_explicit=require_existing_explicit,
    )
    if key not in values:
        return resolved_profile, path, False

    values.pop(key, None)
    write_profile_values(
        context,
        resolved_profile,
        values,
        require_existing_explicit=require_existing_explicit,
    )
    return resolved_profile, path, True


__all__ = [
    "list_explicit_profiles",
    "list_persisted_profiles",
    "load_env_file",
    "load_local_profile_values_from_vault_dir",
    "load_profile_values",
    "remove_key_from_profile",
    "require_persisted_profile",
    "resolve_profile_path",
    "write_profile_values",
]
