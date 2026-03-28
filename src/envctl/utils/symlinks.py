"""Symlink capability helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

from envctl.domain.doctor import DoctorCheck


def check_symlink_support() -> DoctorCheck:
    """Check whether symlink creation works in the current environment."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        source = root / "source.txt"
        target = root / "target.txt"
        source.write_text("ok", encoding="utf-8")

        try:
            target.symlink_to(source)
            ok = target.is_symlink() and target.resolve() == source.resolve()
            return DoctorCheck(
                name="symlink_support",
                status="ok" if ok else "fail",
                detail="Symlink creation works",
            )
        except OSError as exc:
            return DoctorCheck(
                name="symlink_support",
                status="fail",
                detail=f"Symlink creation failed: {exc}",
            )
