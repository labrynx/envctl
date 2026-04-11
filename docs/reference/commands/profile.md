# profile

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>profile</code> manages explicit local value namespaces.
    Use it when one machine needs more than one local context for the same shared contract.
  </p>
</div>

```bash
envctl profile list
envctl profile create NAME
envctl profile copy SRC DST
envctl profile remove NAME
envctl profile path [NAME]
```

## Purpose

Profiles are local namespaces of values.

They let you switch context without duplicating fragile files or muddying the shared contract.

## What these commands do

These commands manage explicit local profiles.

## Available subcommands

* `envctl profile list`
* `envctl profile create NAME`
* `envctl profile copy SRC DST`
* `envctl profile remove NAME`
* `envctl profile path [NAME]`

## When to use it

Use `profile` commands when one machine needs more than one local value set for the same contract.

## When not to use it

Do not use profiles as alternate contracts. Profiles change local values, not project requirements.

## Notes

Named profiles must be created explicitly before use.

## Related commands

* see [`set`](set.md), [`fill`](fill.md), and [`check`](check.md) for the commands that operate on the active profile

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Profiles concept

Go back to what profiles mean in the model.

[Read about profiles](../../concepts/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles guide

See the practical workflow for create, copy, fill, and remove.

[Open profiles guide](../../guides/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles reference

See the exact selection and storage rules.

[Open profiles reference](../profiles.md)
</div>

</div>
