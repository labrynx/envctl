"""Contract domain models."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from envctl.constants import CONTRACT_VERSION
from envctl.errors import ContractError

VariableType = Literal["string", "int", "bool", "url"]

_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


class VariableSpec(BaseModel):
    """Single variable declaration in the contract."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    name: str
    type: VariableType = "string"
    required: bool = True
    description: str = ""
    sensitive: bool = True
    default: str | int | bool | None = None
    provider: str | None = None
    example: str | None = None
    pattern: str | None = None
    choices: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Validate the contract variable name."""
        if not _KEY_RE.fullmatch(value):
            raise ValueError(f"Invalid variable name: {value!r}")
        return value

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        """Normalize the human-readable description."""
        return value.strip()

    @field_validator("provider", "example", "pattern", mode="before")
    @classmethod
    def normalize_optional_string(cls, value: object) -> str | None:
        """Normalize optional string values."""
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("choices", mode="before")
    @classmethod
    def normalize_choices(cls, value: object) -> tuple[str, ...]:
        """Normalize and validate choices."""
        if value is None:
            return ()

        if isinstance(value, tuple):
            raw_items = list(value)
        elif isinstance(value, list):
            raw_items = value
        else:
            raise ValueError("'choices' must be a list or tuple of strings")

        items: list[str] = []
        seen: set[str] = set()

        for item in raw_items:
            if not isinstance(item, str):
                raise ValueError("'choices' must contain only strings")
            normalized = item.strip()
            if not normalized:
                raise ValueError("'choices' cannot contain empty values")
            if normalized not in seen:
                seen.add(normalized)
                items.append(normalized)

        return tuple(items)

    @model_validator(mode="after")
    def validate_consistency(self) -> VariableSpec:
        """Validate cross-field consistency."""
        if self.pattern is not None:
            try:
                re.compile(self.pattern)
            except re.error as exc:
                raise ValueError(
                    f"Invalid regex pattern for '{self.name}': {self.pattern}"
                ) from exc

        if self.choices and self.default is not None:
            default_as_string = str(self.default)
            if default_as_string not in self.choices:
                raise ValueError(
                    f"Default value for '{self.name}' must be one of: {', '.join(self.choices)}"
                )

        return self

    def to_contract_payload(self) -> dict[str, object]:
        """Convert the spec into a YAML-friendly payload."""
        payload: dict[str, object] = {
            "type": self.type,
            "required": self.required,
            "sensitive": self.sensitive,
            "description": self.description,
        }

        if self.default is not None:
            payload["default"] = self.default

        if self.provider is not None:
            payload["provider"] = self.provider

        if self.example is not None:
            payload["example"] = self.example

        if self.pattern is not None:
            payload["pattern"] = self.pattern

        if self.choices:
            payload["choices"] = list(self.choices)

        return payload


class Contract(BaseModel):
    """Repository environment contract."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    version: int = CONTRACT_VERSION
    variables: dict[str, VariableSpec] = Field(default_factory=dict)

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: int) -> int:
        """Validate the contract version."""
        if value != CONTRACT_VERSION:
            raise ValueError(f"Unsupported contract version: {value}")
        return value

    @model_validator(mode="after")
    def validate_variables(self) -> Contract:
        """Ensure mapping keys and embedded spec names match."""
        for key, spec in self.variables.items():
            if key != spec.name:
                raise ValueError(f"Variable key '{key}' does not match embedded name '{spec.name}'")
        return self

    def with_variable(self, spec: VariableSpec) -> Contract:
        """Return a new contract with one variable inserted or replaced."""
        variables = dict(self.variables)
        variables[spec.name] = spec
        return self.model_copy(update={"variables": variables})

    def without_variable(self, key: str) -> Contract:
        """Return a new contract without one variable."""
        variables = dict(self.variables)
        variables.pop(key, None)
        return self.model_copy(update={"variables": variables})

    def to_contract_payload(self) -> dict[str, object]:
        """Convert the contract into a YAML-friendly payload."""
        return {
            "version": self.version,
            "variables": {
                key: self.variables[key].to_contract_payload() for key in sorted(self.variables)
            },
        }


def validate_contract_or_raise(payload: dict[str, object]) -> Contract:
    """Validate a contract payload and convert validation failures to ContractError."""
    try:
        return Contract.model_validate(payload)
    except Exception as exc:
        raise ContractError(str(exc)) from exc
