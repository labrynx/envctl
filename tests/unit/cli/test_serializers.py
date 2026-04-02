from __future__ import annotations

from pathlib import Path

from envctl.cli.serializers import (
    serialize_doctor_checks,
    serialize_error,
    serialize_project_context,
    serialize_resolution_report,
    serialize_resolved_value,
    serialize_status_report,
)
from envctl.domain.doctor import DoctorCheck
from envctl.domain.status import StatusReport
from envctl.utils.masking import mask_value
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contexts import make_project_context


def test_serialize_project_context_returns_expected_shape() -> None:
    context = make_project_context(
        repo_root="/tmp/demo",
        repo_remote="git@github.com:labrynx/envctl.git",
    )

    payload = serialize_project_context(context)

    assert payload["project_slug"] == "demo"
    assert payload["project_key"] == "demo"
    assert payload["project_id"] == "prj_aaaaaaaaaaaaaaaa"
    assert payload["display_name"] == "demo (prj_aaaaaaaaaaaaaaaa)"
    assert payload["repo_root"] == "/tmp/demo"
    assert payload["repo_remote"] == "git@github.com:labrynx/envctl.git"
    assert payload["binding_source"] == "local"
    assert payload["repo_contract_path"].endswith(".envctl.schema.yaml")
    assert payload["vault_values_path"].endswith("values.env")


def test_serialize_resolved_value_masks_sensitive_values() -> None:
    item = make_resolved_value(
        key="API_KEY",
        value="super-secret",
        masked=True,
    )

    payload = serialize_resolved_value(item)

    assert payload == {
        "key": "API_KEY",
        "raw_value": None,
        "value": mask_value("super-secret"),
        "source": "vault",
        "masked": True,
        "expansion_status": "none",
        "expansion_refs": [],
        "expansion_error": None,
        "valid": True,
        "detail": None,
    }


def test_serialize_resolution_report_returns_expected_shape() -> None:
    report = make_resolution_report(
        values={
            "PORT": make_resolved_value(
                key="PORT",
                value="abc",
                source="default",
                masked=False,
                valid=False,
                detail="Expected an integer",
            ),
            "API_KEY": make_resolved_value(
                key="API_KEY",
                value="super-secret",
                source="vault",
                masked=True,
                valid=True,
            ),
        },
        missing_required=("DATABASE_URL",),
        unknown_keys=("LEGACY_KEY",),
        invalid_keys=("PORT",),
    )

    payload = serialize_resolution_report(report)

    assert payload["is_valid"] is False
    assert payload["missing_required"] == ["DATABASE_URL"]
    assert payload["unknown_keys"] == ["LEGACY_KEY"]
    assert payload["invalid_keys"] == ["PORT"]
    assert payload["values"]["API_KEY"]["value"] == mask_value("super-secret")
    assert payload["values"]["API_KEY"]["expansion_status"] == "none"
    assert payload["values"]["PORT"]["detail"] == "Expected an integer"


def test_serialize_status_report_returns_expected_shape() -> None:
    report = StatusReport(
        project_slug="demo",
        project_id="prj_aaaaaaaaaaaaaaaa",
        repo_root=Path("/tmp/demo"),
        contract_exists=True,
        vault_exists=False,
        resolved_valid=False,
        summary="The project contract is not satisfied yet.",
        issues=["Missing required keys: API_KEY"],
        suggested_action="Run 'envctl fill'",
    )

    payload = serialize_status_report(report)

    assert payload == {
        "project_slug": "demo",
        "project_id": "prj_aaaaaaaaaaaaaaaa",
        "repo_root": "/tmp/demo",
        "contract_exists": True,
        "vault_exists": False,
        "resolved_valid": False,
        "summary": "The project contract is not satisfied yet.",
        "issues": ["Missing required keys: API_KEY"],
        "suggested_action": "Run 'envctl fill'",
    }


def test_serialize_doctor_checks_aggregates_failures() -> None:
    payload = serialize_doctor_checks(
        [
            DoctorCheck("config", "ok", "config ok"),
            DoctorCheck("vault", "warn", "vault warn"),
            DoctorCheck("git", "fail", "git fail"),
        ]
    )

    assert payload["has_failures"] is True
    assert payload["checks"] == [
        {"name": "config", "status": "ok", "detail": "config ok"},
        {"name": "vault", "status": "warn", "detail": "vault warn"},
        {"name": "git", "status": "fail", "detail": "git fail"},
    ]


def test_serialize_error_returns_expected_shape() -> None:
    payload = serialize_error(
        error_type="ValidationError",
        message="Cannot sync because the resolved environment is invalid",
        command="envctl sync",
    )

    assert payload == {
        "ok": False,
        "command": "envctl sync",
        "error": {
            "type": "ValidationError",
            "message": "Cannot sync because the resolved environment is invalid",
        },
    }
