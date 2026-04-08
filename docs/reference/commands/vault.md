
# vault

```bash
envctl vault check
envctl vault show
envctl vault path
envctl vault edit
envctl vault prune
```

## Purpose

The vault is the physical local store.

Vault commands focus on the actual persisted files rather than the higher-level contract model.

## What these commands do

These commands inspect or maintain physical vault files.

## Available subcommands

* `envctl vault check`
* `envctl vault show`
* `envctl vault path`
* `envctl vault edit`
* `envctl vault prune`

## When to use it

Use `vault` commands when you need to inspect or maintain the physical stored state on disk.

## When not to use it

Do not use vault commands when your real question is about the resolved runtime environment. Use [`inspect`](inspect.md) or [`check`](check.md) first.

## Notes

Use vault commands when you need to inspect or maintain the physical state on disk, not when you want the resolved runtime view.

## Related commands

* see [`inspect`](inspect.md) for resolved state
* see [`sync`](sync.md) for generated dotenv artifacts
