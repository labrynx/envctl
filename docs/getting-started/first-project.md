# First project

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Getting started</span>
  <p class="envctl-section-intro__body">
    Use this page when you have cloned a real repository and want a little more context than the quickstart.
    The goal is still practical: get from fresh checkout to a validated, runnable local setup without mixing shared requirements and local values.
  </p>
</div>

## Starting point

This page assumes:

- the repository already uses `envctl`
- you want to prepare your machine, not redesign the project contract
- you want a first successful run and a reliable next step if something is missing

## Step 1: create your local config

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">config</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl config init</span></code></pre>
</div>

This creates your machine-level config. It controls tool behavior such as vault location and default profile. It does not define the project contract and it does not store the project’s shared requirements.

## Step 2: initialize the repository

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">init</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl init</span></code></pre>
</div>

`init` prepares the checkout for normal `envctl` use. It may establish local structure, binding, and managed hook wrappers where supported.

!!! note "`init` prepares local state, not secrets"
    `init` can normalize local structure and recover project state. It does not invent or guess the real values your machine needs.

## Step 3: inspect what is already ready

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">status</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl status</span></code></pre>
</div>

This is the fastest way to answer the practical question:

> what is already ready, and what is still missing?

If you also want to confirm the managed hook layer, check it directly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">hooks</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl hooks status</span></code></pre>
</div>

## Step 4: fill missing required values

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">fill</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl fill</span></code></pre>
</div>

This prompts only for values that are both:

- required by the contract
- missing from the active profile

## Step 5: validate

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">check</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span></code></pre>
</div>

If validation fails, stay at this layer first. Fix the model before debugging a downstream runtime.

## Step 6: run the project

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">run</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl run -- python app.py</span>
<span class="envctl-doc-terminal__line">$ envctl run -- npm start</span>
<span class="envctl-doc-terminal__line">$ envctl run -- make dev</span></code></pre>
</div>

For most local workflows, `run` is the right default because it keeps projection explicit and ephemeral.

## If you need a second local context

Create a named profile instead of mutating one local setup in place:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">profiles</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile create dev</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev fill</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev check</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev run -- python app.py</span></code></pre>
</div>

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Mental model

See the compact explanation of the layers you just used.

[Open mental model](mental-model.md)
</div>

<div class="envctl-doc-card" markdown>
### Daily workflow

Move from first setup into the normal rhythm of working with `envctl`.

[Open daily workflow](../workflows/daily.md)
</div>

<div class="envctl-doc-card" markdown>
### Command reference

Look up exact command behavior once the onboarding flow already makes sense.

[Open command reference](../reference/commands/index.md)
</div>

</div>
