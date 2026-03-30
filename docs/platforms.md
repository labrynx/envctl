# Platform support

`envctl` is designed to work on Unix-like systems first, including Linux, macOS, and WSL.

The v2 model reduces platform coupling by avoiding symlinks as a core requirement. The central workflows are now based on:

- contract loading
- local value storage
- resolution and validation
- subprocess environment injection
- optional file materialization

That makes the tool easier to support across heterogeneous environments.

## Core assumptions

`envctl` assumes the platform can provide, at minimum:

- filesystem access for local storage
- subprocess execution for `envctl run`
- standard text file handling for contracts and generated env files

The tool works best in environments that also provide:

- Git command availability
- POSIX-like permissions
- predictable shell behavior

Binding persistence relies on local Git config for checkout-local identity.
This works best in environments where Git metadata remains stable and accessible from the same execution context.

## Permissions

The tool attempts to use restrictive permissions for local storage, typically:

- `0700` for directories
- `0600` for files

On filesystems that do not support POSIX permissions, these operations may fail silently or only partially apply.

In such cases, users are responsible for choosing a secure storage location and avoiding shared or insecure filesystems.

## Linux and macOS

Linux and macOS are the primary target environments.

Typical behavior is straightforward:

- local storage works as expected
- Git detection is predictable
- subprocess execution for `run` is reliable
- `sync` and `export` workflows behave naturally

## WSL

WSL is expected to work well when `envctl` is run inside the Linux environment.

This is usually the best option on Windows when you want predictable permissions and shell behavior.

Typical benefits include:

- more predictable file permissions
- better compatibility with POSIX-oriented shell output
- simpler subprocess behavior for `run`
- more natural handling of generated `.env.local` artifacts

Binding persistence relies on local Git config for checkout-local identity.
This works best in environments where Git metadata remains stable and accessible from the same execution context.

## Native Windows

Native Windows support is possible, but behavior depends more heavily on the execution environment.

Important considerations include:

- `chmod`-style permission semantics do not map directly
- shell export behavior differs between shells
- subprocess behavior may vary depending on PowerShell, cmd, or other terminals
- path conventions differ from Unix-like environments

The v2 architecture is still more portable than a symlink-based model, but shell-specific and permission-specific differences remain relevant.

Binding persistence relies on local Git config for checkout-local identity.
This works best in environments where Git metadata remains stable and accessible from the same execution context.

## Shell compatibility

`envctl export` is primarily aimed at POSIX-like shells.

If broader shell support is added later, it should be explicit rather than implicit. For example, future support may include shell-specific output modes instead of trying to guess the target shell automatically.

At the moment:

- `run` is the most portable projection mode
- `sync` is the most tool-compatible file-based projection mode
- `export` is the most shell-specific mode

That distinction is useful when choosing which workflow to rely on across platforms.

## Projection portability

Among the projection modes:

### `run`

- usually the most portable
- injects values in memory
- avoids shell-specific and filesystem-specific assumptions

### `sync`

- platform-neutral as plain text
- depends on how the consuming tool reads `.env.local`
- should remain explicit

### `export`

- POSIX-oriented
- depends on shell behavior
- should be treated as shell-specific output, not a universal projection format

## Generated files

`envctl sync` produces plain text env artifacts such as `.env.local`.

This is generally platform-neutral, but the consuming tools may still behave differently across platforms. For that reason:

- `sync` should remain explicit
- generated files should be easy to inspect
- users should not rely on hidden platform-specific behavior

## Diagnostics

`envctl doctor` is intended to help users identify local readiness issues such as:

- invalid config
- missing contract
- insecure local storage location
- repository detection problems
- environment compatibility issues

Diagnostics should remain read-only and descriptive.

## Possible future improvements

Potential future platform work may include:

- clearer Windows-specific guidance
- shell-specific export formats
- more detailed readiness diagnostics
- better reporting for unsupported permission models

## Summary

The v2 model is less fragile across platforms because it no longer depends on repository symlinks as a core mechanism.

The main portability concerns now are:

- filesystem security
- shell behavior
- subprocess execution
- path handling

That is a much healthier platform surface than the previous link-based model.
