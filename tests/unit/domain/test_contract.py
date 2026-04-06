from __future__ import annotations

import pytest

from envctl.domain.contract import VariableSpec


def test_variable_spec_accepts_string_format() -> None:
    spec = VariableSpec(name="TEST_JSON", type="string", format="json")

    assert spec.format == "json"


def test_variable_spec_rejects_format_for_non_string_types() -> None:
    with pytest.raises(ValueError, match=r"can only be used with type 'string'"):
        VariableSpec(name="PORT", type="int", format="json")


def test_variable_spec_accepts_groups_array() -> None:
    spec = VariableSpec(name="DATABASE_URL", groups=("Database", "Secrets", "Database"))

    assert spec.groups == ("Database", "Secrets")
    assert spec.normalized_groups == ("Database", "Secrets")


def test_variable_spec_accepts_legacy_group_for_compatibility() -> None:
    spec = VariableSpec(name="DATABASE_URL", group="Database")

    assert spec.group == "Database"
    assert spec.normalized_groups == ("Database",)


def test_variable_spec_normalizes_blank_group_to_none() -> None:
    spec = VariableSpec(name="DATABASE_URL", group="   ")

    assert spec.group is None
    assert spec.normalized_groups == ()


def test_variable_spec_rejects_group_and_groups_together() -> None:
    with pytest.raises(ValueError, match=r"cannot define both 'group' and 'groups'"):
        VariableSpec(name="DATABASE_URL", group="Database", groups=("Database",))
