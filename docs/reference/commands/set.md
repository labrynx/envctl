
# set

```bash
envctl set KEY VALUE
```

## Philosophy

`set` changes local state only.

It updates the active profile value without modifying the shared contract.

## What it does

* updates the value only
* does not modify the contract
* fails fast if the selected explicit profile does not exist

## When to use it

Use `set` when the contract already exists and you only want to change the active-profile value.

## Typical use

This is the command you use most often once the contract is already defined.
