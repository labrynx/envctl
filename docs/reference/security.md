# Security Reference

**Important:** `envctl` assumes a single-user trusted environment. If your system is compromised, your secrets are compromised.

That is not hidden in the fine print. It is one of the basic assumptions of the tool.

`envctl` is designed to make local environment handling clearer and safer. It is not designed to replace a full shared secrets platform with remote access control, host hardening, and isolation guarantees.

## Security principles

The security posture of `envctl` is intentionally simple and explicit.

Core principles:

* secrets stay outside repositories
* project contracts do not contain secret values
* read-only commands do not mutate local state
* projection is explicit, not hidden
* generated files are artifacts, not sources of truth
* dangerous overwrites stay visible and controlled
* contract mutations are explicit and reviewable
* profile selection stays explicit and inspectable

In other words, `envctl` tries to reduce accidental mistakes more than it tries to hide complexity behind magic.

## The security value of the model itself

A lot of `envctl`’s security story comes from the way it separates concerns:

* **contract**: what variables the project needs
* **storage**: where real values live
* **profiles**: which local value set is active
* **resolution**: how values are selected and validated
* **projection**: how the resolved environment is exposed to tools

In practice, that means:

* `.envctl.schema.yaml` describes requirements only
* local provider state stores real values
* profiles organize stored values explicitly
* `check` validates but does not invent values
* `run`, `sync`, and `export` expose already-resolved state

That separation reduces confusion and avoids competing sources of truth.

## Placeholder expansion guarantees

`envctl` enforces a strict rule for placeholder expansion:

* `${VAR}` is only resolved if `VAR` is declared in the contract
* unknown placeholders are treated as errors
* no implicit fallback to host process variables is performed during expansion

This means that expressions such as:

```text
CACHE_DIR=${HOME}/.cache/demo
```

are invalid unless `HOME` is explicitly declared in the contract.

This is intentional and part of the security model.

It prevents:

* accidental dependency on host-specific variables
* environment drift between machines
* implicit leakage of host environment context into resolved application environments

This guarantees that resolution is deterministic across machines.

In short:

> placeholder expansion is explicit, contract-driven, and deterministic

## Mutation safety

`envctl` also makes an important distinction between **contract mutation** and **value mutation**.

* `add` writes contract + active-profile value
* `set` writes active-profile value only
* `unset` removes active-profile value only
* `remove` removes contract + all persisted profile values

This matters for security and correctness because it keeps shared project requirements separate from machine-local values.

The contract describes what exists. Profiles store what is currently set.

### Important note about `add`

The `add` command changes the repository contract:

```text
.envctl.schema.yaml
```

That has real consequences:

* it creates or updates a variable definition in a versioned file
* it may introduce new required variables for other developers
* it may change the expected environment of the project
* it should be treated as a shared change, not just a local tweak

Because of that:

* `add` should be used intentionally
* contract changes should be reviewed before commit
* inferred metadata should be checked
* teams should treat contract updates like normal code-review material

By contrast:

* `set` and `unset` affect only one active profile
* `remove` also changes the contract and should be treated with similar care

## Contract security rules

The contract is versioned with the project, so it must remain safe to share.

### Allowed

* declaring required and optional variables
* storing descriptions or onboarding notes
* declaring validation rules
* marking variables as sensitive
* providing non-sensitive defaults where appropriate
* declaring patterns and allowed choices
* declaring semantic string formats (`json`, `url`, `csv`) for stricter validation
* storing provider hints for future extensibility

### Not allowed

* storing secret values in the contract
* embedding machine-specific local paths in the contract
* generating secrets during validation
* mutating local state during read-only commands
* defining profile-specific secret values in the contract

The contract describes needs. It does not quietly act as a hidden source of real values.

## Local storage protections

The default local provider stores values outside repositories.

Typical protections include:

* restrictive directory permissions such as `0700`
* restrictive file permissions such as `0600`
* user-owned local paths
* explicit write operations through commands such as `add`, `set`, `unset`, and `fill`
* idempotent value roundtrips for untouched keys during profile rewrites

