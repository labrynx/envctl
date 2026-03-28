from __future__ import annotations

from types import SimpleNamespace

from envctl.domain.resolution import ResolutionReport, ResolvedValue
from envctl.services.inspect_service import run_inspect


def test_run_inspect_returns_context_and_resolution_report(monkeypatch) -> None:
    context = SimpleNamespace(project_slug="demo")
    contract = object()
    report = ResolutionReport(
        values={
            "APP_NAME": ResolvedValue(
                key="APP_NAME",
                value="demo-app",
                source="vault",
                masked=False,
                valid=True,
                detail=None,
            )
        },
        missing_required=[],
        unknown_keys=["LEGACY_KEY"],
        invalid_keys=[],
    )

    monkeypatch.setattr(
        "envctl.services.inspect_service.load_project_context",
        lambda: (SimpleNamespace(), context),
    )
    monkeypatch.setattr(
        "envctl.services.inspect_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.inspect_service.resolve_environment",
        lambda _context, _contract: report,
    )

    result_context, result_report = run_inspect()

    assert result_context is context
    assert result_report is report
    assert result_report.values["APP_NAME"].value == "demo-app"
    assert result_report.unknown_keys == ["LEGACY_KEY"]