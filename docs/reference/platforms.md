# Platform Support

`envctl` is designed for Unix-like systems first, including Linux, macOS, and WSL.

That does not mean other environments are impossible. It means the main workflows are designed around platforms where filesystem behavior, subprocess execution, and shell conventions are easier to keep consistent.

## Why platform support is simpler in the v2 model

Earlier link-based approaches tend to create platform-specific problems quickly. In the v2 model, `envctl` relies much less on repository symlinks and much more on a cleaner set of workflows:

- contract loading
- local value storage
- profile-aware value selection
- resolution and validation
- subprocess environment injection
- optional file materialization

That gives the tool a healthier portability surface. There are still platform differences, of course, but fewer of them are baked into the core model.

## Core assumptions

At a minimum, `envctl` assumes the platform can provide:

- filesystem access for local storage
- subprocess execution for `envctl run`
- standard text file handling for contracts and generated env files

The tool works best when the environment also provides:

- Git command availability
- POSIX-like permissions
- predictable shell behavior

Binding persistence relies on local Git config for checkout-local identity, so the experience is best where Git metadata is stable and available from the same execution context.

## Permissions

`envctl` tries to use restrictive permissions for local storage, typically:

- `0700` for directories
- `0600` for files

On filesystems that do not support POSIX permissions, those settings may fail silently or apply only partially.

In those cases, the user is responsible for choosing a secure storage location and avoiding shared or insecure filesystems.

Current diagnostics are intentionally conservative. For example, some checks verify that storage is **not world-writable**, rather than requiring one exact permission mode everywhere.

## Linux and macOS

Linux and macOS are the main target environments.

Typical behavior is straightforward:

- local storage behaves as expected
- explicit profile files behave as expected
- Git detection is stable
- subprocess execution for `run` is reliable
- `sync` and `export` fit naturally into common workflows

## WSL

WSL is expected to work well when `envctl` runs inside the Linux environment rather than through a mixed Windows shell setup.

This is usually the best path on Windows if you want more consistent permissions and shell behavior.

Typical benefits include:

- more predictable file permissions
- better compatibility with POSIX-style shell output
- simpler subprocess behavior for `run`
- more natural handling of `.env.local`
- straightforward handling of explicit profile files

## Native Windows

Native Windows support is possible, but behavior depends more on the shell and filesystem details of the environment.

Things to keep in mind:

- `chmod`-style semantics do not map directly
- shell export behavior varies between shells
- subprocess behavior may differ across PowerShell, cmd, or other terminals
- path conventions differ from Unix-like environments

The v2 architecture is still easier to support than a symlink-heavy model, but these differences still matter.

## Shell compatibility

`envctl export` is mainly aimed at POSIX-like shells.

If broader shell support is added later, it should be explicit. A future shell-specific mode is better than trying to guess the target shell automatically.

Right now, the rough rule is:

- `run` is the most portable projection mode
- `sync` is the most compatible file-based projection mode
- `export` is the most shell-specific mode

## Projection portability

### `run`

- usually the most portable
- injects values in memory
- avoids many shell-specific and filesystem-specific assumptions

### `sync`

- plain text and generally portable
- still depends on how the consuming tool reads `.env.local`
- should stay explicit

### `export`

- oriented toward POSIX-like shells
- depends on shell behavior
- should be treated as shell-facing output, not a universal format

## Generated files

`envctl sync` produces plain text env files such as `.env.local`.

That output is usually portable as a file, but the tools that consume it may still behave differently from platform to platform. For that reason:

- `sync` should remain explicit
- generated files should stay easy to inspect
- users should not depend on hidden platform-specific behavior

The same idea applies to profile vault files. They are plain text local artifacts, not cross-platform workflow magic.

## Diagnostics

`envctl inspect` is now the main command for local readiness and detailed state inspection. The deprecated `envctl doctor` alias still helps identify issues such as:

- invalid config
- missing contract
- insecure local storage
- repository detection problems
- environment compatibility issues
- missing or unexpected active profile files

Diagnostics should stay read-only and descriptive.

## Possible future improvements

Possible future platform work may include:

- clearer Windows-specific guidance
- shell-specific export formats
- more detailed readiness diagnostics
- better reporting for unsupported permission models
- more explicit profile-related portability guidance

## Summary

The v2 model is less fragile across platforms because it no longer depends on repository symlinks as a core mechanism.

The main portability concerns now are:

- filesystem security
- shell behavior
- subprocess execution
- path handling

That is a much better place to be than relying on path-based link tricks.