Permissions are applied on a best-effort basis and depend on the filesystem underneath.

The repository ↔ vault binding is stored in local Git config for the current checkout. That keeps binding local and out of version control, but it also means Git metadata is part of the local operational surface and should be treated accordingly.

Diagnostics are intentionally conservative. For example, some vault checks verify that a file is not world-writable rather than enforcing one exact mode everywhere.

## Profile security rules

Profiles are local value namespaces. They are not access-control boundaries.

That means:

* `dev`, `staging`, and `ci` are names for local value sets
* switching profile changes which local values are resolved
* profiles do not provide encryption
* profiles do not provide privilege separation
* profiles do not enforce environment-specific policy on their own

The safety value of profiles is clarity, not isolation.

## Projection security rules

Projection commands should remain explicit.

### `envctl run`

* injects values into a subprocess in memory
* avoids writing an env file for that workflow
* is usually the safest projection mode when the target tool supports it

### `envctl sync`

* writes a generated env artifact such as `.env.local`
* should validate before writing
* makes it visible that the file is generated
* should follow safe overwrite rules
* `--output PATH` can write resolved secrets to arbitrary filesystem locations

### `envctl export`

* prints shell export lines
* quotes values safely
* should be treated as shell-facing output, not a hidden storage path
* `--format dotenv` prints resolved secrets directly to stdout

Projection should never quietly redefine the source of truth.

## Read-only command guarantees

Commands such as these should remain read-only:

* `check`
* `inspect`
* `explain`
* `doctor`
* `status`
* `profile list`
* `profile path`
* `vault check`
* `vault path`
* `vault show`

They may inspect contract and local state, but they should not:

* write missing values
* repair state implicitly
* generate new secrets
* materialize files as side effects

That boundary matters for user trust.

## `inspect` vs `vault show`

`envctl` exposes two different visibility modes on purpose.

### `inspect`

* shows the resolved environment
* follows contract semantics
* masks sensitive values
* is the right command for understanding runtime state

### `vault show`

* shows stored local values for one physical profile file
* reflects the vault artifact directly
* is useful for low-level debugging
* should be treated more carefully because it is closer to raw local state

This distinction helps avoid confusion between:

* what is stored
* what is resolved
* what is projected

`vault show --raw` requires explicit confirmation before printing unmasked values. That reduces the chance of accidental disclosure in normal terminal use.

## Generated files

A file such as `.env.local`, produced by `envctl sync`, is a generated artifact.

It is:

* useful for compatibility
* derived from resolved state
* not the source of truth
* safe to regenerate

This helps avoid confusion between stored secrets, declared contract, and materialized outputs.

## Limitations

`envctl` has explicit non-goals and limitations.

Current limitations include:

* no encryption at rest in the core model
* no OS keyring integration by default
* no remote access-control model
* no protection against a compromised local account
* no guarantee against exposure on insecure filesystems
* no security isolation between profiles beyond explicit separation of values

These are part of the intended scope. They are not hidden surprises.

## User responsibilities

Users are still responsible for host security.

That includes:

* keeping the local account secure
* storing the vault in a private location
* avoiding shared or insecure filesystems
* keeping generated env artifacts out of version control
* keeping project contracts free of secrets
* understanding when `sync` writes values to disk
* understanding the difference between local values and shared contract definitions
* understanding that profiles are namespaces, not security barriers

`envctl doctor` can help identify obvious readiness or storage problems, but it cannot replace host security.

## Future security direction

Future improvements may include:

* optional provider integrations
* optional encryption helpers outside the core model
* richer diagnostics for insecure local setups
* better shell-specific safety around exports
* more explicit machine-readable validation output
* better profile-aware diagnostics

Even as the tool evolves, the core rule should remain the same:

`envctl` should make local environment handling more explicit and less error-prone, not more magical.

## Summary

The security posture of `envctl` depends heavily on explicit separation:

* contract
* local values
* profiles
* resolution
* projection

That separation is not just an architecture choice. It is also one of the main safety properties of the tool.
