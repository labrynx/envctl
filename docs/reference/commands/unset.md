# unset

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>unset</code> clears one local value while leaving the shared contract intact.
    Use it when a key should remain part of the project model but the active profile should stop providing a value for it.
  </p>
</div>

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

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### set

Use this when the local value should change rather than disappear.

[Open set reference](set.md)
</div>

<div class="envctl-doc-card" markdown>
### remove

Use this instead when the variable should stop existing in the shared contract.

[Open remove reference](remove.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles

Reconnect value clearing to the local profile model.

[Read about profiles](../../concepts/profiles.md)
</div>

</div>
