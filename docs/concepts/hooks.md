# Hooks

envctl can install and manage a minimal set of Git hooks to ensure that sensitive data never gets committed by mistake.

This is not a general-purpose hook system. It is a very focused safety mechanism.

## What envctl does

envctl manages only two hooks:

- `pre-commit`
- `pre-push`

Both run:

```
envctl guard secrets
```

This means:

- your commits are checked before they are created
- your pushes are checked before they leave your machine

If a secret is detected, the operation is blocked.

## Managed vs foreign hooks

envctl classifies hooks into two categories:

### Managed hooks

Hooks created by envctl:

- contain the marker `managed-by: envctl`
- match the expected wrapper exactly
- are fully controlled by envctl

### Foreign hooks

Any hook that:

- does not contain the envctl marker
- or has been modified manually
- or comes from another tool (Husky, Git LFS, etc.)

envctl will not modify these by default.

## Why envctl does not merge hooks

envctl does **not** try to merge its logic into existing hooks.

That is intentional.

Hook scripts can be fragile:

- execution order matters
- shell flags (`set -e`) can change behavior
- some scripts use `exec`
- others depend on environment variables

Trying to automatically inject logic would make the system unreliable.

Instead, envctl follows a simple rule:

> If a hook is not managed by envctl, it is left untouched.

## What happens on conflict

If a hook already exists and is not managed by envctl:

- envctl reports a conflict
- envctl does not overwrite it
- the system is considered partially configured

You can then decide how to proceed:

- keep the existing hook and integrate manually
- or let envctl take control with `--force`

## Scope and limitations

envctl hooks are designed to:

- prevent accidental leaks of secrets
- provide consistent behavior across environments

They are **not** designed to:

- replace other hook systems
- run arbitrary commands
- enforce policies in CI
- guarantee enforcement against `--no-verify`

They are a local safety layer, not a complete enforcement system.
