# Binding

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    Binding is how <code>envctl</code> reconnects a repository checkout to the correct local project state.
    It answers an identity question, not a configuration question.
  </p>
</div>

## What binding is

Binding answers this question:

> If I run `envctl` from this checkout, which local project state should it use?

That matters because repositories move, get copied, and get reopened from paths `envctl` has not seen before.

## Why binding matters

Without an explicit binding model, project identity would have to be guessed from folder names or filesystem paths. That is brittle.

Binding makes identity:

- explicit
- local to the checkout
- recoverable after moves or re-clones

## What problem binding solves

Binding solves repository identity, not runtime truth.

It tells `envctl` where the local state for this checkout lives. It does **not** define:

- the contract
- the active values
- the active profile
- the resolved runtime environment

## What binding is not

Binding is not:

- the contract
- the vault
- profile selection
- metadata itself

Metadata may support binding, but binding is the identity link, not the storage of all local facts.

## How it fits in the system

The conceptual split is:

- the **contract** defines shared requirements
- the **vault** stores local values
- a **profile** selects one local value set
- **binding** connects this checkout to the right local project state

That separation is what keeps repository identity from leaking into the value model.

## Canonical project id

Each bound project has a canonical id:

```text
prj_<16-hex>
```

That id lives in local Git config under:

```text
envctl.projectId
```

This keeps binding local to the checkout instead of turning it into shared repository data.

## Binding states

A checkout may appear as:

- **local**: normal explicit local binding exists
- **recovered**: `envctl` restored project identity from existing local state
- **derived**: a temporary working identity is being used until a canonical one is established

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Metadata and local state

See the supporting local metadata that helps binding stay recoverable.

[Read about metadata](metadata.md)
</div>

<div class="envctl-doc-card" markdown>
### First project

See where binding shows up in a normal onboarding flow.

[Open first project](../getting-started/first-project.md)
</div>

<div class="envctl-doc-card" markdown>
### Team workflows

Connect checkout identity back to shared repository workflows.

[Open team guide](../guides/team.md)
</div>

</div>
