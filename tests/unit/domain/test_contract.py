from __future__ import annotations

import pytest

from envctl.domain.contract import VariableSpec


def test_variable_spec_accepts_string_format() -> None:
    spec = VariableSpec(name="TEST_JSON", type="string", format="json")

    assert spec.format == "json"


def test_variable_spec_rejects_format_for_non_string_types() -> None:
    with pytest.raises(ValueError, match="can only be used with type 'string'"):
        VariableSpec(name="PORT", type="int", format="json")
