# Metadata and Local State

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    This page covers the supporting metadata that <code>envctl</code> keeps locally.
    Its job is operational continuity and recovery, not becoming a second source of truth.
  </p>
</div>

## What metadata is

Local metadata is the helper state that lets `envctl` reconnect a checkout to the right local project state and recover more safely when paths or local context change.

## Why it matters

`envctl` needs a small amount of local support data for things like:

- project identity
- recovery after a repository move or clone
- continuity across checkouts
- known local paths and related recovery hints

That support layer matters operationally, but it still stays secondary.

## What problem it solves

Metadata solves continuity and recovery. It does not solve shared requirements or local secret storage.

That distinction prevents a common failure mode:

> a helper file quietly becomes the real system model

## What metadata is not

Metadata is not:

- the contract
- the vault
- the resolved environment
- a replacement for profiles

If it started doing those jobs, `envctl` would gain a hidden second model that would be harder to trust and harder to debug.

## How it fits in the system

Keep the roles separate:

- the **contract** is shared repository truth
- the **vault** stores local values
- **binding** connects the checkout to the right project state
- **metadata** helps that binding and recovery story remain stable

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Binding

Start with the identity model that metadata supports.

[Read about binding](binding.md)
</div>

<div class="envctl-doc-card" markdown>
### Vault

Revisit the actual local value layer that metadata never replaces.

[Read about the vault](vault.md)
</div>

<div class="envctl-doc-card" markdown>
### First project

See how local metadata stays in a support role during onboarding.

[Open first project](../getting-started/first-project.md)
</div>

</div>
