
# project

```bash
envctl project bind ID
envctl project unbind
envctl project rebind
envctl project repair
```

## Purpose

Project commands preserve repository identity and local continuity.

They exist to keep the binding between a repository and its local vault state understandable and recoverable.

## What these commands do

These commands manage repository identity and local binding continuity.

## Available subcommands

* `envctl project bind ID`
* `envctl project unbind`
* `envctl project rebind`
* `envctl project repair`

## When to use it

Use `project` commands when local binding is broken, ambiguous, moved, or needs recovery.

## When not to use it

Do not reach for `project` commands for normal day-to-day value changes. They are identity and recovery tools, not routine environment mutation commands.

## Notes

These commands matter most when local binding is broken, moved, or needs recovery.

## Related commands

* see [`status`](status.md) and [`inspect`](inspect.md) when you are diagnosing whether the local project context itself is healthy
