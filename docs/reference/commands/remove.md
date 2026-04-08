
# remove

```bash
envctl remove KEY
```

## Philosophy

`remove` changes the shared model destructively.

Use it when the variable should no longer exist as part of the project contract.

## What it does

* removes the contract definition
* removes the value from all persisted profiles
* reports which persisted profiles were inspected and changed

## When to use it

Use `remove` when the variable should no longer be part of the shared project model.

## Caution

This is broader than [`unset`](unset.md). `unset` clears one local value. `remove` removes the variable from the project itself.
