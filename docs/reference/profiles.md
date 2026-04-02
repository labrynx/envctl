# Profiles Reference

Profiles are local value namespaces for the same project contract.

They are useful when one machine needs more than one local setup, but the project requirements themselves do not change.

## Selection order

The active profile is resolved in this order:

1. `--profile`
2. `ENVCTL_PROFILE`
3. config `default_profile`
4. `local`

## Storage rules

* `values.env` is the canonical file for the implicit `local` profile
* explicit profiles are stored as `profiles/<name>.env`
* `local` does not use `profiles/local.env`
* explicit profiles must exist before use

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

Use this before running commands against a named profile such as `dev` or `staging`.

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
* `add`, `set`, `unset`, and `fill` target the active profile only
* `remove` removes the key from the contract and all persisted profiles

That means profiles are about organizing local values, not about redefining the project.
