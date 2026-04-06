from __future__ import annotations

import pytest

from envctl.domain.diagnostics import InspectKeyResult
from envctl.services.explain_service import run_explain
from tests.support.builders import make_resolved_value
from tests.support.contexts import make_project_context


def test_run_explain_delegates_to_inspect_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    context = make_project_context(repo_root="/tmp/demo")
    result = InspectKeyResult(
        project=context,
        active_profile="local",
        item=make_resolved_value(key="APP_NAME", value="demo-app", source="vault"),
        contract_type="string",
        contract_format=None,
        groups=(),
        default=None,
        sensitive=False,
    )

    monkeypatch.setattr(
        "envctl.services.explain_service.run_inspect_key",
        lambda key, active_profile=None: (context, result, ()),
    )

    result_context, value, warnings = run_explain("APP_NAME")

    assert result_context == context
    assert value is result
    assert warnings == ()
