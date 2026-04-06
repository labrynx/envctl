"""Contract domain models."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from envctl.constants import CONTRACT_VERSION
from envctl.domain.contract_sets import SetSpec

VariableType = Literal["string", "int", "bool", "url"]
VariableFormat = Literal["json", "url", "csv"]

VARIABLE_NAME_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"
_KEY_RE = re.compile(VARIABLE_NAME_PATTERN)


def is_valid_variable_name(value: str) -> bool:
    """Return whether one environment variable name follows the contract rules."""
    return _KEY_RE.fullmatch(value) is not None


def _normalize_string_sequence(value: object, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, tuple):
        raw_items = list(value)
    elif isinstance(value, list):
        raw_items = value
    else:
        raise ValueError(f"'{field_name}' must be a list or tuple of strings")

    items: set[str] = set()
    for item in raw_items:
        if not isinstance(item, str):
            raise ValueError(f"'{field_name}' must contain only strings")
        normalized = item.strip()
        if not normalized:
            raise ValueError(f"'{field_name}' cannot contain empty values")
        items.add(normalized)

    return tuple(sorted(items))


class ContractMeta(BaseModel):
    """Shared logical metadata for the repository contract."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True,
    )

    project_key: str
    project_name: str | None = None

    @field_validator("project_key")
    @classmethod
    def validate_project_key(cls, value: str) -> str:
        """Validate the logical project key."""
        normalized = value.strip()
        if not normalized:
            raise ValueError("project_key cannot be empty")
        return normalized

    @field_validator("project_name")
    @classmethod
    def normalize_project_name(cls, value: str | None) -> str | None:
        """Normalize the human project name."""
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


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
    group: str | None = None
    groups: tuple[str, ...] = Field(default_factory=tuple)
    format: VariableFormat | None = None
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

    @field_validator("provider", "example", "group", "pattern", mode="before")
    @classmethod
    def normalize_optional_string(cls, value: object) -> str | None:
        """Normalize optional string values."""
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("groups", mode="before")
    @classmethod
    def normalize_groups(cls, value: object) -> tuple[str, ...]:
        """Normalize multi-group membership."""
        return _normalize_string_sequence(value, field_name="groups")

    @field_validator("choices", mode="before")
    @classmethod
    def normalize_choices(cls, value: object) -> tuple[str, ...]:
        """Normalize and validate choices."""
        return _normalize_string_sequence(value, field_name="choices")

    @model_validator(mode="after")
    def validate_consistency(self) -> VariableSpec:
        """Validate cross-field consistency."""
        if self.group is not None and self.groups:
            raise ValueError(f"Variable '{self.name}' cannot define both 'group' and 'groups'")

        if self.format is not None and self.type != "string":
            raise ValueError(f"'format' can only be used with type 'string' for '{self.name}'")

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

    @property
    def normalized_groups(self) -> tuple[str, ...]:
        """Return normalized groups, including legacy `group` compatibility."""
        if self.groups:
            return self.groups
        if self.group is not None:
            return (self.group,)
        return ()

    def to_contract_payload(self) -> dict[str, object]:
        """Convert the spec into a YAML-friendly payload."""
        payload: dict[str, object] = {
            "type": self.type,
            "sensitive": self.sensitive,
            "description": self.description,
        }

        if self.default is not None:
            payload["default"] = self.default

        if self.provider is not None:
            payload["provider"] = self.provider

        if self.example is not None:
            payload["example"] = self.example

        if self.normalized_groups:
            payload["groups"] = list(self.normalized_groups)

        if self.format is not None:
            payload["format"] = self.format

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
    meta: ContractMeta | None = None
    variables: dict[str, VariableSpec] = Field(default_factory=dict)
    sets: dict[str, SetSpec] = Field(default_factory=dict)

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: int) -> int:
        """Validate the contract version."""
        if value != CONTRACT_VERSION:
            raise ValueError(f"Unsupported contract version: {value}")
        return value

    @model_validator(mode="after")
    def validate_contract(self) -> Contract:
        """Ensure mapping keys, embedded names, and set references match."""
        for key, variable_spec in self.variables.items():
            if key != variable_spec.name:
                raise ValueError(
                    f"Variable key '{key}' does not match embedded name '{variable_spec.name}'"
                )

        for key, set_spec in self.sets.items():
            if key != set_spec.name:
                raise ValueError(f"Set key '{key}' does not match embedded name '{set_spec.name}'")

            for referenced_set in set_spec.sets:
                if referenced_set not in self.sets:
                    raise ValueError(
                        f"Set '{set_spec.name}' references unknown set '{referenced_set}'"
                    )

            for referenced_variable in set_spec.variables:
                if referenced_variable not in self.variables:
                    raise ValueError(
                        f"Set '{set_spec.name}' references unknown variable '{referenced_variable}'"
                    )

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

    def with_meta(
        self,
        *,
        project_key: str,
        project_name: str | None = None,
    ) -> Contract:
        """Return a new contract with logical metadata ensured."""
        return self.model_copy(
            update={
                "meta": ContractMeta(
                    project_key=project_key,
                    project_name=project_name,
                )
            }
        )

    def to_contract_payload(self) -> dict[str, object]:
        """Convert the contract into a YAML-friendly payload."""
        payload: dict[str, object] = {
            "version": self.version,
            "variables": {
                key: self.variables[key].to_contract_payload() for key in sorted(self.variables)
            },
        }

        if self.meta is not None:
            payload["meta"] = self.meta.model_dump(
                mode="python",
                exclude_none=True,
            )

        if self.sets:
            payload["sets"] = {
                key: self.sets[key].to_contract_payload() for key in sorted(self.sets)
            }

        return payload
