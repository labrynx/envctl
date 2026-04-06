# Metadata and Local State

`envctl` does not treat a repository-local metadata file as the main source of truth.

That is a deliberate design choice.

The contract belongs to the repository. Real values belong to local storage. Project identity is resolved from the current checkout and local binding state. Those concerns are related, but they are not the same thing, and `envctl` tries hard not to collapse them into one blurry layer.

## The main idea

`envctl` separates these concerns on purpose:

- **contract**: what the project needs
- **local state**: what values exist on this machine
- **profiles**: which local value set is active
- **projection**: how the resolved environment is exposed to tools
- **identity**: how the current repository is recognized consistently

A repository should not need a mandatory local link file just to know which environment belongs to it. That would make the repository itself responsible for machine-local state, which is exactly what `envctl` tries to avoid.

## Repository identity

Project identity is handled through the binding model.

`envctl` distinguishes between:

- a **canonical project id** such as `prj_<16-hex>`
- a **provisional project id** such as `tmp_<hash>`
- a **logical project key** used when a project needs to be recognized across checkouts

The canonical identity is persisted in local Git config for the current checkout.

If no persisted local binding exists yet, `envctl` may still be able to recover the project identity from existing vault state using things like:

- Git remote URL
- contract metadata such as `meta.project_key`
- previously seen checkout paths (`known_paths`)

If nothing reliable can be recovered, `envctl` falls back to a provisional identity until a command persists a canonical binding.

## Persisted local state

Each vault project can also store some structured local state to help with recovery and continuity.

Typical fields may include:

- project slug
- project key
- canonical project id
- repository root
- Git remote when known
- known checkout paths
- timestamps

This is operational metadata. It helps `envctl` reconnect things locally, but it is not the contract and it is not the source of truth for secrets.

## What local state means

Local state is the set of values that exist on the current machine for the current project.

That includes things like:

- values written with `envctl add`
- values written with `envctl set`
- values collected with `envctl fill`
- values stored by the default local provider

This state is local by design. It should not be committed to source control.

## Profiles

Profiles are one layer inside local state.

A profile gives a name to one local value set for the same project contract. That is how you can keep `local`, `dev`, `staging`, or `ci` values on one machine without changing the shared requirements of the project.

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

Profiles are still local state. They do not change who owns the values, and they do not become part of the repository contract.

## Contract definitions vs local values

In v2.3, `envctl` makes a clear distinction between:

* variables declared in the contract
* values stored locally for those variables
* profiles that group those local values

You can see that distinction in command behavior:

* `add` → creates a contract definition and stores an initial value in the active profile
* `set` → updates the active-profile value only
* `unset` → removes the active-profile value only
* `remove` → deletes the contract definition and removes values from all persisted profiles

This is one of the core semantic rules of the model:

* the contract defines what exists
* local profile state defines what is currently set

## Optional cache or helper files

`envctl` may create local cache files or helper artifacts for compatibility or convenience.

If those files exist, they should follow these rules:

* they are not the source of truth
* they do not contain the project contract
* they are safe to delete and regenerate
* they should be ignored by Git where appropriate
* they do not redefine project identity

That way, helper files stay helpers. They do not quietly become part of the model.

## What the repository owns

The repository owns the shared contract:

```text
<repo-root>/.envctl.yaml
<repo-root>/.envctl.schema.yaml  # legacy fallback
```

That file may describe:

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

Those values may vary from one machine to another. That is normal and expected.

Profiles make that separation easier to work with, but they do not change ownership:

* the contract is still shared
* profile values are still local
* projected files are still generated artifacts

## What projected files are

A file such as `.env.local`, created by `envctl sync`, is a generated artifact.

It is:

* useful for compatibility
* derived from resolved state
* not the source of truth
* safe to regenerate

This distinction matters because it keeps three separate ideas from getting mixed together:

* what the project declares
* what the machine stores
* what a tool happens to consume right now

## Security note

Any local cache, stored value file, or generated env artifact may reveal something about the local developer environment.

Even when those files do not contain the full secret model, they should still be handled carefully:

* keep them out of version control
* store them in private locations
* do not assume they are portable across machines

## Future evolution

Future versions may add things like:

* richer local provider state formats
* optional provider-specific caches
* migration helpers for older repository metadata
* clearer machine-readable state inspection
* better profile inspection and management

Even if those features appear, the core rule should stay the same:

the contract is shared, profile values are local, and generated artifacts are not the source of truth.

## Summary

Project identity is resolved through local binding. The contract is shared. Profiles organize local values. Generated env files are disposable outputs.

That is the metadata model `envctl` is built around.

## See also

* [Binding](binding.md)
* [Profiles](profiles.md)
* [Resolution](resolution.md)
