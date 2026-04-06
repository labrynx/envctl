from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from envctl.errors import ContractError
from envctl.repository.contract_graph import resolve_contract_graph


def _write_contract(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_resolve_contract_graph_loads_recursive_imports_once(tmp_path: Path) -> None:
    root = tmp_path / ".envctl.yaml"
    shared = tmp_path / "contracts" / "shared.yaml"
    backend = tmp_path / "contracts" / "backend.yaml"
    _write_contract(
        root,
        {
            "version": 1,
            "imports": ["./contracts/shared.yaml", "./contracts/backend.yaml"],
            "variables": {"ROOT": {"sensitive": False}},
        },
    )
    _write_contract(
        shared,
        {
            "version": 1,
            "imports": ["./backend.yaml"],
            "variables": {"SHARED": {"sensitive": False}},
        },
    )
    _write_contract(backend, {"version": 1, "variables": {"BACKEND": {"sensitive": False}}})

    result = resolve_contract_graph(root, repo_root=tmp_path)

    assert result.root_path == root.resolve()
    assert result.contract_paths.count(backend.resolve()) == 1
    assert backend.resolve() in result.import_graph[shared.resolve()]


def test_resolve_contract_graph_detects_cycles(tmp_path: Path) -> None:
    root = tmp_path / ".envctl.yaml"
    shared = tmp_path / "contracts" / "shared.yaml"
    _write_contract(
        root,
        {
            "version": 1,
            "imports": ["./contracts/shared.yaml"],
            "variables": {"ROOT": {"sensitive": False}},
        },
    )
    _write_contract(
        shared,
        {
            "version": 1,
            "imports": ["../.envctl.yaml"],
            "variables": {"SHARED": {"sensitive": False}},
        },
    )

    with pytest.raises(ContractError, match=r"Reserved root contract import is not allowed"):
        resolve_contract_graph(root, repo_root=tmp_path)


def test_resolve_contract_graph_raises_for_invalid_import_path(tmp_path: Path) -> None:
    root = tmp_path / ".envctl.yaml"
    _write_contract(
        root,
        {
            "version": 1,
            "imports": ["./contracts/missing.yaml"],
            "variables": {"ROOT": {"sensitive": False}},
        },
    )

    with pytest.raises(ContractError, match=r"Invalid contract import"):
        resolve_contract_graph(root, repo_root=tmp_path)
