# inspect

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>inspect</code> is the detailed diagnostic view.
    Use it when the short validation answer is not enough and you need to see what the resolved environment actually looks like.
  </p>
</div>

```bash
envctl inspect
envctl inspect KEY
envctl inspect --contracts
envctl inspect --sets
envctl inspect --groups
```

## Purpose

`inspect` is the deep diagnostic view.

Where [`check`](check.md) answers “is this valid?”, `inspect` answers “what exactly is happening?”.

## What it does

* shows the resolved runtime view for the active scope
* includes project context, contract composition, runtime paths, summary, variables, and problems
* shows effective expanded values
* masks sensitive values in normal output
* exposes auxiliary views for resolved contracts, sets, and groups
* fails fast if the selected explicit profile does not exist

## Main forms

### `envctl inspect`

Shows the detailed runtime view for the current scope.

Use this when you want the broad diagnostic picture.

### `envctl inspect KEY`

Shows one variable in detail.

Use this when the real problem is one confusing key, one unexpected default, or one broken placeholder chain.

`envctl inspect KEY` cannot be combined with:

* `--group`
* `--set`
* `--var`
* `--contracts`
* `--sets`
* `--groups`

### Auxiliary views

* `envctl inspect --contracts` shows only the resolved contract graph
* `envctl inspect --sets` shows all resolved contract sets
* `envctl inspect --groups` shows all resolved contract groups
* `envctl --set NAME inspect` focuses the main view on one resolved set
* `envctl --group NAME inspect` focuses the main view on one resolved group

## Scope and selectors

Global selectors apply to the main inspect view:

* `--group LABEL` shows only variables whose normalized `groups` include `LABEL`
* `--set NAME` shows one named contract set
* `--var KEY` shows one explicit variable in the main view

When no selector is provided, `inspect` shows the full contract scope.

## What `inspect` does not do

`inspect` does not:

* change the contract
* change stored values
* generate files
* bypass validation

It is diagnostic only.

## When to use it

Use `inspect`:

* after `check` fails and you need the full picture
* when projection is blocked and you need to understand why
* when you want to see the resolved contract composition
* when a single variable looks wrong and `inspect KEY` is the fastest path

## Typical examples

```bash
envctl inspect
envctl inspect DATABASE_URL
envctl --group Runtime inspect
envctl inspect --contracts
envctl inspect --sets
envctl inspect --groups
```

## Related commands

* use [`check`](check.md) for the short pass-or-fail answer
* use [`status`](status.md) for a smaller readiness snapshot
* use [`run`](run.md) after you understand the resolved state you want to project

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Resolution

Reconnect inspection to the step that computes effective runtime truth.

[Read about resolution](../../concepts/resolution.md)
</div>

<div class="envctl-doc-card" markdown>
### check

Use this when you only need the fast validation answer.

[Open check reference](check.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging

Use the broader workflow when you are isolating the wrong layer.

[Open debugging guide](../../guides/debugging.md)
</div>

</div>
