#!/usr/bin/env bash
set -Eeuo pipefail

python3 -m venv .venv
source .venv/bin/activate

pip install -U pip
pip install -e .

echo "Dev environment ready."
