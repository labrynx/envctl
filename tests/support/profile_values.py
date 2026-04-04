from __future__ import annotations

from pathlib import Path

import pytest

import envctl.services.resolution_service.resolution as resolution_service_module


def patch_loaded_profile_values(
    monkeypatch: pytest.MonkeyPatch,
    *,
    values: dict[str, str],
    profile: str = "local",
) -> Path:
    """Patch profile loading with explicit contract-backed values."""
    path = (
        Path("/tmp/vault.env") if profile == "local" else Path("/tmp/profiles") / f"{profile}.env"
    )

    monkeypatch.setattr(
        resolution_service_module,
        "load_profile_values",
        lambda _context, _profile, require_existing_explicit=False: (
            _profile,
            path,
            values.copy(),
        ),
    )

    return path
