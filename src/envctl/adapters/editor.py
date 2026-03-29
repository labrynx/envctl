# src/envctl/adapters/editor.py

from __future__ import annotations

import os
import shlex
import shutil
import subprocess

from envctl.errors import ExecutionError


def resolve_editor() -> list[str]:
    visual = os.environ.get("VISUAL", "").strip()
    if visual:
        return shlex.split(visual)

    editor = os.environ.get("EDITOR", "").strip()
    if editor:
        return shlex.split(editor)

    for candidate in ("nano", "vi"):
        path = shutil.which(candidate)
        if path:
            return [path]

    raise ExecutionError("No editor found. Set VISUAL or EDITOR.")


def open_file(path: str) -> None:
    command = [*resolve_editor(), path]

    try:
        completed = subprocess.run(command, check=False)
    except OSError as exc:
        raise ExecutionError(f"Failed to launch editor: {command[0]}") from exc

    if completed.returncode != 0:
        raise ExecutionError(f"Editor exited with code {completed.returncode}")
