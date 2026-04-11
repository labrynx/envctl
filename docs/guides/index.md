# Guides

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guides</span>
  <p class="envctl-section-intro__body">
    This section is for real workflows.
    Use it when you already know the basic model and want help applying it to Docker, CI, team usage, debugging, or day-to-day work.
  </p>
</div>

## When to use guides

Use Guides when your question sounds like:

- how should I use `envctl` with Docker
- how do profiles fit into a real workflow
- how should a team share contract changes
- how do I debug the right layer

If your question is instead “what does this concept mean?”, go to [Concepts](../concepts/index.md). If you need exact syntax or behavior, go to [Reference](../reference/index.md).

## Workflow guides

<div class="grid cards" markdown>

-   :material-docker:{ .lg .middle } **Docker**

    Use `envctl` with containers without confusing host resolution and container injection.

    [Open Docker guide](docker.md)

-   :material-source-branch:{ .lg .middle } **CI**

    Run `envctl` in pipelines with predictable selection and projection behavior.

    [Open CI guide](ci.md)

-   :material-layers-outline:{ .lg .middle } **Profiles**

    Create, fill, copy, and remove local profiles without mutating the contract.

    [Open profiles guide](profiles.md)

-   :material-account-group-outline:{ .lg .middle } **Team workflows**

    Keep the contract shared while real values stay local to each machine.

    [Open team guide](team.md)

-   :material-bug-outline:{ .lg .middle } **Debugging**

    Debug the right layer instead of guessing at runtime behavior.

    [Open debugging guide](debugging.md)

-   :material-calendar-check-outline:{ .lg .middle } **Daily workflow**

    See the small set of commands that matter most in normal day-to-day use.

    [Open daily workflow](../workflows/daily.md)

-   :material-source-commit:{ .lg .middle } **Hooks**

    Operate the managed Git safety layer when your team uses it.

    [Open hooks guide](hooks.md)

</div>

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Daily workflow

Start with the day-to-day command rhythm most users actually repeat.

[Open daily workflow](../workflows/daily.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging

Open this when reality and expectations stop matching.

[Open debugging guide](debugging.md)
</div>

<div class="envctl-doc-card" markdown>
### Troubleshooting

If you are already in a failure state, start from symptoms instead.

[Open troubleshooting](../troubleshooting/index.md)
</div>

</div>
