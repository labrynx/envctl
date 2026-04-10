# Daily Workflow

This is the most common way to use `envctl` day to day.

Once a project is initialized and your values are in place, most work comes down to a small set of repeated actions: run the app, change a value, inspect the current state, and debug a variable when something feels off.

## Run your app

```bash
envctl run -- <command>
```

For most day-to-day work, `run` is the default choice. It injects the resolved environment directly into the subprocess, so you usually do not need to materialize `.env.local`.

## Change a value

```bash
envctl set KEY VALUE
```

Use `set` when you want to change a local value in the active profile without changing the shared project contract.

## Inspect the current state

```bash
envctl inspect
```

Use `inspect` when you want to understand what the runtime view looks like right now.

This is especially useful if a value is coming from a default, a profile, or the process environment and you want to see the result clearly.

## Debug one variable

```bash
envctl inspect KEY
```

Use `inspect KEY` when the problem is really about one key, not the whole environment. `explain KEY` still works for now, but it is deprecated.

## Switch environment

```bash
envctl --profile dev run -- app
```

Use a profile when you want the same project contract with a different local value set.

## Summary

A simple rule of thumb is:

* use `run` to execute
* use `set` for local changes
* use `inspect` to understand what is going on

If you need to verify the local Git safety net itself, add:

```bash
envctl hooks status
```
