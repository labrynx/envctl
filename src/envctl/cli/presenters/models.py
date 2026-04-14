from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

MessageLevel = Literal["info", "success", "warning", "failure", "error"]
SectionItemKind = Literal["field", "bullet", "raw"]


@dataclass(frozen=True)
class OutputMessage:
    level: MessageLevel
    text: str
    err: bool = False


@dataclass(frozen=True)
class OutputItem:
    kind: SectionItemKind
    text: str
    value: str | None = None
    err: bool = False


@dataclass(frozen=True)
class OutputSection:
    title: str
    items: list[OutputItem] = field(default_factory=list)
    err: bool = False


@dataclass(frozen=True)
class CommandOutput:
    title: str | None = None
    messages: list[OutputMessage] = field(default_factory=list)
    sections: list[OutputSection] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    