from __future__ import annotations

import pytest

from envctl.domain.contract import VariableSpec


def test_variable_spec_accepts_string_format() -> None:
    spec = VariableSpec(name="TEST_JSON", type="string", format="json")

    assert spec.format == "json"


def test_variable_spec_rejects_format_for_non_string_types() -> None:
    with pytest.raises(ValueError, match=r"can only be used with type 'string'"):
        VariableSpec(name="PORT", type="int", format="json")


def test_variable_spec_accepts_optional_group_label() -> None:
    spec = VariableSpec(name="DATABASE_URL", group="Database")

    assert spec.group == "Database"


def test_variable_spec_normalizes_blank_group_to_none() -> None:
    spec = VariableSpec(name="DATABASE_URL", group="   ")

    assert spec.group is None
