from __future__ import annotations

from envctl.domain.contract import Contract, VariableFormat, VariableSpec, VariableType
from envctl.domain.contract_sets import SetSpec


def make_variable_spec(
    *,
    name: str,
    type: VariableType = "string",
    required: bool = True,
    description: str = "",
    sensitive: bool = False,
    default: str | int | bool | None = None,
    provider: str | None = None,
    example: str | None = None,
    group: str | None = None,
    groups: tuple[str, ...] = (),
    format: VariableFormat | None = None,
    pattern: str | None = None,
    choices: tuple[str, ...] = (),
) -> VariableSpec:
    """Build a variable spec with sensible test defaults."""
    return VariableSpec(
        name=name,
        type=type,
        required=required,
        description=description,
        sensitive=sensitive,
        default=default,
        provider=provider,
        example=example,
        group=group,
        groups=groups,
        format=format,
        pattern=pattern,
        choices=choices,
    )


def make_set_spec(
    *,
    name: str,
    description: str | None = None,
    sets: tuple[str, ...] = (),
    groups: tuple[str, ...] = (),
    variables: tuple[str, ...] = (),
) -> SetSpec:
    """Build a set spec with normalized values."""
    return SetSpec(
        name=name,
        description=description,
        sets=sets,
        groups=groups,
        variables=variables,
    )


def make_contract(
    variables: dict[str, VariableSpec] | None = None,
    *,
    sets: dict[str, SetSpec] | None = None,
    version: int = 1,
) -> Contract:
    """Build a contract with optional variables and sets."""
    return Contract(
        version=version,
        variables=variables or {},
        sets=sets or {},
    )


def make_standard_contract() -> Contract:
    """Build the standard contract used across many tests."""
    return make_contract(
        {
            "APP_NAME": make_variable_spec(
                name="APP_NAME",
                type="string",
                required=True,
                sensitive=False,
            ),
            "PORT": make_variable_spec(
                name="PORT",
                type="int",
                required=True,
                sensitive=False,
                default=3000,
            ),
            "DEBUG": make_variable_spec(
                name="DEBUG",
                type="bool",
                required=False,
                sensitive=False,
            ),
            "DATABASE_URL": make_variable_spec(
                name="DATABASE_URL",
                type="url",
                required=True,
                sensitive=True,
            ),
            "ENVIRONMENT": make_variable_spec(
                name="ENVIRONMENT",
                type="string",
                required=False,
                sensitive=False,
                choices=("dev", "prod"),
            ),
            "SLUG": make_variable_spec(
                name="SLUG",
                type="string",
                required=False,
                sensitive=False,
                pattern=r"^[a-z0-9-]+$",
            ),
        }
    )


def make_fill_contract() -> Contract:
    """Build the contract used in fill-service tests."""
    return make_contract(
        {
            "API_KEY": make_variable_spec(
                name="API_KEY",
                type="string",
                required=True,
                description="API key",
                sensitive=True,
            ),
            "PORT": make_variable_spec(
                name="PORT",
                type="int",
                required=True,
                description="Port number",
                sensitive=False,
                default=3000,
            ),
        }
    )
