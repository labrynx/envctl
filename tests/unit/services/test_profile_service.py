from __future__ import annotations

import logging
from pathlib import Path

import pytest

import envctl.services.profile_service as profile_service
from envctl.errors import ExecutionError, ValidationError
from tests.support.contexts import make_project_context
from tests.support.paths import normalize_path_str


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
    written_path: Path | None = None
    written_values: dict[str, str] | None = None

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

    def fake_write_profile_values(context, profile, values):
        nonlocal written_path, written_values
        written_path = context.vault_project_dir / "profiles" / "dev.env"
        written_values = values
        return profile, written_path

    monkeypatch.setattr(
        profile_service,
        "write_profile_values",
        fake_write_profile_values,
    )

    _context, result = profile_service.run_profile_create("dev")

    assert result.profile == "dev"
    assert result.created is True
    assert written_path is not None
    assert written_values is not None
    assert normalize_path_str(written_path).endswith("/profiles/dev.env")
    assert written_values == {}


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


def test_run_profile_copy_logs_info_summary(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
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
            {"APP_NAME": "demo"},
        ),
    )
    monkeypatch.setattr(
        profile_service,
        "write_profile_values",
        lambda context, profile, values: (
            profile,
            context.vault_project_dir / "profiles" / f"{profile}.env",
        ),
    )

    logger = logging.getLogger("envctl")
    logger.addHandler(caplog.handler)
    logger.setLevel(logging.INFO)
    caplog.set_level("INFO")

    try:
        profile_service.run_profile_copy("dev", "staging")
    finally:
        logger.removeHandler(caplog.handler)

    assert any(
        record.name == "envctl.services.profile_service"
        and record.levelname == "INFO"
        and record.message == "Profile copy completed"
        and getattr(record, "copied_key_count", None) == 1
        for record in caplog.records
    )
