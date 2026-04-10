#!/bin/sh
set -eu

HOOK_NAME="${HOOK_NAME:-unknown}"

# Run secret guard only on hooks that gate changes before they leave the workstation.
case "$HOOK_NAME" in
  pre-commit|pre-push)
    if command -v uv >/dev/null 2>&1; then
      uv run envctl guard secrets
    else
      envctl guard secrets
    fi
    ;;
esac

# Preserve optional Git LFS hook integration when git-lfs is available locally.
if command -v git-lfs >/dev/null 2>&1; then
  git lfs "$HOOK_NAME" "$@"
else
  echo >&2 "⚠️ git-lfs not found (skipping)"
fi
