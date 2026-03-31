# Vault Reference

The vault is where `envctl` stores local values.

It lives outside the repository and is meant to hold the machine-local data needed to satisfy the project contract.

## Structure

A typical structure looks like this:

```text
vault/
  projects/<slug>--<id>/
    values.env
    profiles/
```

The default `local` profile is stored in `values.env`. Explicit profiles are stored under `profiles/`.

## Commands

### `check`

```bash
envctl vault check
```

Checks the current vault file and reports things such as:

* whether it exists
* whether it can be parsed
* whether permissions look reasonable

### `show`

```bash
envctl vault show
```

Shows stored values with sensitive entries masked.

This is useful when you want to inspect the physical vault content without printing raw secrets.

### `show --raw`

```bash
envctl vault show --raw
```

Prints unmasked values, but only after explicit confirmation.

This extra step exists to reduce accidental disclosure during normal terminal use.

### `edit`

```bash
envctl vault edit
```

Opens the current physical vault file in an editor.

This is a low-level operation and is best used when you really need to work directly with the stored file.

### `path`

```bash
envctl vault path
```

Shows the path to the current physical vault file.

This is useful when you want to inspect where the active profile is stored on disk.

### `prune`

```bash
envctl vault prune
```

Removes keys that are no longer declared in the contract.

This is useful after contract cleanup, when old values are still hanging around in local storage.
