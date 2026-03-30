# Profiles

Profiles namespace local values for the same contract.

They allow multiple local environments without changing project requirements.

## What a profile is

A profile is a **named set of values**.

Examples:

- `local`
- `dev`
- `staging`
- `ci`

## What a profile changes

A profile changes only:

- stored values

A profile does NOT change:

- contract schema
- required variables
- types
- descriptions
- validation rules

## Storage layout

Implicit profile:

```text
values.env
```

Explicit profiles:

```text
profiles/<name>.env
```

Example:

```text
~/.envctl/vault/projects/<slug>--<id>/
  values.env
  profiles/
    dev.env
    staging.env
```

## Profile selection

Precedence:

1. `--profile`
2. `ENVCTL_PROFILE`
3. config `default_profile`
4. `local`

## No inheritance

Profiles do not inherit from each other.

There is no:

* fallback chain
* cascading values
* implicit merging

This keeps resolution predictable.

## Typical usage

```bash
envctl --profile dev run -- app
envctl --profile staging check
```

## Profile commands

* `profile list`
* `profile create`
* `profile copy`
* `profile remove`
* `profile path`

## See also

* [Contract](contract.md)
* [Resolution](resolution.md)
