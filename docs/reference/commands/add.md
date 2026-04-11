# add

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>add</code> changes the shared project contract.
    Use it when the application now requires a new variable as part of the repository-owned environment model.
  </p>
</div>

```bash
envctl add KEY VALUE
```

## Philosophy

`add` changes the shared model.

Use it when the project itself now requires a new variable, not when you only want to tweak your own local value.

## What it does

* updates the contract
* stores the value in the active profile
* may infer metadata for the contract entry
* does not initialize other profiles implicitly

## Useful options

* `--type` to set variable type explicitly
* `--format` to set semantic string format such as `json`, `url`, or `csv` when `--type string`
* `--required` / `--optional`
* `--sensitive` / `--non-sensitive`
* `--description`
* `--default`
* `--example`
* `--pattern`
* `--choice`

## When to use it

Use `add` when the variable becomes part of the shared project contract.

## When not to use it

Do not use `add` when the contract already exists and you only want to change your local value. In that case, use [`set`](set.md).

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Contract

Go back to the shared layer that `add` modifies.

[Read about the contract](../../concepts/contract.md)
</div>

<div class="envctl-doc-card" markdown>
### remove

Use the inverse shared-model mutation when a variable should stop existing.

[Open remove reference](remove.md)
</div>

<div class="envctl-doc-card" markdown>
### Team workflows

See how contract changes behave in a shared repository workflow.

[Open team guide](../../guides/team.md)
</div>

</div>
