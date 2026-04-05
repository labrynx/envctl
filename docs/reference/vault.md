# Vault Reference

The vault is where `envctl` stores local values.

It lives outside the repository and is meant to hold the machine-local data needed to satisfy the project contract.

## Structure

A typical structure looks like this:

```text
vault/
  master.key          ← encryption key (present only when encryption is enabled)
  projects/<slug>--<id>/
    values.env
    profiles/
```

The default `local` profile is stored in `values.env`. Explicit profiles are stored under `profiles/`.

Vault values are handled as logical strings during read/write operations. Rewriting a profile through `set` or `unset` should not progressively escape untouched structured values.

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

When encryption is enabled, the file is transparently decrypted to a temporary
file before the editor opens, then re-encrypted after the editor exits.  The
temporary file is always removed.

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

### `encrypt`

```bash
envctl vault encrypt
```

Encrypts all plaintext vault profile files for the current project.

Run this once after setting `encryption.enabled = true` in your config to migrate
existing plaintext vault files.  Files already encrypted are skipped automatically.

Requires `encryption.enabled = true` in config.  See the
[Encryption Reference](encryption.md) for full details.

### `decrypt`

```bash
envctl vault decrypt
```

Decrypts all encrypted vault profile files for the current project back to plain text.

Run this before setting `encryption.enabled = false` to avoid leaving `envctl`
unable to read its own files.  Files already in plaintext are skipped.

Requires `encryption.enabled = true` in config.
