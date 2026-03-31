# Profiles Reference

Profiles are local value namespaces for the same project contract.

They are useful when one machine needs more than one local setup, but the project requirements themselves do not change.

## Commands

### `list`

```bash
envctl profile list
```

Shows the available profiles for the current project.

### `create`

```bash
envctl profile create dev
```

Creates a new explicit profile.

### `copy`

```bash
envctl profile copy dev staging
```

Copies one profile into another. This is useful when you want a starting point instead of filling everything from scratch.

### `remove`

```bash
envctl profile remove staging
```

Removes one explicit profile.

### `path`

```bash
envctl profile path dev
```

Shows the physical path for a profile file.

## Rules

Profiles follow a few important rules:

* profiles do not change the contract
* profiles do not inherit from each other
* profiles are local only

That means profiles are about organizing local values, not about redefining the project.
