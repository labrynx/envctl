# Team workflows

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guide</span>
  <p class="envctl-section-intro__body">
    Teams need one shared description of the project environment,
    but they should not share real local values through Git.
    <code>envctl</code> works well when the team shares intent and keeps machine truth local.
  </p>
</div>

## The problem this guide solves

In most teams, environment setup goes wrong in one of two ways:

- secrets drift into version control
- the repository stops describing what the application actually needs

Then onboarding turns into tribal knowledge:

- “copy my file”
- “ignore that variable”
- “CI uses something different”
- “I think this one is optional”

That is exactly the kind of ambiguity `envctl` is built to reduce.

## The team rule that matters most

<div class="envctl-callout" markdown>
The repository should describe **requirements**.  
Each machine should keep **real values** local.
</div>

That one split gives you:

- a contract the whole team can reason about
- local values that never need to be committed
- clearer onboarding
- less guesswork after pull

## A normal team change

When the project itself needs a new variable, add it to the contract.

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">shared change</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl add API_KEY</span>
<span class="envctl-doc-terminal__line">$ git add .envctl.yaml</span>
<span class="envctl-doc-terminal__line">$ git commit -m "require API_KEY"</span></code></pre>
</div>

That change belongs in Git because it changes the project’s requirements.

What should **not** be committed is one developer’s actual `API_KEY`.

## What the next developer does

After another developer pulls the contract change, the next step is not “copy someone else’s file”.

It is:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">after pull</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span>
<span class="envctl-doc-terminal__line">$ envctl fill</span>
<span class="envctl-doc-terminal__line">$ envctl run -- python app.py</span></code></pre>
</div>

That is the shape you want:

- **pull shared requirements**
- **check**
- **fill only what is missing locally**
- **run**

## What gets shared and what stays local

### Shared through Git

The team shares:

- the contract
- variable names
- required vs optional expectations
- defaults that are safe to publish
- descriptions and validation rules

### Kept local

Each machine keeps:

- real credentials
- machine-specific URLs
- personal development overrides
- profile-local variants

That is the whole idea.

## When to use `add` vs `set`

This distinction matters a lot in team workflows.

### Use `add` when the project changes

Use `add` when the application now depends on a new variable as part of the shared contract.

That is a repository-level change.

### Use `set` when only your machine changes

Use `set` when the contract stays the same, but your local machine needs a different value.

That is a local profile-level change.

A quick rule:

- **project changed** → `add`
- **my machine changed** → `set`

## A realistic onboarding flow

For a new teammate, the path should feel like this:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">onboarding</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl config init</span>
<span class="envctl-doc-terminal__line">$ envctl init</span>
<span class="envctl-doc-terminal__line">$ envctl check</span>
<span class="envctl-doc-terminal__line">$ envctl fill</span>
<span class="envctl-doc-terminal__line">$ envctl run -- python app.py</span></code></pre>
</div>

Notice what is missing there:

- no secret files from another person
- no guessing which variables matter
- no “try this dotenv and see”

That is the payoff.

## Team workflows with profiles

Sometimes one developer needs more than one local context for the same project.

For example:

- normal local development
- a second local integration setup
- a dedicated profile for another backend or account

That still does not require changing the contract.

It just means using profiles explicitly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">profiles</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl profile create dev-alt</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev-alt fill</span>
<span class="envctl-doc-terminal__line">$ envctl --profile dev-alt check</span></code></pre>
</div>

## Hooks help teams, but they are not the whole story

Managed Git hooks are useful because they stop obvious mistakes before commit and push.

But hooks are local protection, not the entire team process.

A healthy team setup usually has all three:

- contract in Git
- local values outside Git
- CI validation after push

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Contract

Understand the shared definition the team collaborates on.

[Read about the contract](../concepts/contract.md)
</div>

<div class="envctl-doc-card" markdown>
### Profiles

See how multiple local setups fit into one team-owned contract.

[Open profiles guide](profiles.md)
</div>

<div class="envctl-doc-card" markdown>
### Vault

Reconnect team workflows to the local storage layer where real values live.

[Read about the vault](../concepts/vault.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks

Add local secret-guard protection to the workflow.

[Open hooks guide](hooks.md)
</div>

</div>
