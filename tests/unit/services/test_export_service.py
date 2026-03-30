from __future__ import annotations

from types import SimpleNamespace

import pytest

import envctl.services.export_service as export_service
from envctl.errors import ValidationError
from envctl.services.export_service import run_export
from tests.support.builders import make_resolution_report, make_resolved_value


def test_run_export_returns_shell_lines_for_valid_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = SimpleNamespace(project_slug="demo")
    contract = object()
    report = make_resolution_report(
        values={
            "APP_NAME": make_resolved_value(
                key="APP_NAME",
                value="demo",
                source="vault",
                valid=True,
            ),
            "DATABASE_URL": make_resolved_value(
                key="DATABASE_URL",
                value="https://db.example.com",
                source="vault",
                valid=True,
                masked=True,
            ),
        }
    )

    monkeypatch.setattr(
        export_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(export_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(export_service, "resolve_environment", lambda _context, _contract: report)

    result_context, lines = run_export()

    assert result_context is context
    assert lines == [
        "export APP_NAME='demo'",
        "export DATABASE_URL='https://db.example.com'",
    ]


def test_run_export_raises_when_environment_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = SimpleNamespace(project_slug="demo")
    contract = object()
    report = make_resolution_report(missing_required=("DATABASE_URL",))

    monkeypatch.setattr(
        export_service,
        "load_project_context",
        lambda project_name=None, persist_binding=False: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(export_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(export_service, "resolve_environment", lambda _context, _contract: report)

    with pytest.raises(
        ValidationError,
        match="Cannot export because the resolved environment is invalid",
    ):
        run_export()
