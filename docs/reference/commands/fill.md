
# fill

```bash
envctl fill
```

## Philosophy

`fill` helps you complete local state from shared intent.

It is an interactive recovery command for missing required values.

## What it does

* prompts for missing required values
* uses contract metadata when available
* fails fast if the selected explicit profile does not exist

## When to use it

Use `fill` when the contract is valid but the active profile is missing required values.

## Typical use

`fill` is useful after onboarding, after switching machines, or after adding new required variables to the contract.
