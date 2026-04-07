# Encryption Reference

`envctl` supports optional symmetric encryption of vault profile files at rest.

When enabled, every vault file (`values.env`, `profiles/*.env`) is stored as
an AES-128-CBC + HMAC-SHA256 Fernet token instead of plain text.  The rest of
the tool — commands, profiles, resolution, projection — works identically.

## Enabling encryption

Add the following block to `~/.config/envctl/config.json`:

```json
{
  "encryption": { "enabled": true }
}
```

Then migrate existing plaintext vault files:

```bash
envctl vault encrypt
```

Files that are already encrypted are skipped automatically.

## Disabling encryption

Decrypt first, then disable:

```bash
envctl vault decrypt
```

Then set `"encryption": { "enabled": false }` (or remove the `encryption` key)
in your config.  If you disable encryption before decrypting, `envctl` will
fail to read the existing encrypted files.

## How the key works

On first use, `envctl` generates a random 32-byte key and writes it to:

```text
<vault_dir>/master.key
```

Default location: `~/.envctl/vault/master.key`

The key file is created with mode `0400` (owner read-only).  No passphrase is
required.  The key is loaded once per process and used for all vault I/O within
that run.

## Key backup

**Losing `master.key` means all encrypted vault data is unrecoverable.**

Treat `master.key` like any other secret credential:

- Back it up separately from the vault directory.
- Do not commit it to version control.
- When migrating to a new machine, copy both the vault directory **and**
  `master.key`.

## vault edit with encryption

`envctl vault edit` works normally when encryption is enabled.  Internally:

1. The selected profile file is decrypted to a temporary file (mode `0600`)
   in the same directory as the vault file.
2. The editor opens the temporary file.
3. After the editor exits, the temporary file is re-encrypted back to the
   original path.
4. The temporary file is deleted unconditionally, even if the editor errors.

The temporary file is never named with a `.env` extension so it is not
accidentally picked up by other tools.

## Vault structure with encryption enabled

The directory layout is identical to plaintext mode.  Files have the same names
and permissions.  The only difference is that their content is a Fernet token
(a URL-safe base64-encoded binary blob) rather than dotenv text.

```text
~/.envctl/vault/
  master.key          ← new; mode 0400
  projects/
    myapp--prj_abc/
      values.env      ← Fernet-encrypted dotenv content
      profiles/
        staging.env   ← Fernet-encrypted dotenv content
```

## Migration commands

### `envctl vault encrypt`

Encrypts all plaintext profile files for the current project.  Files already
encrypted are skipped.

```bash
envctl vault encrypt
```

### `envctl vault decrypt`

Decrypts all encrypted profile files for the current project back to plain text.
Files already in plaintext are skipped.

```bash
envctl vault decrypt
```

## Security properties

| Property | Value |
|---|---|
| Algorithm | AES-128-CBC + HMAC-SHA256 (Fernet) |
| Key size | 32 bytes (256-bit; 128 for encryption + 128 for signing) |
| IV | Randomly generated per write |
| Integrity | HMAC-SHA256 — tampering is detected on read |
| Key storage | `master.key` on disk, mode `0400` |
| Passphrase | Not required (single-user model) |
| Secret names visible | No — the entire file is encrypted, including key names |

Fernet provides authenticated encryption.  A file encrypted with one key cannot
be decrypted or silently altered with a different key.

## Limitations

Encryption at rest protects vault files on disk.  It does **not** protect:

- Values in memory during a running `envctl` process.
- Values injected into subprocess environments by `envctl run`.
- Generated files produced by `envctl sync` — those remain plain text.
- The vault key itself (`master.key`).

`envctl` is a single-user local tool.  Encryption here defends against
accidental disclosure (backup exposure, shared filesystem, shoulder surfing)
rather than against a compromised local account.


## Master key format

`envctl` now stores new master keys in a canonical, self-identifying format:

```text
ENVCTL-MASTER-KEY-V1:<key-id>:<base64-key>
```

- `prefix` is the stable format marker and version
- `key-id` is the public short identifier derived from the real key bytes
- `base64-key` is the Fernet key material used to encrypt vault files

Legacy raw Fernet keys are still accepted during the transition period, but they are deprecated and scheduled for removal in `v2.6.0`. When `envctl` loads a legacy key from disk and can safely rewrite the file, it migrates the file automatically to the canonical format without changing the real secret.

`ENVCTL_VAULT_KEY` also accepts both formats during the transition period. Legacy values supplied only through the environment are not persisted automatically.
