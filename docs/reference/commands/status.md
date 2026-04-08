
# status

```bash
envctl status
```

## Purpose

`status` is the quick readiness snapshot.

It tells you whether the current project and profile are in a usable state without going into the full detail of `inspect`.

## What it does

* shows a readiness summary
* shows the active profile
* surfaces structured diagnostics when config, contract loading, persisted state, or project binding recovery fail before readiness can be computed
* fails fast if the selected explicit profile does not exist

## When to use it

Use `status` when you want a quick view of what is ready and what still needs attention.

## When not to use it

Do not use `status` when you need the full resolved runtime picture or one-key diagnosis. Use [`inspect`](inspect.md) or [`check`](check.md) for that.

## Related commands

* use [`check`](check.md) for the short pass-or-fail validation gate
* use [`inspect`](inspect.md) for the detailed runtime view
