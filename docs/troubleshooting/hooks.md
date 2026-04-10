# Hooks troubleshooting

This page explains common issues when working with envctl-managed hooks.

## partial_conflict after init

Example:

```
hooks_installed: no
hooks_reason: partial_conflict
```

This means:

- envctl applied some changes
- but could not fully take control of all hooks

### Why it happens

Usually because:

- a hook already exists
- and is not managed by envctl

### How to fix

Check the status:

```
envctl hooks status
```

Then either:

#### Option 1 — let envctl take control

```
envctl hooks install --force
```

#### Option 2 — keep existing hooks

Manually integrate:

```
envctl hook-run pre-commit
```

inside your existing hook script.

---

## Hook is not running

### Possible causes

- envctl is not in PATH
- hook was not installed
- hook was removed manually

### Fix

Check:

```
envctl hooks status
```

Reinstall:

```
envctl hooks repair
```

---

## envctl not found in hook

Error:

```
envctl is not available in PATH in this environment.
```

### Cause

The shell executing the hook cannot resolve `envctl`.

### Fix

- ensure your virtualenv is activated
- or ensure envctl is globally available

---

## Hooks not working on Windows

### Possible causes

- Git Bash vs PowerShell differences
- PATH differences
- missing shell environment

### Fix

- ensure Git uses a POSIX shell (default in Git for Windows)
- ensure envctl is available in PATH for that shell

---

## Conflict with other tools

envctl does not integrate automatically with:

- Husky
- pre-commit
- Git LFS hooks
- custom scripts

### What you can do

#### Option 1 — replace

```
envctl hooks install --force
```

#### Option 2 — integrate manually

Edit your existing hook:

```
envctl hook-run pre-commit
```

---

## Unsupported hooks path

If your Git config uses:

```
core.hooksPath
```

pointing outside the repository, envctl will not modify it.

### Why

envctl only operates inside the repository boundary.

### Fix

- move hooks inside the repo
- or manage them manually

---

## Drifted hooks

A hook is `drifted` when:

- it was managed by envctl
- but has been modified

### Fix

```
envctl hooks repair
```

---

## Missing hooks

A hook is `missing` when it does not exist.

### Fix

```
envctl hooks install
```

---

## Understanding status levels

| Status       | Meaning               |
|--------------|-----------------------|
| healthy      | fully correct         |
| degraded     | fixable issues        |
| conflict     | external interference |

---

## Final note

envctl hooks are a safety layer.

They help prevent mistakes, but they do not guarantee enforcement in all cases.

For full protection, combine them with CI checks.
