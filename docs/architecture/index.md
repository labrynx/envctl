# Architecture

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Architecture</span>
  <p class="envctl-section-intro__body">
    This section is for maintainers and contributors.
    It explains how <code>envctl</code> is structured internally and which boundaries matter if you want the codebase to keep matching the product model.
  </p>
</div>

## When to use this section

Use these pages when your question sounds like:

- what belongs in each implementation layer
- which boundaries are architectural, not accidental
- where compatibility rules still shape the codebase

If you are learning the product itself, go back to [Concepts](../concepts/index.md) or [Guides](../guides/index.md).

<div class="grid cards" markdown>

-   :material-layers-outline:{ .lg .middle } **Layers**

    Understand the main layers of the codebase and what belongs in each one.

    [Read about layers](layers.md)

-   :material-border-all-variant:{ .lg .middle } **Boundaries**

    See why explicit boundaries protect clarity and long-term maintainability.

    [Read about boundaries](boundaries.md)

-   :material-sitemap-outline:{ .lg .middle } **Internal architecture**

    A maintainer-facing view of how the current repository is organized.

    [Read the internal architecture guide](../internals/architecture.md)

-   :material-history:{ .lg .middle } **Compatibility**

    Legacy behaviors and migration notes that still shape the codebase and docs.

    [Read the compatibility guide](../internals/compatibility.md)

</div>

## Why this matters

`envctl` only stays clean if it keeps strong lines between:

- CLI orchestration
- service-level workflows
- domain rules
- repository logic
- adapters and platform concerns

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Layers

Start here for the conceptual codebase shape.

[Read about layers](layers.md)
</div>

<div class="envctl-doc-card" markdown>
### Boundaries

See the implementation limits that protect the product model.

[Read about boundaries](boundaries.md)
</div>

<div class="envctl-doc-card" markdown>
### Internal architecture

Move to the maintainer-facing repository view when you need current ownership details.

[Read the internal architecture guide](../internals/architecture.md)
</div>

</div>
