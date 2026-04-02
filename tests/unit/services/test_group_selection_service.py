from __future__ import annotations

from envctl.services.group_selection_service import (
    build_variable_groups,
    filter_projection_values,
    filter_resolution_report,
    get_group_target_keys,
)
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contracts import make_contract, make_variable_spec


def test_get_group_target_keys_matches_exact_label() -> None:
    contract = make_contract(
        {
            "API_HOST": make_variable_spec(name="API_HOST", group="Network"),
            "API_PORT": make_variable_spec(name="API_PORT", group="Runtime"),
            "API_URL": make_variable_spec(name="API_URL", group="Application"),
        }
    )

    assert get_group_target_keys(contract, group="Application") == frozenset({"API_URL"})


def test_filter_projection_values_returns_only_targeted_group() -> None:
    contract = make_contract(
        {
            "API_HOST": make_variable_spec(name="API_HOST", group="Network"),
            "API_URL": make_variable_spec(name="API_URL", group="Application"),
        }
    )

    values = {
        "API_HOST": "host",
        "API_URL": "http://host",
    }

    assert filter_projection_values(values, contract, group="Application") == {
        "API_URL": "http://host",
    }


def test_filter_resolution_report_ignores_unknown_keys_for_grouped_view() -> None:
    contract = make_contract(
        {
            "API_URL": make_variable_spec(name="API_URL", group="Application"),
            "API_HOST": make_variable_spec(name="API_HOST", group="Network"),
        }
    )
    report = make_resolution_report(
        values={
            "API_URL": make_resolved_value(key="API_URL", value="http://host"),
            "API_HOST": make_resolved_value(key="API_HOST", value="host"),
        },
        missing_required=("API_HOST",),
        unknown_keys=("OLD_KEY",),
        invalid_keys=("API_HOST",),
    )

    filtered = filter_resolution_report(report, contract, group="Application")

    assert tuple(filtered.values) == ("API_URL",)
    assert filtered.missing_required == ()
    assert filtered.invalid_keys == ()
    assert filtered.unknown_keys == ()


def test_build_variable_groups_returns_declared_labels_for_projection_keys() -> None:
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(name="APP_NAME"),
            "DATABASE_URL": make_variable_spec(name="DATABASE_URL", group="Database"),
        }
    )

    assert build_variable_groups(
        contract,
        {
            "APP_NAME": "demo",
            "DATABASE_URL": "https://db.example.com",
        },
    ) == {
        "APP_NAME": None,
        "DATABASE_URL": "Database",
    }
