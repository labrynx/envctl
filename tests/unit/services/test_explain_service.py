from __future__ import annotations

import pytest

from envctl.errors import ValidationError
from envctl.services.explain_service import run_explain
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context


def test_run_explain_returns_resolved_value(monkeypatch: pytest.MonkeyPatch) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    contract = object()
    resolved = make_resolved_value(
        key="APP_NAME",
        value="demo-app",
        source="vault",
        valid=True,
    )
    report = make_resolution_report(values={"APP_NAME": resolved})

    monkeypatch.setattr(
        "envctl.services.explain_service.load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(
        "envctl.services.explain_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.explain_service.resolve_environment",
        lambda _context, _contract: report,
    )

    result_context, value = run_explain("APP_NAME")

    assert result_context == context
    assert value is resolved
    assert value.key == "APP_NAME"
    assert value.value == "demo-app"
    assert value.source == "vault"


def test_run_explain_raises_when_key_is_not_resolved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    contract = object()
    report = make_resolution_report(missing_required=("APP_NAME",))

    monkeypatch.setattr(
        "envctl.services.explain_service.load_project_context",
        lambda project_name=None, persist_binding=False: (object(), context),
    )
    monkeypatch.setattr(
        "envctl.services.explain_service.load_contract_for_context",
        lambda _context: contract,
    )
    monkeypatch.setattr(
        "envctl.services.explain_service.resolve_environment",
        lambda _context, _contract: report,
    )

    with pytest.raises(ValidationError, match="Key is not resolved: APP_NAME"):
        run_explain("APP_NAME")
