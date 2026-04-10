# Common errors

This page is for situations where `envctl` is already telling you something went wrong, but you still need to understand what the failure actually means.

The goal is not just to patch symptoms. The goal is to connect what you see to the underlying cause.

!!! tip "If diagnosis stops being quick, jump to Recovery"
    This page is for fast symptom-to-cause interpretation. If the fix turns into a multi-step repair path, use [Recovery](recovery.md).

## Missing required values

### What you see

Typically:

* `envctl check` fails
* `envctl run`, `sync`, or `export` refuse to project
* diagnostics mention missing required keys

### What it means

The selected profile and contract defaults do not produce a complete valid environment for the current scope.

This is usually not a command bug. It means the model is doing its job and refusing to invent values silently.

### How to fix it

Validate first:

```bash
envctl check
```

Then fill missing values interactively if that fits the workflow:

```bash
envctl fill
```

If you need to understand one confusing key, inspect it directly:

```bash
envctl inspect DATABASE_URL
```

### Why this happens

Resolution only uses the active profile plus contract defaults. It does not quietly read undeclared host environment variables to make missing values disappear.

* [Resolution](../concepts/resolution.md)

## Unknown or invalid placeholder references

### What you see

Typically:

* `check` reports placeholder reference problems
* `run`, `sync`, or `export` fail before projection
* a value references `${VAR}`, but `VAR` is missing or undeclared

### What it means

A placeholder chain cannot resolve under the contract rules.

Either:

* the referenced key is not declared in the contract
* the referenced key is declared but still has no selected value
* the placeholder syntax is malformed

### How to fix it

Inspect the broken key:

```bash
envctl inspect APP_URL
```

Then confirm that every `${VAR}` reference points to a declared contract key and that those referenced keys can resolve cleanly.

If the intent is real, add the missing contract key first rather than assuming host shell inheritance.

### Why this happens

Placeholder expansion is contract-only. `envctl` does not treat `${HOME}` or similar host variables as automatic fallback inputs unless they are part of the contract.

* [Resolution](../concepts/resolution.md)

## Wrong active profile

### What you see

Typically:

* values look correct in one workflow and wrong in another
* `check` or `run` behaves differently than expected
* a command fails because the selected explicit profile does not exist

### What it means

You are either using the wrong profile or assuming that profiles inherit from each other.

Profiles are explicit and isolated local value sets.

### How to fix it

Check which profile you intended to use and select it explicitly:

```bash
envctl --profile dev check
```

If the profile does not exist yet, create it first:

```bash
envctl profile create dev
```

Then fill or set the missing values for that profile.

### Why this happens

Profiles do not inherit implicitly and there is no hidden cascade between them.

* [Profiles](../concepts/profiles.md)

## Generated `.env.local` is stale or misleading

### What you see

Typically:

* the app behaves differently from what you expected
* a previously generated dotenv file no longer matches current local values
* someone starts treating `.env.local` as the main state store

### What it means

A projection artifact has been mistaken for the source of truth.

The resolved environment changed, but the generated file was not regenerated, or it was edited manually.

### How to fix it

Regenerate the file explicitly:

```bash
envctl sync
```

If a file is not actually required, prefer direct subprocess injection instead:

```bash
envctl run -- python app.py
```

### Why this happens

Projection outputs are derived artifacts. They are useful handoff formats, but they are not the contract or the vault.

* [Projection](../concepts/projection.md)

## Invalid config or runtime mode

### What you see

Typically:

* commands fail before normal resolution starts
* diagnostics mention config loading or runtime mode problems

### What it means

The user-level `envctl` config is malformed, inconsistent, or contains unsupported settings.

### How to fix it

Inspect the config file and compare it with the documented config shape:

* [Configuration](../reference/configuration.md)

If needed, recreate the base config:

```bash
envctl config init
```

Then reapply only the settings you actually need.

### Why this happens

Config is upstream of most command flows. If config loading fails, later steps such as resolution and projection may never start.

## Broken or ambiguous binding

### What you see

Typically:

* commands fail while discovering project context
* diagnostics mention repository identity, binding, or project recovery
* local state seems to belong to the wrong checkout or no checkout at all

### What it means

`envctl` cannot confidently reconnect the current repository checkout to the correct local project state.

### How to fix it

Start with the recovery path:

```bash
envctl project repair
```

If you know you need a lower-level operation, use `project bind`, `unbind`, or `rebind` intentionally.

### Why this happens

Binding is how `envctl` connects a repository checkout to the right local vault state. If that link is missing or ambiguous, later commands cannot trust what “current project” means.

* [Binding](../concepts/binding.md)
* [Recovery](recovery.md)

## Managed hooks are missing, drifted, or conflicted

### What you see

Typically:

* `envctl hooks status` exits non-zero
* output mentions `missing`, `drifted`, `foreign`, or `unsupported`
* `init` warns that managed hooks were not fully installed

### What it means

The envctl-owned Git protection layer is not currently in a healthy state.

Common causes:

* the managed hook files were deleted or edited
* another tool already owns one of the supported hook names
* the effective Git hooks path resolves outside the repository perimeter

### How to fix it

Start with inspection:

```bash
envctl hooks status
```

If the hooks are envctl-managed but damaged or missing:

```bash
envctl hooks repair
```

If a supported hook is owned by something else and you really want envctl to take over that hook name:

```bash
envctl hooks install --force
```

### Why this happens

`envctl` keeps hook management intentionally narrow and non-invasive. It only owns its own supported wrappers and refuses to manage hooks outside the repository perimeter.
