# Metadata and Local State

`envctl` does not treat a repository-local metadata file as the primary source of truth.

The project contract lives in the repository. Local values live in user-owned local storage. Project identity is derived from the current repository and configuration.

## Core principle

`envctl` separates these concerns intentionally:

- **contract**: what the project needs
- **local state**: which values are available on this machine
- **profiles**: which local value namespace is active
- **projection**: how the resolved environment is exposed to tools
- **identity**: how the current repository is recognized consistently

A repository should not need a mandatory link file just to connect itself to its local environment state.

## Repository identity

Project identity is resolved through an explicit local binding model.

`envctl` distinguishes between:

- a **canonical project id** such as `prj_<16-hex>`
- a **provisional project id** such as `tmp_<hash>`
- a **logical project key** used to identify the project across checkouts when needed

Canonical identity is persisted in local Git config for the current checkout.

When no persisted local binding exists, `envctl` may recover identity from persisted vault state using:

- Git remote URL
- contract metadata such as `meta.project_key`
- previously seen checkout paths (`known_paths`)

If no persisted identity can be found, a provisional identity is used until a command persists a canonical binding.

## Persisted local state

Each vault project stores structured local state used for recovery and continuity.

Typical fields include:

- project slug
- project key
- canonical project id
- repository root
- Git remote when known
- known checkout paths
- timestamps

This state is local operational metadata. It is not the contract and it is not the source of truth for secret values.

## Local state

Local state refers to the values that exist on the current machine for the current project.

Examples include:

- values written with `envctl add`
- values written with `envctl set`
- values collected with `envctl fill`
- values stored by the default local provider

This state is local by design and should not be committed to source control.

## Profiles

Profile state is a refinement of local state.

A profile identifies one explicit local value set for the same project contract.

Examples:

- `local`
- `dev`
- `staging`
- `ci`

The implicit `local` profile is stored at:

```text
<vault-project-dir>/values.env
```

Explicit profiles are stored at:

```text
<vault-project-dir>/profiles/<profile>.env
```

Profiles are local and machine-specific, just like the underlying values.

There is no hidden inheritance between profiles.

## Contract definitions vs local values

In v2.3, `envctl` distinguishes clearly between:

* variables declared in the contract
* values stored locally for those variables
* profiles that namespace those local values

This distinction is visible in command semantics:

* `add` → creates contract definition + active-profile value
* `set` → updates active-profile value only
* `unset` → removes active-profile value only
* `remove` → deletes contract definition + removes values from all persisted profiles

That separation keeps the system explicit:

* the contract defines what exists
* local profile state defines what is currently set

This is one of the key semantic rules of the v2.3 model.

## Optional cache or helper files

`envctl` may use local cache files or helper artifacts for performance or compatibility.

If such files exist, they should follow these rules:

* they are not the source of truth
* they do not contain the project contract
* they are safe to delete and regenerate
* they are ignored by Git where appropriate
* they do not redefine project identity

## What the repository owns

The repository owns the shared contract:

```text
<repo-root>/.envctl.schema.yaml
```

That file may define:

* required and optional variables
* descriptions
* types
* non-sensitive defaults
* sensitivity flags
* patterns
* allowed choices

The repository does **not** own the user's local secret state.

## What local storage owns

Local storage owns the machine-specific values used to satisfy the contract.

Those values may differ from one developer machine to another. That is expected.

Profiles make that separation more expressive, but they do not change ownership:

* the contract is still shared
* profile values are still local
* projected files are still derived artifacts

## What projected files are

A projected file such as `.env.local` produced by `envctl sync` is a generated artifact.

It is:

* useful for compatibility
* derived from resolved state
* not the source of truth
* safe to regenerate

This distinction is important. It avoids confusion between stored secrets, declared contract, and materialized outputs.

## Security note

Any local cache, stored value file, or generated env artifact may reveal information about the developer environment.

Even when such files do not contain the full secret model, they should still be treated carefully:

* keep them out of version control
* store them in private locations
* do not assume they are portable across machines

## Future evolution

Future versions may introduce:

* richer local provider state formats
* optional provider-specific caches
* migration helpers for legacy repository metadata
* clearer machine-readable state inspection
* richer profile inspection and management

Even then, the core rule should remain the same:

the repository contract is shared, profile values are local, and generated artifacts are not the source of truth.

## Summary

Project identity is derived.
Contract is shared.
Profiles namespace local values.
Generated env files are disposable artifacts.

That is the metadata model `envctl` is built around.

## See also

* [Binding](binding.md)
* [Profiles](profiles.md)
* [Resolution](resolution.md)
