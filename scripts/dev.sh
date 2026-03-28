#!/usr/bin/env bash
set -Eeuo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e .[dev]

echo "Development environment ready."
