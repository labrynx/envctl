# Contract

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    The contract is the shared definition of what the project environment requires.
    It is the repository-owned layer of the model: names, requirements, safe defaults, and structure — not one machine’s actual values.
  </p>
</div>

## What it is

A contract answers one question:

> What does this project expect to exist in its environment?

That makes it shared intent, not local truth.

## Why it matters

Without a contract, environment handling drifts into habit:

- copy someone else’s file
- tweak it locally
- hope CI matches
- repeat the same onboarding explanation later

The contract stops that by making requirements explicit, reviewable, and versioned.

<div class="envctl-callout" markdown>
If the team can discuss it, review it, and commit it safely, it probably belongs in the contract.
</div>

## What problem it solves

The contract gives the team one stable place to answer:

- which variables matter
- which ones are required
- what shape the environment has
- what should be validated before runtime

That is why contract changes belong in Git:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">shared contract change</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl add API_KEY</span>
<span class="envctl-doc-terminal__line">$ git add .envctl.yaml</span>
<span class="envctl-doc-terminal__line">$ git commit -m "require API_KEY"</span></code></pre>
</div>

That commit changes project requirements. It does not distribute anyone’s real secret.

## What it is not

The contract is not the place for:

- developer-specific secrets
- personal machine URLs or credentials
- copied dotenv files
- generated projection artifacts
- anything that turns the repository into a secret transport layer

Those belong to local storage, not to the shared model.

## How it fits in the system

The contract is the first layer in the chain:

- the **contract** defines requirements
- the **vault** stores local values
- **profiles** select one local context
- **resolution** computes what is true for this run
- **projection** hands that result to the runtime

Validation makes the contract operational: `envctl check` asks whether the currently resolved local environment satisfies the shared contract.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Vault

See the local layer that satisfies the contract on one machine.

[Read about the vault](vault.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles

See how the same contract can be satisfied through different local contexts.

[Read about profiles](profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Team workflows

See how contract changes behave in a shared repository.

[Open team guide](../guides/team.md)
</div>

</div>
