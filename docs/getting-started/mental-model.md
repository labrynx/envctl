# Mental model

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Getting started</span>
  <p class="envctl-section-intro__body">
    This page is the onboarding version of the model.
    It gives you the minimum structure you need before memorizing commands, while the canonical definitions live in the <a href="../concepts/">Concepts</a> section.
  </p>
</div>

## Why this page matters

A lot of tooling feels harder than it really is because people learn commands before they learn the shape of the problem.

With `envctl`, the shape matters.

If you only memorize commands, sooner or later you end up asking questions like:

- why does `check` pass here but not there
- why do I need profiles
- why is the contract separate from local values
- why does `run` behave differently from `export`

Those questions all get easier once the model is clear.

## The five-part model

The simplest useful mental model is this:

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Contract

What the project requires.
</div>

<div class="envctl-doc-card" markdown>
### Vault

What this machine stores locally.
</div>

<div class="envctl-doc-card" markdown>
### Profiles

Which local value set is active.
</div>

<div class="envctl-doc-card" markdown>
### Resolution

What is actually true right now.
</div>

<div class="envctl-doc-card" markdown>
### Projection

How that truth reaches your tools.
</div>

</div>

If that five-step chain is clear, the CLI starts to make a lot more sense.

## 1. Contract — shared requirements

The contract is the repository-level definition of the environment model.

It says things like:

- which variables exist
- which ones are required
- how the environment is structured
- what the project expects before runtime

The contract is shared.

It belongs in version control because it changes the project itself.

## 2. Vault — local real values

The vault is where actual machine-specific values live.

That includes things like:

- credentials
- local URLs
- developer-specific concrete values

The vault is local.

It is deliberately separate from the contract so the repository does not become a place to store or move real secrets.

## 3. Profiles — local context selection

A machine may need more than one local context.

For example:

- one setup for normal development
- one for Docker
- one for reproducing CI-like behavior

Profiles let the same machine satisfy the same contract in different local ways.

So profiles do not change the project.
They change the active local value set.

## 4. Resolution — current truth

Resolution is the moment where `envctl` computes what is actually true for this run.

That means:

- contract + local values + selected profile
- become one effective environment state

This is the step where the model stops being abstract.

## 5. Projection — runtime handoff

Projection is how the resolved environment reaches another tool.

For example:

- a subprocess through `run`
- a rendered file through `export`
- another explicit handoff path

This matters because even when validation is correct, a runtime can still behave differently if the projection path is wrong.

## One sentence version

If you want the shortest possible mental model:

> The repo defines requirements, the machine stores real values, the selected profile chooses context, resolution computes what is true, and projection hands it to the runtime.

That is `envctl` in one sentence.

## Why this is better than “just use a dotenv file”

Because a single dotenv file usually collapses too many roles into one artifact.

It becomes all of this at once:

- pseudo-documentation
- local runtime state
- accidental source of truth
- onboarding mechanism
- team handoff file
- stale snapshot of who knows when

That is exactly the kind of ambiguity `envctl` is trying to avoid.

## The most important separation

If you remember only one thing from this page, let it be this:

### Shared requirement

belongs in the contract

### Real local value

belongs in local storage

That separation is the backbone of the tool.

Everything else becomes easier once that part is internalized.

## What `check` really means

When you run:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">mental model check</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span></code></pre>
</div>

you are really asking:

> Does the currently resolved local environment satisfy the shared contract?

That is a much more useful way to think about it than “did my env file load”.

## What `fill` really means

When you run:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">mental model fill</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl fill</span></code></pre>
</div>

you are not editing shared requirements.

You are supplying missing local values so the current machine can satisfy them.

That difference is fundamental.

## What `run` really means

When you run:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">mental model run</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl run -- python app.py</span></code></pre>
</div>

you are projecting resolved truth into a subprocess.

So `run` is not “another check”.
It is the runtime handoff step.

## Where confusion usually comes from

Most confusion comes from collapsing two or more layers together.

For example:

- treating the contract like local storage
- treating local storage like team truth
- treating validation like projection
- treating projection like if it were the same thing as resolution

When that happens, the system starts to feel more magical than it really is.

## A healthy way to learn envctl

This order tends to work well:

1. understand the five-part model
2. initialize your local setup
3. fill only what is missing
4. validate with `check`
5. run through an explicit projection path

That gives you a much clearer start than memorizing every command at once.

<div class="envctl-callout" markdown>
When you want the precise definition of one layer, switch from this onboarding page to the corresponding page in [Concepts](../concepts/index.md).
</div>

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Quickstart

Now that the model is clear, walk the shortest practical path.

[Open quickstart](quickstart.md)
</div>

<div class="envctl-doc-card" markdown>
### Contract

Go deeper into the shared requirement layer.

[Read about the contract](../concepts/contract.md)
</div>

<div class="envctl-doc-card" markdown>
### Resolution

See how the current environment becomes true for a run.

[Read about resolution](../concepts/resolution.md)
</div>

</div>
