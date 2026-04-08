from __future__ import annotations

import logging

import pytest

import envctl.services.unset_service as unset_service
from tests.support.contexts import make_project_context


def test_run_unset_removes_existing_key_from_active_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    profile_path = context.vault_project_dir / "profiles" / "staging.env"

    written: dict[str, object] = {}

    monkeypatch.setattr(
        unset_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        unset_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
            {"APP_NAME": "demo", "PORT": "3000"},
        ),
    )
    monkeypatch.setattr(
        unset_service,
        "write_profile_values",
        lambda context, profile, values, require_existing_explicit=False: (
            profile,
            written.update(
                {
                    "path": context.vault_project_dir / "profiles" / "staging.env",
                    "values": values,
                }
            )
            or context.vault_project_dir / "profiles" / "staging.env",
        ),
    )

    _context, active_profile, resolved_path, removed = unset_service.run_unset(
        "APP_NAME",
        "staging",
    )

    assert active_profile == "staging"
    assert resolved_path == profile_path
    assert removed is True
    assert written["path"] == profile_path
    assert written["values"] == {"PORT": "3000"}


def test_run_unset_keeps_file_when_key_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(vault_values_path="/tmp/values.env")
    written: dict[str, object] = {}

    monkeypatch.setattr(
        unset_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        unset_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False: (
            profile,
            context.vault_values_path,
            {"PORT": "3000"},
        ),
    )
    monkeypatch.setattr(
        unset_service,
        "write_profile_values",
        lambda context, profile, values, require_existing_explicit=False: (
            profile,
            written.update({"path": context.vault_values_path, "values": values})
            or context.vault_values_path,
        ),
    )

    _context, active_profile, resolved_path, removed = unset_service.run_unset(
        "APP_NAME",
        "local",
    )

    assert active_profile == "local"
    assert resolved_path == context.vault_values_path
    assert removed is False
    assert written["values"] == {"PORT": "3000"}


def test_run_unset_logs_debug_and_info(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    context = make_project_context(vault_values_path="/tmp/values.env")

    monkeypatch.setattr(
        unset_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        unset_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False: (
            profile,
            context.vault_values_path,
            {"APP_NAME": "demo"},
        ),
    )
    monkeypatch.setattr(
        unset_service,
        "write_profile_values",
        lambda context, profile, values, require_existing_explicit=False: (
            profile,
            context.vault_values_path,
        ),
    )

    logger = logging.getLogger("envctl")
    logger.addHandler(caplog.handler)
    logger.setLevel(logging.DEBUG)
    caplog.set_level("DEBUG")

    try:
        unset_service.run_unset("APP_NAME", "local")
    finally:
        logger.removeHandler(caplog.handler)

    assert any(
        record.name == "envctl.services.unset_service"
        and record.levelname == "DEBUG"
        and record.message == "Persisted unset result"
        and getattr(record, "removed", None) is True
        for record in caplog.records
    )
    assert any(
        record.name == "envctl.services.unset_service"
        and record.levelname == "INFO"
        and record.message == "Unset key in active profile"
        and getattr(record, "removed", None) is True
        for record in caplog.records
    )
