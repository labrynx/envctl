from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast


def unwrap_callable(value: object) -> Callable[..., Any]:
    wrapped = getattr(value, "__wrapped__", None)
    if wrapped is None or not callable(wrapped):
        msg = "Expected a wrapped callable with __wrapped__"
        raise TypeError(msg)
    return cast(Callable[..., Any], wrapped)
