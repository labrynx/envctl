# Architecture

This section explains how `envctl` is structured internally and why those boundaries matter.

The goal is not architecture for architecture’s sake.

The goal is to keep the system understandable, testable, and resistant to accidental coupling.

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
