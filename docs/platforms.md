# Platform support

`envctl` is designed to work on Unix-like systems (Linux, macOS, WSL) where symlinks and POSIX permissions are available. It may work on other platforms with limitations.

## Symlinks

`envctl` relies on symbolic links to link repository `.env.local` files to the vault. On systems where symlinks are not supported (for example native Windows without developer mode), the tool will fail with an error. The `doctor` command checks symlink support and will warn if it is not available.

This dependency on symlinks is central to the current model:

- the repository holds a link
- the vault holds the secret
- the two must remain separate

## Permissions

The tool attempts to set `0700` for directories and `0600` for files to keep secrets user-private. On filesystems that do not support POSIX permissions (for example FAT, exFAT, some network shares), these `chmod` calls will fail silently.

In such cases, it is the user’s responsibility to ensure the vault directory is not accessible by other users, for example by using appropriate filesystem-level permissions or storing the vault on a private volume.

## Windows

- **Git Bash / WSL**: `envctl` works normally if run inside a Unix-like environment that provides symlink and `chmod` support.
- **Native Windows (cmd/PowerShell)**: symlinks may require developer mode or administrator privileges. The `doctor` command will indicate whether symlink creation works. Permissions are not enforced via `chmod`; users should store the vault on a secure location.

## Schema and team workflows

The future schema-based workflow (`.envctl.schema.yaml`, `check`, `fill`) is platform-neutral in concept, but still depends on the same repository-to-vault model underneath.

That means platform limitations remain fundamentally tied to:

- symlink support
- local filesystem behavior
- vault privacy guarantees

## Possible future improvements

- Better Windows support, for example alternative linking strategies where safe and predictable
- More diagnostics around platform limitations
- Clearer machine-readable reporting for unsupported features

If you encounter platform-specific issues, please open an issue on GitHub.
