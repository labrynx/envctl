# Profiles

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    Profiles let one machine hold more than one local value set for the same contract.
    They exist so you can switch local context without rewriting shared requirements or mutating one single local state over and over.
  </p>
</div>

## What they are

A profile answers this question:

> Which local value set should this machine use right now?

It is a local context selector, not another project definition.

## Why they matter

Without profiles, people usually end up:

- overwriting values in place
- renaming files manually
- keeping several ad-hoc dotenv copies
- forgetting which setup is active

Profiles stop that from becoming normal.

<div class="envctl-callout" markdown>
Same project requirements, different local context — that is the real purpose of profiles.
</div>

## What problem they solve

Profiles let one machine satisfy the same shared contract in multiple valid ways.

Typical examples:

- `local` for normal daily development
- `docker` for a container-oriented setup
- `dev-alt` for another backend or account
- `ci-like` for local reproduction of pipeline assumptions

Explicit selection matters because many “wrong value” problems are really profile-selection problems:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">select profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl --profile local check</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev-alt run -- python app.py</span></code></pre>
</div>

## What they are not

Profiles do not change:

- the contract
- required variables
- shared metadata
- repository-level environment shape

So profiles are not alternate contracts and they are not shared runtime truth.

## How they fit in the system

Profiles sit between local storage and runtime truth:

- the **contract** stays shared
- the **vault** stores local values
- a **profile** selects one local set
- **resolution** computes what is true for this run

That is why profiles pair naturally with validation and runtime selection, but not with shared contract mutation.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Profiles guide

See the operational workflow for creating, filling, copying, and removing profiles.

[Open profiles guide](../guides/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles reference

See the exact selection and storage rules.

[Open profiles reference](../reference/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Resolution

Understand how selected profile values become part of final runtime truth.

[Read about resolution](resolution.md)
</div>

</div>
