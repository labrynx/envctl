"""Helpers for stable project identifiers."""

from __future__ import annotations

import hashlib
from pathlib import Path

from envctl.constants import PROJECT_ID_LENGTH
from envctl.utils.git import get_repo_remote_url


def build_repo_fingerprint(repo_root: Path) -> str:
    """Build a stable repository fingerprint.

    Priority:
    1. remote.origin.url
    2. absolute repository path
    """
    remote_url = get_repo_remote_url(repo_root)
    basis = remote_url or str(repo_root.resolve())
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def build_project_id(repo_root: Path) -> str:
    """Build a compact project identifier."""
    return build_repo_fingerprint(repo_root)[:PROJECT_ID_LENGTH]
