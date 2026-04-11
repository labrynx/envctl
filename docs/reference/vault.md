# Vault Reference

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    This page describes the physical vault layout and the command surface for working with stored local values.
    Use it when you need exact storage and command behavior, not the high-level concept.
  </p>
</div>

## Structure

A typical structure looks like this:

```text
vault/
  master.key          ← encryption key when encryption is enabled
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

Checks whether the current vault file exists, can be parsed, and appears usable.

### `show`

```bash
envctl vault show
```

Shows stored values with sensitive entries masked.

### `show --raw`

```bash
envctl vault show --raw
```

Prints unmasked values, but only after explicit confirmation.

### `edit`

```bash
envctl vault edit
```

Opens the current physical vault file in an editor. When encryption is enabled, the file is temporarily decrypted and then re-encrypted after edit.

### `path`

```bash
envctl vault path
```

Shows the path to the current physical vault file.

### `prune`

```bash
envctl vault prune
```

Removes keys that are no longer declared in the contract.

### `encrypt`

```bash
envctl vault encrypt
```

Encrypts plaintext vault profile files for the current project. Requires `encryption.enabled = true`.

### `decrypt`

```bash
envctl vault decrypt
```

Decrypts encrypted vault profile files for the current project back to plaintext. Requires `encryption.enabled = true`.

## Rules and constraints

- the vault lives outside the repository
- the vault stores local values, not shared contract data
- encryption protects vault files, not generated projection artifacts
- profile storage is local and explicit

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Vault concept

Go back to the conceptual role of local storage.

[Read about the vault](../concepts/vault.md)
</div>

<div class="envctl-doc-card" markdown>
### Encryption reference

Open this when the physical vault files are encrypted at rest.

[Open encryption reference](encryption.md)
</div>

<div class="envctl-doc-card" markdown>
### Security reference

Reconnect physical storage details to the broader safety model.

[Open security reference](security.md)
</div>

</div>
