"""Configuration management service."""

from __future__ import annotations

from pathlib import Path

from envctl.config.defaults import (
    get_default_config_path,
    get_default_env_filename,
    get_default_vault_dir,
)
from envctl.errors import ConfigError
from envctl.utils.filesystem import ensure_dir, write_json_atomic


def _to_tilde_path(path: Path) -> str:
    """Return a user-friendly path using `~` when it is inside the home directory."""
    home = Path.home().resolve()
    resolved = path.expanduser().resolve()

    try:
        relative = resolved.relative_to(home)
    except ValueError:
        return str(resolved)

    if not relative.parts:
        return "~"

    return str(Path("~") / relative)


def run_config_init() -> Path:
    """Create the default envctl config file if it does not already exist.

    Behavior:
    - creates the parent config directory when needed
    - refuses to overwrite an existing config file
    - writes user-friendly default values
    - keeps config creation explicit rather than implicit

    TODO(v1.1):
    - add `--force` for explicit overwrite
    - add flags for customizing vault_dir and env_filename
    - add YAML output support when YAML config becomes supported
    """
    config_path = get_default_config_path()

    if config_path.exists():
        raise ConfigError(f"Config file already exists: {config_path}")

    ensure_dir(config_path.parent)
    write_json_atomic(
        config_path,
        {
            "vault_dir": _to_tilde_path(get_default_vault_dir()),
            "env_filename": get_default_env_filename(),
        },
    )

    return config_path