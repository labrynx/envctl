from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast


def unwrap_callable(value: object) -> Callable[..., Any]:
    return cast(Callable[..., Any], value.__wrapped__)
