#!/usr/bin/env bash
set -Eeuo pipefail

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .[dev]
pytest
