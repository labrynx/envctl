from __future__ import annotations

from pathlib import Path

from envctl.utils.project_paths import (
    build_profile_env_path,
    build_profiles_dir,
    is_local_profile,
    normalize_profile_name,
)


def test_normalize_profile_name_falls_back_to_local() -> None:
    assert normalize_profile_name(None) == "local"
    assert normalize_profile_name("") == "local"
    assert normalize_profile_name("   ") == "local"


def test_normalize_profile_name_normalizes_case_and_spaces() -> None:
    assert normalize_profile_name("  Staging  ") == "staging"


def test_is_local_profile_identifies_local() -> None:
    assert is_local_profile(None) is True
    assert is_local_profile("local") is True
    assert is_local_profile("LOCAL") is True
    assert is_local_profile("staging") is False


def test_build_profile_env_path_returns_legacy_values_path_for_local() -> None:
    vault_project_dir = Path("/tmp/vault/projects/demo--prj_aaaaaaaaaaaaaaaa")

    assert build_profile_env_path(vault_project_dir, "local") == vault_project_dir / "values.env"


def test_build_profile_env_path_returns_profiles_file_for_explicit_profiles() -> None:
    vault_project_dir = Path("/tmp/vault/projects/demo--prj_aaaaaaaaaaaaaaaa")

    assert build_profiles_dir(vault_project_dir) == vault_project_dir / "profiles"
    assert build_profile_env_path(vault_project_dir, "staging") == (
        vault_project_dir / "profiles" / "staging.env"
    )
