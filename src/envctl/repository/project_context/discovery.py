from __future__ import annotations

from pathlib import Path

from envctl.domain.error_diagnostics import ProjectBindingDiagnostics
from envctl.errors import ProjectDetectionError


def find_vault_dir_by_project_id(projects_dir: Path, project_id: str) -> Path | None:
    """Return the vault directory for one persisted project id."""
    if not projects_dir.exists():
        return None

    matches = [
        path
        for path in projects_dir.iterdir()
        if path.is_dir() and path.name.endswith(f"--{project_id}")
    ]
    if not matches:
        return None

    if len(matches) > 1:
        options = ", ".join(sorted(path.name for path in matches))
        raise ProjectDetectionError(
            f"Multiple vault directories found for project id '{project_id}': {options}",
            diagnostics=ProjectBindingDiagnostics(
                category="multiple_vault_directories",
                project_id=project_id,
                matching_directories=tuple(sorted(matches)),
                suggested_actions=("envctl project bind",),
            ),
        )

    return matches[0]
