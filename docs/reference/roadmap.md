# Roadmap

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Supporting reference</span>
  <p class="envctl-section-intro__body">
    This page captures the product direction that current documentation and implementation are reinforcing.
    It is for orientation, not for exact command behavior or release-by-release promises.
  </p>
</div>

This page is a high-level view of where `envctl` came from and what direction the product is reinforcing.

## What the product has already clarified

The major direction is already established:

* the contract is the shared definition of environment requirements
* local values stay local
* profiles are explicit
* resolution is deterministic
* projection is explicit

That is the core shape of the product now.

## What recent evolution has reinforced

Recent work has mostly pushed `envctl` in three directions:

### 1. Clearer environment model

The tool moved away from “environment files first” toward:

* contract-driven requirements
* explicit local state
* better runtime explainability

### 2. Better local multiplicity

Profiles became first-class so one machine can keep several local contexts without redefining the project.

### 3. Better visibility and recovery

Commands such as `check`, `inspect`, `status`, and the project/vault tooling make it easier to understand:

* what is required
* what is missing
* what was resolved
* what is physically stored
* how to recover from broken local state

## What the roadmap still points toward

The product direction continues to favor:

* explicit behavior over magic
* local-first workflows
* stronger explainability
* cleaner boundaries between contract, local values, runtime, and projection

## Current engineering priority

The current priority is repository consolidation, not product expansion.

That means near-term engineering work should prefer:

* reducing operational ambiguity
* tightening contributor workflows
* reinforcing tests in sensitive paths
* improving security clarity and guard rails
* keeping architectural boundaries healthy as the codebase grows

Feature work should only displace this priority when it directly reduces risk, maintenance cost, or ambiguity for existing workflows.

## What this page is not

This is not a version-by-version changelog and it is not a promise of exact future releases.

For concrete release detail, use the changelog and release notes instead.

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Concepts

Go back to the model the roadmap is reinforcing.

[Open concepts](../concepts/index.md)
</div>

<div class="envctl-doc-card" markdown>
### Architecture

See the maintainers’ view of the boundaries that support this direction.

[Open architecture overview](../architecture/index.md)
</div>

<div class="envctl-doc-card" markdown>
### Distribution

Connect roadmap direction to the current release-hardening policy.

[Open distribution reference](distribution.md)
</div>

</div>
