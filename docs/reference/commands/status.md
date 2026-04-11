# status

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>status</code> is the quick readiness snapshot.
    Use it when you want a compact summary of whether the current project and profile are usable.
  </p>
</div>

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

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### First project

See where `status` helps answer “what is already ready?” during onboarding.

[Open first project](../../getting-started/first-project.md)
</div>

<div class="envctl-doc-card" markdown>
### check

Use this when you need explicit validation rather than a summary snapshot.

[Open check reference](check.md)
</div>

<div class="envctl-doc-card" markdown>
### inspect

Use this when the compact snapshot is not enough detail.

[Open inspect reference](inspect.md)
</div>

</div>
