#!/usr/bin/env bash
set -Eeuo pipefail

python3 -m pip install --user -U pip
python3 -m pip install --user .

echo "envctl installed locally."