# Profiles

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guide</span>
  <p class="envctl-section-intro__body">
    Profiles let one machine keep more than one local value set for the same contract.
    They are the clean way to switch local context without mutating shared project requirements.
  </p>
</div>

If you want the definition of profiles rather than the workflow, start with the [Profiles concept](../concepts/profiles.md).

## Why profiles exist

One repository often needs more than one local setup.

Typical examples:

- local development with one account
- local development with another account
- a second integration target
- temporary side-by-side testing
- different local ports or machine-owned endpoints

Without profiles, people often drift toward brittle habits:

- copying dotenv files around
- renaming files manually
- overwriting values in place
- forgetting what changed

Profiles exist to stop that mess from becoming normal.

## What a profile changes

A profile changes **local stored values**.

It does **not** change:

- the contract
- required variables
- shared defaults
- descriptions
- validation rules

That distinction is the whole point.

<div class="envctl-callout" markdown>
Use profiles when the **project stays the same** but your **local execution context changes**.
</div>

## Create a profile

When you want a second local context, create it explicitly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">create profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile create dev</span></code></pre>
</div>

If you like, think of this as creating a new local namespace of values.

## Fill missing values for that profile

Once the profile exists, populate only what is missing there:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">fill profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl --profile dev fill</span></code></pre>
</div>

This keeps the values scoped to that profile instead of overwriting your default local setup.

## Validate it

Before you trust it, validate it:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">check profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl --profile dev check</span></code></pre>
</div>

This tells you whether that selected local value set satisfies the same shared contract.

## Run with it

Once validated, use it directly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">run profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl --profile dev run -- python app.py</span></code></pre>
</div>

Same contract, different local context.

That is exactly what profiles are for.

## See what profiles exist

Use this when you want a quick overview of local profile names:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">list profiles</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile list</span></code></pre>
</div>

## Copy an existing profile

Sometimes the second profile is almost the same as the first one.

In that case, copy it and then change only what is different:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">copy profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile copy local staging-like</span></code></pre>
</div>

That is often cleaner than rebuilding a second profile from scratch.

## Remove a profile you no longer need

If a local context is obsolete, remove it explicitly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">remove profile</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile remove dev</span></code></pre>
</div>

This keeps local profile sprawl under control.

## See where a profile lives

If you want to inspect profile-local storage path information directly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">profile path</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile path</span>
<span class="envctl-doc-terminal__line">$ envctl profile path dev</span></code></pre>
</div>

That is useful when debugging local storage layout.

## A practical pattern

A very normal setup on one machine might be:

- `local` → normal daily development
- `dev-alt` → second local backend or second account
- `ci-like` → a local profile used to mimic CI constraints

The important part is that all three still point to the same contract.

## When not to use profiles

Do **not** use profiles as if they were alternate contracts.

If the application requirements changed for everyone, that is not a profile problem. That is a contract change.

A quick rule:

- **shared project requirements changed** → update the contract
- **my local context changed** → use profiles

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Profiles concept

Go deeper into the conceptual role of profiles.

[Read about profiles](../concepts/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles reference

See the exact selection and storage rules.

[Open profiles reference](../reference/profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Resolution

Understand how profile values participate in final runtime resolution.

[Read about resolution](../concepts/resolution.md)
</div>

</div>
