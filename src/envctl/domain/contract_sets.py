"""Contract set models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _normalize_members(value: object, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        raw_items = list(value)
    elif isinstance(value, list):
        raw_items = value
    else:
        raise ValueError(f"'{field_name}' must be a list or tuple of strings")

    normalized: set[str] = set()
    for item in raw_items:
        if not isinstance(item, str):
            raise ValueError(f"'{field_name}' must contain only strings")
        item_normalized = item.strip()
        if not item_normalized:
            raise ValueError(f"'{field_name}' cannot contain empty values")
        normalized.add(item_normalized)
    return tuple(sorted(normalized))


class SetSpec(BaseModel):
    """Named reusable subset of contract variables."""

    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    name: str
    description: str | None = None
    sets: tuple[str, ...] = Field(default_factory=tuple)
    groups: tuple[str, ...] = Field(default_factory=tuple)
    variables: tuple[str, ...] = Field(default_factory=tuple)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("set name cannot be empty")
        return normalized

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str | None:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    @field_validator("sets", mode="before")
    @classmethod
    def normalize_sets(cls, value: object) -> tuple[str, ...]:
        return _normalize_members(value, field_name="sets")

    @field_validator("groups", mode="before")
    @classmethod
    def normalize_groups(cls, value: object) -> tuple[str, ...]:
        return _normalize_members(value, field_name="groups")

    @field_validator("variables", mode="before")
    @classmethod
    def normalize_variables(cls, value: object) -> tuple[str, ...]:
        return _normalize_members(value, field_name="variables")

    @model_validator(mode="after")
    def validate_not_empty(self) -> SetSpec:
        if not (self.sets or self.groups or self.variables):
            raise ValueError(
                f"Set '{self.name}' must declare at least one of 'sets', 'groups', or 'variables'"
            )
        return self

    def to_contract_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {}
        if self.description is not None:
            payload["description"] = self.description
        if self.sets:
            payload["sets"] = list(self.sets)
        if self.groups:
            payload["groups"] = list(self.groups)
        if self.variables:
            payload["variables"] = list(self.variables)
        return payload
