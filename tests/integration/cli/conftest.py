from __future__ import annotations

import subprocess
from pathlib import Path


def _git(repo_root: Path, *args: str) -> None:
    # Intentional in tests: use git from PATH against a temporary local repository.
    subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo_root,
        check=True,
        capture_output=True,
    )


def _write_sample_contract(repo_root: Path) -> None:
    (repo_root / ".envctl.yaml").write_text(
        "version: 1\n"
        "variables:\n"
        "  APP_NAME:\n"
        "    type: string\n"
        "    required: true\n"
        "    sensitive: false\n",
        encoding="utf-8",
    )
