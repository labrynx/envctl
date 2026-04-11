# set

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>set</code> updates the active profile only.
    Use it when the shared contract stays the same and only your current local value needs to change.
  </p>
</div>

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

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Profiles

Reconnect `set` to the local context that owns the updated value.

[Read about profiles](../../concepts/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### unset

Use this when the local value should be cleared rather than changed.

[Open unset reference](unset.md)
</div>

<div class="envctl-doc-card" markdown>
### Team workflows

See the rule for `add` versus `set` in shared repositories.

[Open team guide](../../guides/team.md)
</div>

</div>
