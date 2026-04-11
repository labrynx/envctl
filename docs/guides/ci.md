# CI

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guide</span>
  <p class="envctl-section-intro__body">
    In CI, <code>envctl</code> should act as an explicit validation and projection layer.
    The goal is not to “fix things quietly”, but to fail clearly when the selected environment is not valid.
  </p>
</div>

## The wrong mental model for CI

The most dangerous CI setup is usually the one that looks convenient:

- values appear from unclear places
- missing state gets patched silently
- pipelines become harder to trust
- failures turn into guesswork

That is exactly what `envctl` should help you avoid.

<div class="envctl-callout" markdown>
In CI, prefer **explicit validation** and **narrow projection**.
Do not use CI as a place to invent local state or repair missing values interactively.
</div>

## The default CI path

For the most common pipeline shape, validate the environment directly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">ci check</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span></code></pre>
</div>

That gives you the fastest explicit answer:

- the selected environment satisfies the contract
- or it does not

## Use an explicit CI profile when you have one

If the pipeline should validate a dedicated CI-local value set, select it intentionally:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">ci profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ ENVCTL_PROFILE=ci envctl check</span></code></pre>
</div>

Or, if your workflow prefers CLI flags globally:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">explicit profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl --profile ci check</span></code></pre>
</div>

The key thing is not *which syntax* you choose.

It is that the choice is explicit and easy to read later.

## When CI needs the runtime environment, not just validation

Sometimes CI does not only need pass/fail validation. Sometimes the next step needs the resolved environment itself.

At that point, choose the narrowest handoff that fits the downstream tool.

### Option 1: run the command directly

If the next step can receive environment variables through a subprocess, use `run`:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">run</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl run -- make integration-test</span>
<span class="envctl-doc-terminal__line">$ envctl run -- pytest</span></code></pre>
</div>

This is usually the cleanest option, because nothing has to be written to disk.

### Option 2: export a dotenv payload

If a downstream step expects dotenv-style content, export it explicitly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">export</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl export --format dotenv > /tmp/app.env</span></code></pre>
</div>

Use this when another tool wants a dotenv file-like handoff.

### Option 3: select only part of the contract

If the pipeline only needs a subset, use selectors instead of projecting everything:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">scoped ci</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl --group Runtime check</span>
<span class="envctl-doc-terminal__line">$ envctl --set docker_runtime export --format dotenv</span>
<span class="envctl-doc-terminal__line">$ envctl --var DATABASE_URL inspect</span></code></pre>
</div>

That keeps CI tighter and easier to reason about.

## What not to do in CI

There are a few patterns worth avoiding.

### Do not use `fill`

`fill` is interactive by design.

That is useful locally, but wrong for CI. A pipeline should not pause and ask for missing values.

### Do not treat generated files as the source of truth

If you use `sync` or exported dotenv output in CI, remember what it is:

- projection output
- not the source of truth
- not a replacement for the contract or vault model

### Do not hide profile selection

If your pipeline depends on `ci`, say so explicitly. Silent assumptions here make failures harder to debug.

## A good CI outcome

A good CI integration with `envctl` produces one of two outcomes:

- the pipeline passes because the selected environment satisfies the contract
- the pipeline fails with explicit diagnostics about what is missing or invalid

That is the right kind of strictness.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### check

See the command that acts as the fast validation gate.

[Open check reference](../reference/commands/check.md)
</div>

<div class="envctl-doc-card" markdown>
### run

Use subprocess projection when the next CI step can consume env vars directly.

[Open run reference](../reference/commands/run.md)
</div>

<div class="envctl-doc-card" markdown>
### Projection

Understand the difference between validating, exporting, syncing, and running.

[Read about projection](../concepts/projection.md)
</div>

</div>
