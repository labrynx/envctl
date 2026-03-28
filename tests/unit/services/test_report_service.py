from __future__ import annotations

from types import SimpleNamespace

import pytest

import envctl.services.export_service as export_service
from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.errors import ValidationError
from envctl.services.export_service import run_export


def test_run_export_returns_shell_lines_for_valid_environment(monkeypatch) -> None:
    context = SimpleNamespace()
    contract = object()
    report = ResolutionReport(
        values={
            "APP_NAME": ResolvedValue(
                key="APP_NAME",
                value="demo",
                source="vault",
                masked=False,
                valid=True,
                detail=None,
            ),
            "DATABASE_URL": ResolvedValue(
                key="DATABASE_URL",
                value="https://db.example.com",
                source="vault",
                masked=True,
                valid=True,
                detail=None,
            ),
        },
        missing_required=[],
        unknown_keys=[],
        invalid_keys=[],
    )

    monkeypatch.setattr(export_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(export_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(export_service, "resolve_environment", lambda _context, _contract: report)

    lines = run_export()

    assert lines == [
        "export APP_NAME='demo'",
        "export DATABASE_URL='https://db.example.com'",
    ]


def test_run_export_raises_when_environment_is_invalid(monkeypatch) -> None:
    context = SimpleNamespace()
    contract = object()
    report = ResolutionReport(
        values={},
        missing_required=["APP_NAME"],
        unknown_keys=[],
        invalid_keys=[],
    )

    monkeypatch.setattr(export_service, "load_project_context", lambda: (SimpleNamespace(), context))
    monkeypatch.setattr(export_service, "load_contract_for_context", lambda _context: contract)
    monkeypatch.setattr(export_service, "resolve_environment", lambda _context, _contract: report)

    with pytest.raises(ValidationError, match="Cannot export because the resolved environment is invalid"):
        run_export()