from __future__ import annotations

from envctl.services.resolution_diagnostics import (
    build_diagnostic_problems,
    build_diagnostic_summary,
    extract_referenced_key,
)
from tests.support.builders import make_resolution_report, make_resolved_value


def test_extract_referenced_key_returns_name_when_present() -> None:
    assert extract_referenced_key("missing value for referenced key 'API_HOST'") == "API_HOST"


def test_build_diagnostic_summary_counts_values_and_missing() -> None:
    report = make_resolution_report(
        values={"APP_NAME": make_resolved_value(key="APP_NAME", value="demo")},
        missing_required=("DATABASE_URL",),
        unknown_keys=("OLD_KEY",),
        invalid_keys=(),
    )

    summary = build_diagnostic_summary(report)

    assert summary.total == 2
    assert summary.valid == 1
    assert summary.invalid == 1
    assert summary.unknown == 1


def test_build_diagnostic_problems_builds_expansion_reference_actions() -> None:
    report = make_resolution_report(
        values={
            "APP_URL": make_resolved_value(
                key="APP_URL",
                value="",
                valid=False,
                detail="missing value for referenced key 'API_HOST'",
                expansion_status="error",
                expansion_error=__import__(
                    "envctl.domain.expansion", fromlist=["ExpansionErrorInfo"]
                ).ExpansionErrorInfo(
                    kind="missing_reference", detail="missing value for referenced key 'API_HOST'"
                ),
            )
        },
        invalid_keys=("APP_URL",),
    )

    problems = build_diagnostic_problems(report)

    assert len(problems) == 1
    assert problems[0].kind == "expansion_reference_error"
    assert "envctl inspect API_HOST" in problems[0].actions
