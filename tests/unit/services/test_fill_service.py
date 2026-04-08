from __future__ import annotations

import logging

import pytest

import envctl.services.fill_service as fill_service
from tests.support.builders import make_resolution_report
from tests.support.contexts import make_project_context
from tests.support.contracts import make_fill_contract


def test_build_fill_plan_uses_active_profile_resolution(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    contract = make_fill_contract()
    report = make_resolution_report(
        missing_required=("API_KEY", "PORT"),
    )

    monkeypatch.setattr(
        fill_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        fill_service,
        "load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        fill_service,
        "resolve_environment",
        lambda _context, _contract, *, active_profile=None: report,
    )

    _context, active_profile, plan = fill_service.build_fill_plan("staging")

    assert active_profile == "staging"
    assert [item.key for item in plan] == ["API_KEY", "PORT"]
    assert plan[0].sensitive is True
    assert plan[1].default_value == "3000"


def test_apply_fill_writes_only_non_blank_values_to_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context()
    profile_path = context.vault_project_dir / "profiles" / "dev.env"
    written: dict[str, object] = {}

    monkeypatch.setattr(
        fill_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        fill_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False: (
            profile,
            context.vault_project_dir / "profiles" / "dev.env",
            {"APP_NAME": "demo"},
        ),
    )
    monkeypatch.setattr(
        fill_service,
        "write_profile_values",
        lambda context, profile, values, require_existing_explicit=False: (
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

    _context, active_profile, resolved_path, changed_keys = fill_service.apply_fill(
        {
            "API_KEY": "secret",
            "PORT": "",
            "DATABASE_URL": "  postgres://db  ",
        },
        "dev",
    )

    assert active_profile == "dev"
    assert resolved_path == profile_path
    assert changed_keys == ["API_KEY", "DATABASE_URL"]
    assert written["values"] == {
        "APP_NAME": "demo",
        "API_KEY": "secret",
        "DATABASE_URL": "postgres://db",
    }


def test_apply_fill_logs_debug_summary(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    context = make_project_context()

    monkeypatch.setattr(
        fill_service,
        "load_project_context",
        lambda: (object(), context),
    )
    monkeypatch.setattr(
        fill_service,
        "load_profile_values",
        lambda context, profile, require_existing_explicit=False: (
            profile,
            context.vault_values_path,
            {"APP_NAME": "demo"},
        ),
    )
    monkeypatch.setattr(
        fill_service,
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
        fill_service.apply_fill({"API_KEY": "secret", "PORT": " "}, "local")
    finally:
        logger.removeHandler(caplog.handler)

    assert any(
        record.name == "envctl.services.fill_service"
        and record.levelname == "DEBUG"
        and record.message == "Applied fill values"
        and getattr(record, "changed_key_count", None) == 1
        and getattr(record, "skipped_blank_key_count", None) == 1
        for record in caplog.records
    )
