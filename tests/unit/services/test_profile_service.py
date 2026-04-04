from __future__ import annotations

import pytest

import envctl.services.profile_service as profile_service
from envctl.errors import ExecutionError, ValidationError
from tests.support.contexts import make_project_context


def test_run_profile_list_includes_local_and_explicit_profiles(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()

    monkeypatch.setattr(
        profile_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        profile_service,
        "list_explicit_profiles",
        lambda _context: ("dev", "staging"),
    )

    _context, result = profile_service.run_profile_list("staging")

    assert result.active_profile == "staging"
    assert result.profiles == ("local", "dev", "staging")


def test_run_profile_create_creates_missing_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    written: dict[str, object] = {}

    monkeypatch.setattr(
        profile_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        profile_service,
        "resolve_profile_path",
        lambda context, profile: ("dev", context.vault_project_dir / "profiles" / "dev.env"),
    )
    monkeypatch.setattr(
        profile_service,
        "write_profile_values",
        lambda context, profile, values: (
            profile,
            written.update(
                {
                    "path": context.vault_project_dir / "profiles" / "dev.env",
                    "values": values,
                }
            )
            or context.vault_project_dir / "profiles" / "dev.env",
        ),
    )

    _context, result = profile_service.run_profile_create("dev")

    assert result.profile == "dev"
    assert result.created is True
    assert str(written["path"]).endswith("/profiles/dev.env")
    assert written["values"] == {}


def test_run_profile_copy_copies_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    written: dict[str, object] = {}

    monkeypatch.setattr(
        profile_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        profile_service,
        "load_profile_values",
        lambda context, profile: (
            profile,
            context.vault_project_dir / "profiles" / f"{profile}.env",
            {"APP_NAME": "demo", "PORT": "3000"},
        ),
    )
    monkeypatch.setattr(
        profile_service,
        "write_profile_values",
        lambda context, profile, values: (
            profile,
            written.update(
                {
                    "path": context.vault_project_dir / "profiles" / f"{profile}.env",
                    "values": values,
                }
            )
            or context.vault_project_dir / "profiles" / f"{profile}.env",
        ),
    )

    _context, result = profile_service.run_profile_copy("dev", "staging")

    assert result.source_profile == "dev"
    assert result.target_profile == "staging"
    assert result.copied_keys == 2
    assert written["values"] == {"APP_NAME": "demo", "PORT": "3000"}


def test_run_profile_copy_rejects_missing_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()

    monkeypatch.setattr(
        profile_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        profile_service,
        "load_profile_values",
        lambda context, profile: (
            profile,
            context.vault_project_dir / "profiles" / f"{profile}.env",
            {},
        ),
    )

    with pytest.raises(ExecutionError, match=r"Source profile does not exist"):
        profile_service.run_profile_copy("dev", "staging")


def test_run_profile_remove_rejects_local_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()

    monkeypatch.setattr(
        profile_service,
        "load_project_context",
        lambda: (object(), context),
    )

    with pytest.raises(ValidationError, match=r"implicit local profile"):
        profile_service.run_profile_remove("local")
