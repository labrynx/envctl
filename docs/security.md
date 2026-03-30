# Security

**Important:** `envctl` assumes a single-user trusted environment. If your system is compromised, your secrets are compromised.

## Principles

The security posture of `envctl` is intentionally simple and explicit.

Core principles:

- secrets stay outside repositories
- project contracts do not contain secret values
- read-only commands do not mutate local state
- projection is explicit, not hidden
- generated files are artifacts, not sources of truth
- dangerous overwrites must remain visible and controlled
- contract mutations are explicit and visible

`envctl` is not trying to be a full secret manager. It is trying to be a safe local control plane for environment workflows.

## Core model

`envctl` separates these concerns on purpose:

- **contract**: what variables the project needs
- **storage**: where concrete values live
- **resolution**: how values are selected and validated
- **projection**: how the resolved environment is exposed to tools

In practice, that means:

- `.envctl.schema.yaml` describes requirements only
- local provider state stores real values
- `check` validates but does not invent values
- `run`, `sync`, and `export` project already resolved state

This separation reduces confusion and avoids competing sources of truth.

## Mutation safety model

`envctl` also distinguishes between **contract mutation** and **value mutation**.

- `add` writes contract + local value
- `set` writes local value only
- `unset` removes local value only
- `remove` removes contract + local value

This matters for security because it keeps shared project requirements explicit and prevents accidental drift between repository state and machine-local secrets.

The contract describes what exists.  
The local vault stores what is currently set.

### Important note about `add`

The `add` command **modifies the repository contract** (`.envctl.schema.yaml`).

This has important implications:

- it creates or updates a variable definition in a versioned file
- it may introduce new required variables for other developers
- it may change the expected environment of the project
- it should be treated as a **shared change**, not a purely local action

Because of this:

- `add` should be used intentionally
- changes should be reviewed before committing
- inferred metadata should be verified
- teams should treat contract updates as part of normal code review

By contrast:

- `set` and `unset` only affect local state
- `remove` also mutates the contract and should be treated similarly to `add`

This distinction is critical for both correctness and security.

## Contract security rules

The repository contract is versioned with the project, so it must remain safe to share.

### Allowed

- declaring required and optional variables
- storing descriptions or onboarding notes
- declaring basic validation rules
- marking variables as sensitive
- providing non-sensitive defaults where appropriate
- declaring patterns and allowed choices
- storing provider hints for future extensibility

### Not allowed

- storing secret values in the contract
- embedding machine-specific local paths in the contract
- automatically generating secrets during validation
- mutating local state during read-only commands

The contract describes needs. It does not act as a hidden provider of values.

## Local storage protections

The default local provider stores values outside repositories.

Typical protections include:

- restrictive directory permissions such as `0700`
- restrictive file permissions such as `0600`
- user-owned local paths
- explicit write operations through commands such as `add`, `set`, `unset`, and `fill`

Permissions are applied on a best-effort basis and depend on the underlying filesystem.

## Projection security rules

Projection commands must stay explicit.

### `envctl run`

- injects values into a subprocess environment in memory
- avoids writing an env file to disk for that workflow
- is generally the safest projection mode when supported by the target tool

### `envctl sync`

- writes a derived env artifact such as `.env.local`
- must validate before writing
- makes it clear that the file is generated
- follows safe overwrite rules

### `envctl export`

- prints shell export lines
- quotes values safely
- should be treated as a shell-facing output mode, not as a hidden storage workflow

Projection should never silently redefine the source of truth.

## Read-only command guarantees

Commands such as these should remain read-only:

- `check`
- `inspect`
- `explain`
- `doctor`
- `status`
- `vault check`
- `vault path`
- `vault show`

They may analyze contract and local state, but they should not:

- write missing values
- repair local state implicitly
- generate new secrets
- materialize files as a side effect

That distinction is important for user trust.

## Inspect vs vault visibility

`envctl` intentionally exposes two different visibility modes:

### `inspect`

- shows the **resolved environment**
- respects contract semantics
- masks sensitive values
- is the correct command for understanding runtime state

### `vault show`

- shows the **stored local values**
- reflects the physical vault artifact
- is useful for low-level debugging
- should be treated more carefully because it is closer to raw local state

This distinction helps avoid confusion between:
- what is stored
- what is resolved
- what is projected

## Generated files

A projected file such as `.env.local` produced by `envctl sync` is a generated artifact.

It is:

- useful for compatibility
- derived from resolved state
- not the source of truth
- safe to regenerate

This distinction is important. It avoids confusion between stored secrets, declared contract, and materialized outputs.

## Limitations

`envctl` has explicit non-goals and limitations.

Current limitations include:

- no encryption at rest in the core model
- no OS keyring integration by default
- no remote access control model
- no protection against a compromised local account
- no guarantee against exposure on insecure filesystems

These are not hidden limitations. They are part of the deliberate scope of the tool.

## User responsibilities

Users remain responsible for local system security.

That includes:

- keeping the local account secure
- storing the vault on a private location
- avoiding shared or insecure filesystems
- keeping generated env artifacts out of version control
- keeping project contracts free of secrets
- understanding when `sync` writes values to disk
- understanding the difference between local values and shared contract definitions

`envctl doctor` can help identify obvious readiness or storage problems, but it cannot replace host security.

## Future security direction

Future improvements may include:

- optional provider integrations
- optional encryption helpers outside the core model
- richer diagnostics for insecure local setups
- better shell-specific safety around exports
- more explicit machine-readable validation output

Even as the tool evolves, the core security rule should remain the same:

`envctl` should make local environment handling more explicit and less error-prone, not more magical.

## Summary

The security posture of `envctl` depends on explicit separation:

- contract
- local values
- resolution
- projection

That separation is not just an architecture choice. It is also one of the main security properties of the tool.
