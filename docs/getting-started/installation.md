# Installation

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Getting started</span>
  <p class="envctl-section-intro__body">
    Install <code>envctl</code>, verify that it works, and then move straight into the quickstart.
    Keep this page practical — install first, theory later.
  </p>
</div>

## Option 1: install from PyPI

This is the shortest path when you want to use `envctl` as a normal CLI tool.

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">install</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line"><span class="envctl-doc-terminal__prompt">$ </span>python3 -m pip install envctl</span></code></pre>
</div>

Use this when you are onboarding into a project and do not need to work on `envctl` itself.

## Option 2: install from the repo for local development

Use this when you are contributing to `envctl` or testing changes locally.

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">editable install</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line"><span class="envctl-doc-terminal__prompt">$ </span>python3 -m venv .venv</span>
<span class="envctl-doc-terminal__line"><span class="envctl-doc-terminal__prompt">$ </span>source .venv/bin/activate</span>
<span class="envctl-doc-terminal__line"><span class="envctl-doc-terminal__prompt">$ </span>pip install -e .[dev]</span></code></pre>
</div>

That gives you an editable environment suitable for local development.

## Verify that it works

Once installed, confirm that the CLI is available:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">verify</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line"><span class="envctl-doc-terminal__prompt">$ </span>envctl --version</span></code></pre>
</div>

If you see a version printed successfully, the CLI is installed and ready.

## What to do next

Once `envctl` is available in your shell, continue with the [Quickstart](quickstart.md).

If you prefer to understand the model before running commands, read the [Mental model](mental-model.md).

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Quickstart

Move from installation into the shortest safe setup flow.

[Open quickstart](quickstart.md)
</div>

<div class="envctl-doc-card" markdown>
### First project

Follow a fuller onboarding path inside a real repository checkout.

[Open first project](first-project.md)
</div>

<div class="envctl-doc-card" markdown>
### Mental model

Read this first if you want the concepts before the workflow.

[Open mental model](mental-model.md)
</div>

</div>
