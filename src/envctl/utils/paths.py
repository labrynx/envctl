"""Path and project resolution helpers."""

from __future__ import annotations

import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from envctl.constants import GIT_DIRNAME, PROJECT_ID_LENGTH
from envctl.errors import ProjectDetectionError
from envctl.models import AppConfig, ProjectContext


def slugify_project_name(name: str) -> str:
    """Normalize a project name into a filesystem-safe slug."""
    value = name.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    if not value:
        raise ProjectDetectionError("Project name resolved to empty value")
    return value


def detect_repo_root(start: Path) -> Path | None:
    """Walk up from a path until a git root is found."""
    current = start.resolve()
    for candidate in [current, *current.parents]:
        if (candidate / GIT_DIRNAME).exists():
            return candidate
    return None


def resolve_repo_root(start: Path | None = None) -> Path:
    """Resolve the repository root, falling back to the current directory."""
    origin = (start or Path.cwd()).resolve()
    return detect_repo_root(origin) or origin


def require_git_repo_root(start: Path | None = None) -> Path:
    """Resolve the git repository root or fail explicitly."""
    origin = (start or Path.cwd()).resolve()
    repo_root = detect_repo_root(origin)
    if repo_root is None:
        raise ProjectDetectionError("envctl init must be run inside a Git repository")
    return repo_root


def resolve_project_name(repo_root: Path, explicit_project_name: str | None) -> str:
    """Resolve the effective project slug."""
    if explicit_project_name:
        return slugify_project_name(explicit_project_name)
    return slugify_project_name(repo_root.name)


def get_repo_remote_url(repo_root: Path) -> str | None:
    """Return the origin remote URL when available."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=repo_root,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None

    value = result.stdout.strip()
    return value or None


def build_repo_fingerprint(repo_root: Path) -> str:
    """Build a stable repository fingerprint.

    Priority:
    1. `remote.origin.url`
    2. absolute repository path

    TODO(v1.1):
    - consider multi-remote selection strategies
    - consider explicit repo identity pinning if the remote changes later
    """
    remote_url = get_repo_remote_url(repo_root)
    basis = remote_url or str(repo_root.resolve())
    return hashlib.sha256(basis.encode("utf-8")).hexdigest()


def build_project_id(repo_root: Path) -> str:
    """Build a compact project identifier."""
    return build_repo_fingerprint(repo_root)[:PROJECT_ID_LENGTH]


def build_vault_project_dir(project_slug: str, project_id: str, projects_dir: Path) -> Path:
    """Build the unique project directory inside the vault."""
    return projects_dir / f"{project_slug}--{project_id}"


def build_project_context(config: AppConfig, project_name: str | None) -> ProjectContext:
    """Build a project context from the current repository and project name."""
    repo_root = require_git_repo_root()
    project_slug = resolve_project_name(repo_root, project_name)
    project_id = build_project_id(repo_root)

    repo_metadata_path = repo_root / config.metadata_filename
    repo_env_path = repo_root / config.env_filename
    vault_project_dir = build_vault_project_dir(project_slug, project_id, config.projects_dir)
    vault_env_path = vault_project_dir / config.env_filename

    return ProjectContext(
        project_slug=project_slug,
        project_id=project_id,
        repo_root=repo_root,
        repo_metadata_path=repo_metadata_path,
        repo_env_path=repo_env_path,
        vault_project_dir=vault_project_dir,
        vault_env_path=vault_env_path,
    )


def build_context_from_metadata_record(
    config: AppConfig,
    repo_root: Path,
    metadata: dict[str, Any] | None,
) -> ProjectContext | None:
    """Build a project context from stored repository metadata."""
    if not metadata:
        return None

    project_slug = metadata.get("project_slug")
    project_id = metadata.get("project_id")
    env_filename = metadata.get("env_filename", config.env_filename)

    if not isinstance(project_slug, str) or not project_slug.strip():
        return None
    if not isinstance(project_id, str) or not project_id.strip():
        return None
    if not isinstance(env_filename, str) or not env_filename.strip():
        return None

    normalized_slug = slugify_project_name(project_slug)
    normalized_id = project_id.strip()

    repo_metadata_path = repo_root / config.metadata_filename
    repo_env_path = repo_root / env_filename
    vault_project_dir = build_vault_project_dir(normalized_slug, normalized_id, config.projects_dir)
    vault_env_path = vault_project_dir / env_filename

    return ProjectContext(
        project_slug=normalized_slug,
        project_id=normalized_id,
        repo_root=repo_root,
        repo_metadata_path=repo_metadata_path,
        repo_env_path=repo_env_path,
        vault_project_dir=vault_project_dir,
        vault_env_path=vault_env_path,
    )


def require_project_context(config: AppConfig) -> ProjectContext:
    """Return the stored project context or fail if the repository is not initialized."""
    from envctl.utils.filesystem import read_project_metadata_record

    repo_root = resolve_repo_root()
    metadata_path = repo_root / config.metadata_filename
    metadata = read_project_metadata_record(metadata_path)
    context = build_context_from_metadata_record(
        config=config,
        repo_root=repo_root,
        metadata=metadata,
    )

    if context is None:
        raise ProjectDetectionError(
            "Repository project is unknown. Run 'envctl init [PROJECT]' first."
        )

    return context