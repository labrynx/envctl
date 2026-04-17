from __future__ import annotations

from envctl.cli.presenters.outputs.status import build_problem_payload
from tests.unit.cli.presenters.support.factories import make_diagnostic_problem


def test_build_problem_payload() -> None:
    problem = make_diagnostic_problem()
    payload = build_problem_payload(problem)

    assert payload["key"] == problem.key
    assert payload["kind"] == problem.kind
    assert payload["message"] == problem.message
    assert payload["actions"] == list(problem.actions)
