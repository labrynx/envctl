# Profiles

Profiles let you keep more than one local value set for the same project.

That is useful when one contract needs to support several real-world setups, such as local development, staging-like testing, or a CI-oriented configuration.

The key point is this:

> profiles change local values, not project requirements

## What a profile is

A profile is a named set of local values.

Examples:

- `local`
- `dev`
- `staging`
- `ci`

Each profile belongs to the same contract. You are not creating a new project definition when you create a new profile. You are only creating another local value namespace for the same project.

## What a profile changes

A profile changes only stored values.

A profile does **not** change:

- contract schema
- required variables
- types
- descriptions
- validation rules

So if a variable is required by the contract, it is required regardless of which profile you use. Profiles do not rewrite the rules. They only change which local values are available under those rules.

## Storage layout

The implicit default profile is stored as:

```text
values.env
```

Explicit profiles are stored as:

```text
profiles/<name>.env
```

For example:

```text
~/.envctl/vault/projects/<slug>--<id>/
  values.env
  profiles/
    dev.env
    staging.env
```

This means `local` is the default value set, while named profiles live alongside it as separate files.

## How profile selection works

Profile selection follows this order:

1. `--profile`
2. `ENVCTL_PROFILE`
3. config `default_profile`
4. `local`

That makes the selection rules easy to inspect. There is a clear order, and `envctl` does not silently pick a profile from hidden state.

## No inheritance

Profiles do not inherit from each other.

There is no:

* fallback chain
* cascading values
* implicit merging

This is intentional. Inheritance sounds convenient until you are debugging a surprising value and have to figure out which profile secretly contributed it.

`envctl` keeps profiles flat so they are easier to reason about.

## Typical usage

```bash
envctl --profile dev run -- app
envctl --profile staging check
```

This gives you a simple way to work with multiple local environments while keeping the shared contract unchanged.

## Profile commands

* `profile list`
* `profile create`
* `profile copy`
* `profile remove`
* `profile path`

## See also

* [Contract](contract.md)
* [Resolution](resolution.md)
