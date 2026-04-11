# Vault

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    The vault is the local storage layer where real environment values live.
    It exists so the repository can describe shared requirements without becoming the place where actual secrets or machine-specific values are stored.
  </p>
</div>

## What it is

The vault answers one question:

> Where do the real local values live on this machine?

That includes actual credentials, local URLs, and other concrete values that satisfy the contract here.

## Why it matters

Without a local storage layer, teams usually fall into one of two bad patterns:

- secrets drift into repository-visible files
- every developer invents a different local storage habit

The vault makes the boundary explicit: the contract is shared, but real values stay local.

<div class="envctl-callout" markdown>
The vault is local truth, not shared truth.
</div>

## What problem it solves

The vault solves safe locality:

- one machine stores its own real values
- onboarding does not require copying someone else’s env file
- secret handling stops being confused with project definition

That is why commands like `fill` matter:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">fill local values</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl fill</span></code></pre>
</div>

That command supplies missing local values. It does not edit the shared model.

## What it is not

The vault is not:

- the contract
- a public config file
- a team secret-sharing channel
- a generated dotenv artifact

If those boundaries blur, the model becomes much harder to trust.

## How it fits in the system

The vault is one layer in a chain:

- the **contract** defines requirements
- the **vault** stores real local values
- **profiles** select which local set is active
- **resolution** computes effective runtime truth
- **projection** hands that truth to tools

Optional encryption strengthens the storage layer, but it does not change the conceptual split.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Contract

Revisit the shared layer the vault is meant to satisfy locally.

[Read about the contract](contract.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles

See how one machine can hold more than one local value set safely.

[Read about profiles](profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Encryption

Go deeper into protection for local stored values.

[Open encryption reference](../reference/encryption.md)
</div>

</div>
