# Using hooks

envctl can automatically install Git hooks to protect your repository from leaking secrets.

## Installing hooks

When you run:

```
envctl init
```

envctl will try to install managed hooks.

You may see:

```
hooks_installed: yes
```

or:

```
hooks_installed: no
hooks_reason: partial_conflict
```

A conflict usually means there are existing hooks.

## Checking hook status

Run:

```
envctl hooks status
```

You will see the state of each hook:

- `healthy`
- `missing`
- `drifted`
- `foreign`
- `unsupported`

## Installing hooks manually

If hooks are missing:

```
envctl hooks install
```

This will:

- create missing hooks
- fix broken managed hooks
- leave foreign hooks untouched

## Repairing hooks

If something looks wrong:

```
envctl hooks repair
```

This ensures that all supported hooks are functional.

## Forcing installation

If you want envctl to take control of existing hooks:

```
envctl hooks install --force
```

This will overwrite foreign hooks for supported hook names.

Use this only if you are sure.

## Removing hooks

To remove managed hooks:

```
envctl hooks remove
```

This:

- deletes envctl-managed hooks
- leaves foreign hooks untouched

## What hooks actually do

Each managed hook is a simple wrapper:

```
envctl hook-run <hook-name>
```

Which internally runs:

```
envctl guard secrets
```

If secrets are found:

- the operation fails
- the commit or push is blocked

## When to use hooks

Hooks are useful when you want:

- immediate feedback before committing
- protection against accidental leaks
- consistent behavior across developers

They are not a replacement for CI checks.
