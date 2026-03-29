"""Project identifier helpers."""

from __future__ import annotations

import hashlib
from pathlib import Path

from envctl.adapters.git import get_repo_remote
from envctl.constants import PROJECT_ID_LENGTH


def build_repo_identity(repo_root: Path) -> str:
    """Build a stable repository identity string."""
    remote = get_repo_remote(repo_root)
    return remote or str(repo_root.resolve())


def build_repo_fingerprint(repo_root: Path) -> str:
    """Build a stable SHA-256 fingerprint for the repository."""
    identity = build_repo_identity(repo_root)
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def build_project_id(repo_root: Path) -> str:
    """Build the short project identifier."""
    return build_repo_fingerprint(repo_root)[:PROJECT_ID_LENGTH]
