# fill

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>fill</code> is the interactive command for completing missing local values.
    Use it when the contract is already defined but the active profile still lacks required data.
  </p>
</div>

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

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Vault

Reconnect `fill` to the local storage layer it updates.

[Read about the vault](../../concepts/vault.md)
</div>

<div class="envctl-doc-card" markdown>
### check

Validate again after filling missing values.

[Open check reference](check.md)
</div>

<div class="envctl-doc-card" markdown>
### First project

See where `fill` appears in a normal onboarding flow.

[Open first project](../../getting-started/first-project.md)
</div>

</div>
