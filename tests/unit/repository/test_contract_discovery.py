from __future__ import annotations

from pathlib import Path

import pytest

from envctl.errors import ContractError
from envctl.repository.contract_discovery import discover_root_contract_path


def test_discover_root_contract_prefers_primary_file(tmp_path: Path) -> None:
    (tmp_path / ".envctl.yaml").write_text("version: 1\nvariables: {}\n", encoding="utf-8")
    (tmp_path / ".envctl.schema.yaml").write_text("version: 1\nvariables: {}\n", encoding="utf-8")

    result = discover_root_contract_path(tmp_path)

    assert result.path == tmp_path / ".envctl.yaml"
    assert result.warnings
    assert result.warnings[0].kind == "dual_root_contract"


def test_discover_root_contract_falls_back_to_legacy_file(tmp_path: Path) -> None:
    (tmp_path / ".envctl.yaml").write_text("version: 1\nvariables: {}\n", encoding="utf-8")

    result = discover_root_contract_path(tmp_path)

    assert result.path == tmp_path / ".envctl.yaml"
    assert result.warnings == ()


def test_discover_root_contract_raises_when_missing(tmp_path: Path) -> None:
    with pytest.raises(ContractError, match=r"Main envctl contract not found") as exc_info:
        discover_root_contract_path(tmp_path)

    assert exc_info.value.diagnostics is not None
