# Quickstart

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Getting started</span>
  <p class="envctl-section-intro__body">
    This page is the shortest safe path from zero to a validated first run.
    It is intentionally practical: install <code>envctl</code>, initialize local state, fill what is missing, validate, and run.
  </p>
</div>

## When to use this page

Use this page when:

- you want the fastest successful setup
- you do not need the deeper theory first
- you are comfortable following a short command sequence

If you want more context before touching a repository, read [Mental model](mental-model.md) first.

## Shortest safe path

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">quickstart</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl config init</span>
<span class="envctl-doc-terminal__line">$ envctl init</span>
<span class="envctl-doc-terminal__line">$ envctl fill</span>
<span class="envctl-doc-terminal__line">$ envctl check</span>
<span class="envctl-doc-terminal__line">$ envctl run -- python app.py</span></code></pre>
</div>

## What each step is doing

### 1. `envctl config init`

Creates your user-level config file so the CLI has machine-local defaults such as vault location and default profile.

### 2. `envctl init`

Prepares the repository for contract-based workflows and establishes local state where needed.

### 3. `envctl fill`

Prompts only for required values that are still missing from the active profile.

### 4. `envctl check`

Validates the resolved environment against the shared contract.

### 5. `envctl run -- …`

Projects the resolved environment into one subprocess without writing a dotenv file by default.

<div class="envctl-callout" markdown>
Prefer `run` unless another tool explicitly needs a file on disk. Use `sync` only for file-based consumers.
</div>

## Optional next step: use a named profile

If one machine needs more than one local setup, make that explicit:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">named profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile create dev</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev fill</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev check</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev run -- python app.py</span></code></pre>
</div>

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### First project

Follow the same flow with more repository context and a few realistic checks.

[Open first project](first-project.md)
</div>

<div class="envctl-doc-card" markdown>
### Mental model

Learn why the quickstart steps work the way they do.

[Open mental model](mental-model.md)
</div>

<div class="envctl-doc-card" markdown>
### Daily workflow

Move from first setup into the normal day-to-day command rhythm.

[Open daily workflow](../workflows/daily.md)
</div>

</div>
