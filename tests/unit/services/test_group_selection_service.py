from __future__ import annotations

import pytest

from envctl.domain.selection import group_selection, set_selection, var_selection
from envctl.errors import ContractError
from envctl.services.group_selection_service import (
    build_variable_groups,
    filter_projection_values,
    filter_resolution_report,
    resolve_selected_variable_names,
)
from tests.support.builders import make_resolution_report, make_resolved_value
from tests.support.contracts import make_contract, make_set_spec, make_variable_spec


def test_resolve_selected_variable_names_matches_group() -> None:
    contract = make_contract(
        {
            "API_HOST": make_variable_spec(name="API_HOST", groups=("Network",)),
            "API_PORT": make_variable_spec(name="API_PORT", groups=("Runtime",)),
            "API_URL": make_variable_spec(name="API_URL", groups=("Application",)),
        }
    )

    assert resolve_selected_variable_names(contract, group_selection("Application")) == ("API_URL",)


def test_resolve_selected_variable_names_supports_sets() -> None:
    contract = make_contract(
        {
            "API_HOST": make_variable_spec(name="API_HOST", groups=("Network",)),
            "API_URL": make_variable_spec(name="API_URL", groups=("Application",)),
            "DATABASE_URL": make_variable_spec(name="DATABASE_URL"),
        },
        sets={
            "runtime": make_set_spec(
                name="runtime",
                groups=("Application",),
                variables=("DATABASE_URL",),
            )
        },
    )

    assert resolve_selected_variable_names(contract, set_selection("runtime")) == (
        "API_URL",
        "DATABASE_URL",
    )


def test_filter_projection_values_returns_only_targeted_selection() -> None:
    contract = make_contract(
        {
            "API_HOST": make_variable_spec(name="API_HOST", groups=("Network",)),
            "API_URL": make_variable_spec(name="API_URL", groups=("Application",)),
        }
    )

    values = {
        "API_HOST": "host",
        "API_URL": "http://host",
    }

    assert filter_projection_values(values, contract, selection=group_selection("Application")) == {
        "API_URL": "http://host",
    }


def test_filter_resolution_report_ignores_unknown_keys_for_scoped_view() -> None:
    contract = make_contract(
        {
            "API_URL": make_variable_spec(name="API_URL", groups=("Application",)),
            "API_HOST": make_variable_spec(name="API_HOST", groups=("Network",)),
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

    filtered = filter_resolution_report(report, contract, selection=group_selection("Application"))

    assert tuple(filtered.values) == ("API_URL",)
    assert filtered.missing_required == ()
    assert filtered.invalid_keys == ()
    assert filtered.unknown_keys == ()


def test_build_variable_groups_returns_first_alphabetical_group_for_projection_keys() -> None:
    contract = make_contract(
        {
            "APP_NAME": make_variable_spec(name="APP_NAME"),
            "DATABASE_URL": make_variable_spec(
                name="DATABASE_URL",
                groups=("Secrets", "Database"),
            ),
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


def test_resolve_selected_variable_names_rejects_unknown_var() -> None:
    contract = make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")})

    with pytest.raises(ContractError, match="Unknown contract variable"):
        resolve_selected_variable_names(contract, var_selection("MISSING"))
