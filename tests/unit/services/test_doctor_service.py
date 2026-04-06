from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.doctor_service as doctor_service
from envctl.domain.runtime import RuntimeMode
from envctl.errors import ExecutionError
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
        "require_persisted_profile",
        lambda context, profile: (
            profile,
            context.vault_project_dir / "profiles" / "staging.env",
        ),
    )
    monkeypatch.setattr(
        doctor_service,
        "is_world_writable",
        lambda path: False,
    )

    active_profile, checks, warnings = doctor_service.run_doctor("staging")

    assert active_profile == "staging"
    assert warnings == ()
    details = [check.detail for check in checks]
    assert any(detail == "Active profile: staging" for detail in details)
    assert any("Profile vault path:" in detail for detail in details)


def test_run_doctor_fails_when_profile_file_does_not_exist(
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
        "require_persisted_profile",
        lambda context, profile: (_ for _ in ()).throw(
            ExecutionError(
                "Profile does not exist: staging. Create it with 'envctl profile create staging'."
            )
        ),
    )
    monkeypatch.setattr(
        doctor_service,
        "is_world_writable",
        lambda path: False,
    )

    with pytest.raises(
        ExecutionError,
        match=r"Create it with 'envctl profile create staging'",
    ):
        doctor_service.run_doctor("staging")
