# Local state and project identity

`envctl` v2 does not treat a repository-local metadata file as the primary source of truth.

The project contract lives in the repository. Local values live in user-owned local storage. Project identity is derived from the current repository and configuration.

## Core principle

`envctl` separates these concerns intentionally:

- **contract**: what the project needs
- **local state**: which values are available on this machine
- **projection**: how the resolved environment is exposed to tools
- **identity**: how the current repository is recognized consistently

A repository should not need a mandatory link file just to connect itself to its local environment state.

## Repository identity

Project identity is derived dynamically from the current repository.

Typical identity inputs may include:

- Git remote URL when available
- repository root path as a fallback
- repository directory name as a human-readable slug

That identity is used to derive stable local storage locations without requiring the repository to own secret linkage state.

## Local state

Local state refers to the values that exist on the current machine for the current project.

Examples include:

- values written with `envctl set`
- values collected with `envctl fill`
- values stored by the default local provider

This state is local by design and should not be committed to source control.

## Optional cache or helper files

`envctl` may use local cache files or helper artifacts for performance or compatibility.

If such files exist, they should follow these rules:

- they are not the source of truth
- they do not contain the project contract
- they are safe to delete and regenerate
- they are ignored by Git where appropriate
- they do not redefine project identity

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

The repository does **not** own the user's local secret state.

## What local storage owns

Local storage owns the machine-specific values used to satisfy the contract.

Those values may differ from one developer machine to another. That is expected.

Local storage should remain private, explicit, and outside the repository.

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

Even then, the core rule should remain the same:

the repository contract is shared, local values are local, and generated artifacts are not the source of truth.
