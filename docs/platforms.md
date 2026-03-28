# Platform support

`envctl` is designed to work on Unix‑like systems (Linux, macOS, WSL) where symlinks and POSIX permissions are available. It may work on other platforms with limitations.

## Symlinks

`envctl` relies on symbolic links to link repository `.env.local` files to the vault. On systems where symlinks are not supported (e.g., native Windows without developer mode), the tool will fail with an error. The `doctor` command checks symlink support and will warn if it is not available.

## Permissions

The tool attempts to set `0700` for directories and `0600` for files to keep secrets user‑private. On filesystems that do not support POSIX permissions (e.g., FAT, exFAT, some network shares), these `chmod` calls will fail silently. In such cases, it is the user’s responsibility to ensure the vault directory is not accessible by other users (e.g., by using appropriate filesystem‑level permissions or storing the vault on a private volume).

## Windows

- **Git Bash / WSL**: `envctl` works normally if run inside a Unix‑like environment (Git Bash, WSL, Cygwin) that provides symlink and `chmod` support.
- **Native Windows (cmd/PowerShell)**: Symlinks may require developer mode or administrator privileges. The `doctor` command will indicate whether symlink creation works. Permissions are not enforced via `chmod`; users should store the vault on a secure location.

## Future improvements

- Better Windows support (e.g., using directory junctions as an alternative) may be considered in later versions.
- If you encounter platform‑specific issues, please open an issue on GitHub.
