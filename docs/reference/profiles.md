# Profiles Reference

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    This page covers the exact profile selection and storage rules.
    Use it when you already know what profiles are and need the precise mechanics.
  </p>
</div>

## Selection order

The active profile is resolved in this order:

1. `--profile`
2. `ENVCTL_PROFILE`
3. config `default_profile`
4. `local`

## Storage rules

- `values.env` is the canonical file for the implicit `local` profile
- explicit profiles are stored as `profiles/<name>.env`
- `local` does not use `profiles/local.env`
- explicit profiles must exist before use

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

Copies one profile into another.

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

- profiles do not change the contract
- profiles do not inherit from each other
- profiles are local only
- `add`, `set`, `unset`, and `fill` target the active profile only
- `remove` removes the key from the contract and all persisted profiles

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Profiles concept

Go back to what profiles mean in the model.

[Read about profiles](../concepts/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles guide

See the workflow for creating, filling, copying, and removing profiles.

[Open profiles guide](../guides/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Configuration reference

Reconnect selection rules to the config defaults that participate in them.

[Open configuration reference](configuration.md)
</div>

</div>
