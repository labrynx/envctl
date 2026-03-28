"""Configuration management service."""

from __future__ import annotations

from pathlib import Path

from envctl.config.writer import write_default_config_file


def run_config_init() -> Path:
    """Create the default envctl config file."""
    return write_default_config_file()
