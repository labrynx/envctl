
# unset

```bash
envctl unset KEY
```

## Philosophy

`unset` clears local state without changing shared intent.

The variable remains part of the contract, but the active profile no longer provides a value for it.

## What it does

* removes the value from the active profile
* keeps the contract definition
* fails fast if the selected explicit profile does not exist

## When to use it

Use `unset` when you want to clear a local value without removing the variable from the project.
