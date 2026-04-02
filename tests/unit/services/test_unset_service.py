from __future__ import annotations

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
        "load_env_file",
        lambda path: {"APP_NAME": "demo", "PORT": "3000"},
    )
    monkeypatch.setattr(
        unset_service,
        "_write_profile_values",
        lambda path, values: written.update({"path": path, "values": values}),
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
        "load_env_file",
        lambda path: {"PORT": "3000"},
    )
    monkeypatch.setattr(
        unset_service,
        "_write_profile_values",
        lambda path, values: written.update({"path": path, "values": values}),
    )

    _context, active_profile, resolved_path, removed = unset_service.run_unset(
        "APP_NAME",
        "local",
    )

    assert active_profile == "local"
    assert resolved_path == context.vault_values_path
    assert removed is False
    assert written["values"] == {"PORT": "3000"}
