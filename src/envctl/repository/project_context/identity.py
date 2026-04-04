from __future__ import annotations

import hashlib
from pathlib import Path

from envctl.constants import PROVISIONAL_PROJECT_ID_LENGTH


def build_provisional_project_id(repo_root: Path, repo_remote: str | None) -> str:
    """Build a provisional identifier before a binding is persisted."""
    basis = repo_remote or str(repo_root.resolve())
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()
    return f"tmp_{digest[:PROVISIONAL_PROJECT_ID_LENGTH]}"
