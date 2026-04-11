
# remove

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>remove</code> deletes a variable from the shared contract.
    Use it when the project no longer requires that variable at all, not when you only want to clear one local value.
  </p>
</div>

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

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Contract

Go back to the shared layer that `remove` mutates.

[Read about the contract](../../concepts/contract.md)
</div>

<div class="envctl-doc-card" markdown>
### add

Use the opposite shared-model mutation when a variable becomes required.

[Open add reference](add.md)
</div>

<div class="envctl-doc-card" markdown>
### unset

Use this instead when only one active-profile value should be cleared.

[Open unset reference](unset.md)
</div>

</div>
