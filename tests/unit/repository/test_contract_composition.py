from __future__ import annotations

from pathlib import Path

import pytest

from envctl.errors import ContractError
from envctl.repository.contract_composition import (
    build_resolved_contract_graph,
    compose_contract_from_graph,
)
from tests.support.contracts import make_contract, make_set_spec, make_variable_spec


def test_compose_contract_from_graph_merges_sets_and_variables() -> None:
    shared = make_contract(
        {"APP_NAME": make_variable_spec(name="APP_NAME", groups=("runtime",))},
        sets={"runtime": make_set_spec(name="runtime", variables=("APP_NAME",))},
    )

    backend = make_contract(
        {"DATABASE_URL": make_variable_spec(name="DATABASE_URL", groups=("infra",))},
        sets={"runtime": make_set_spec(name="runtime", variables=("DATABASE_URL",))},
    )

    contract = compose_contract_from_graph((shared, backend))

    assert sorted(contract.variables) == ["APP_NAME", "DATABASE_URL"]
    assert contract.sets["runtime"].variables == ("APP_NAME", "DATABASE_URL")


def test_build_resolved_contract_graph_tracks_declared_in_and_groups() -> None:
    contracts = (
        make_contract({"APP_NAME": make_variable_spec(name="APP_NAME", groups=("runtime",))}),
        make_contract({"DATABASE_URL": make_variable_spec(name="DATABASE_URL", groups=("infra",))}),
    )
    paths = (Path("/repo/shared.yaml"), Path("/repo/backend.yaml"))

    graph = build_resolved_contract_graph(
        root_path=Path("/repo/.envctl.yaml"),
        contracts=contracts,
        contract_paths=paths,
        import_graph={paths[0]: (), paths[1]: ()},
    )

    assert graph.declared_in["APP_NAME"] == paths[0]
    assert graph.groups_index["runtime"] == ("APP_NAME",)


def test_build_resolved_contract_graph_raises_for_duplicate_variables() -> None:
    contracts = (
        make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")}),
        make_contract({"APP_NAME": make_variable_spec(name="APP_NAME")}),
    )

    with pytest.raises(ContractError, match=r"Duplicate variable definition: APP_NAME"):
        build_resolved_contract_graph(
            root_path=Path("/repo/.envctl.yaml"),
            contracts=contracts,
            contract_paths=(Path("/repo/a.yaml"), Path("/repo/b.yaml")),
            import_graph={},
        )
