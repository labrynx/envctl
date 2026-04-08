<section class="envctl-splash">
  <div class="envctl-splash__content">
    <p class="envctl-eyebrow">Stop .env drift</p>
    <h1>Your <code>.env.local</code> works... until it doesn't.</h1>
    <p class="envctl-lead">
      <code>envctl</code> keeps environments consistent by separating shared requirements from local values, then making runtime behavior explicit.
    </p>
    <div class="envctl-hero__actions">
      <a class="md-button md-button--primary" href="getting-started/index.md">Get started</a>
      <a class="md-button" href="concepts/index.md">Learn the model</a>
    </div>
    <p class="envctl-hero-note">
      No hidden source of truth.<br />
      No guessing which value won.
    </p>
  </div>
  <a class="envctl-splash__scroll" href="#why-it-exists" aria-label="Scroll to overview">
    <span>See how it works</span>
    <span aria-hidden="true">↓</span>
  </a>
</section>

<div class="envctl-home-body" markdown="1">

<div class="grid cards envctl-splash-highlights" markdown>

-   **Shared requirements**

    The repo says what must exist.

-   **Local values**

    Each machine keeps real values out of Git.

-   **Explicit runtime**

    You can inspect what wins before you run anything.

</div>

## Why it exists { #why-it-exists }

Different machines behave differently.

Onboarding breaks.

CI fails in ways you cannot reproduce.

`envctl` gives you a cleaner model:

- a **contract** for what must exist
- a **vault** for local values outside version control
- **profiles** for different contexts
- deterministic **resolution**
- safe **projection** only when needed

---

## Choose your path

<div class="grid cards envctl-splash-paths" markdown>

-   **New here**

    Install the CLI, initialize your local setup, and run the shortest working path.

    [Go to getting started](getting-started/index.md)

-   **Want the model**

    Learn contract, vault, resolution, and projection before you dive into commands.

    [Go to concepts](concepts/index.md)

-   **Need exact behavior**

    Look up command semantics, flags, and configuration details.

    [Go to reference](reference/index.md)

-   **Something broke**

    Start from symptoms, causes, and recovery paths instead of guessing.

    [Go to troubleshooting](troubleshooting/index.md)

</div>

---

## The model at a glance

`envctl` is not just a CLI. It is a model:

<div class="grid cards envctl-splash-model" markdown>

-   :material-file-document-outline:{ .lg .middle } **Contract**

    The shared definition of required variables, defaults, validation, and intent.

-   :material-shield-lock-outline:{ .lg .middle } **Vault**

    Local values stay outside Git, where they belong.

-   :material-layers-outline:{ .lg .middle } **Profiles**

    Switch context without duplicating fragile files across machines.

-   :material-source-branch:{ .lg .middle } **Resolution**

    Values are resolved in a deterministic order, not by guesswork.

-   :material-export:{ .lg .middle } **Projection**

    Inject values into a process, export them, or generate files only when needed.

-   :material-magnify-scan:{ .lg .middle } **Diagnostics**

    See what is missing, what is selected, and why something fails.

</div>

---

## Read next

Understand the core model before you dive into command detail:

<div class="grid cards envctl-read-next" markdown>

-   **Contract**

    Start with the shared definition of what the project expects.

    [Read about the contract](concepts/contract.md)

-   **Resolution**

    See how `envctl` decides what is actually true at runtime.

    [Read about resolution](concepts/resolution.md)

-   **Projection**

    Understand why generated files and process injection stay downstream of the model.

    [Read about projection](concepts/projection.md)

</div>

</div>
