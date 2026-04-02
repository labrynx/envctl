from __future__ import annotations

from pathlib import Path

import pytest

from envctl.errors import ExecutionError
from envctl.repository.profile_repository import (
    list_explicit_profiles,
    list_persisted_profiles,
    load_profile_values,
    require_persisted_profile,
    resolve_profile_path,
    write_profile_values,
)
from tests.support.contexts import make_project_context


def test_resolve_profile_path_uses_values_env_for_local() -> None:
    context = make_project_context(vault_values_path="/tmp/demo/values.env")

    profile, path = resolve_profile_path(context, "local")

    assert profile == "local"
    assert path == context.vault_values_path


def test_require_persisted_profile_rejects_missing_explicit_profile() -> None:
    context = make_project_context()

    with pytest.raises(ExecutionError, match="Create it with 'envctl profile create staging'"):
        require_persisted_profile(context, "staging")


def test_list_persisted_profiles_reports_local_and_explicit_profiles(tmp_path: Path) -> None:
    context = make_project_context(
        vault_project_dir=tmp_path / "vault",
        vault_values_path=tmp_path / "vault" / "values.env",
    )
    context.vault_values_path.parent.mkdir(parents=True, exist_ok=True)
    context.vault_values_path.write_text("APP_NAME=demo\n", encoding="utf-8")
    profiles_dir = context.vault_project_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    (profiles_dir / "dev.env").write_text("APP_NAME=dev\n", encoding="utf-8")
    (profiles_dir / "staging.env").write_text("APP_NAME=staging\n", encoding="utf-8")

    assert list_explicit_profiles(context) == ("dev", "staging")
    assert list_persisted_profiles(context) == ("local", "dev", "staging")


def test_write_and_load_profile_values_for_explicit_profile(tmp_path: Path) -> None:
    context = make_project_context(
        vault_project_dir=tmp_path / "vault",
        vault_values_path=tmp_path / "vault" / "values.env",
    )
    profiles_dir = context.vault_project_dir / "profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)
    (profiles_dir / "dev.env").write_text("", encoding="utf-8")

    profile, written_path = write_profile_values(
        context,
        "dev",
        {"APP_NAME": "demo-dev"},
        require_existing_explicit=True,
    )
    loaded_profile, loaded_path, values = load_profile_values(
        context,
        "dev",
        require_existing_explicit=True,
    )

    assert profile == "dev"
    assert loaded_profile == "dev"
    assert written_path == loaded_path
    assert values == {"APP_NAME": "demo-dev"}
