
# guard

```bash
envctl guard secrets
```

## Purpose

`guard secrets` is a safety net.

It checks the staged Git index for envctl-specific secret material before you commit something dangerous.

## What it does

Scans the staged Git index for envctl-specific secret material and exits with a non-zero status when it finds something unsafe to commit.

It currently detects:

* encrypted vault payloads
* canonical master keys
* the current project's legacy raw master key during the compatibility window

## When to use it

Use `guard secrets` when you want a pre-commit safety net against accidentally committing envctl-specific secret material.

## When not to use it

Do not treat `guard` as a general secret scanner for every possible credential in the repository. It is a focused protection layer for envctl-specific artifacts.

## Integration

This is the command used by the Git hook that `envctl init` installs when the current repository can safely adopt `.githooks` as its local hooks path.
