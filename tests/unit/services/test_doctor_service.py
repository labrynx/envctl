from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.doctor_service as doctor_service
from envctl.domain.runtime import RuntimeMode
from tests.support.contexts import make_project_context


def test_run_doctor_reports_active_profile_and_profile_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = type(
        "Config",
        (),
        {
            "runtime_mode": RuntimeMode.LOCAL,
            "vault_dir": Path("/tmp/vault"),
        },
    )()
    context = make_project_context()

    monkeypatch.setattr(
        doctor_service,
        "load_project_context",
        lambda: (config, context),
    )
    monkeypatch.setattr(
        doctor_service,
        "build_project_context",
        lambda _config: context,
    )
    monkeypatch.setattr(
        doctor_service,
        "is_world_writable",
        lambda path: False,
    )

    active_profile, checks = doctor_service.run_doctor("staging")

    assert active_profile == "staging"
    details = [check.detail for check in checks]
    assert any(detail == "Active profile: staging" for detail in details)
    assert any("Profile vault path:" in detail for detail in details)


def test_run_doctor_warns_when_profile_file_does_not_exist(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = type(
        "Config",
        (),
        {
            "runtime_mode": RuntimeMode.LOCAL,
            "vault_dir": Path("/tmp/vault"),
        },
    )()
    context = make_project_context()

    monkeypatch.setattr(
        doctor_service,
        "load_project_context",
        lambda: (config, context),
    )
    monkeypatch.setattr(
        doctor_service,
        "build_project_context",
        lambda _config: context,
    )
    monkeypatch.setattr(
        doctor_service,
        "is_world_writable",
        lambda path: False,
    )

    _active_profile, checks = doctor_service.run_doctor("staging")

    vault_profile_checks = [check for check in checks if check.name == "vault_profile"]
    assert len(vault_profile_checks) == 1
    assert vault_profile_checks[0].status == "warn"
