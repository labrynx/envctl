# Projection

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    Projection is the step where a resolved environment leaves the internal model and is handed to another tool.
    It is how runtime truth becomes usable outside <code>envctl</code>.
  </p>
</div>

## What it is

Projection answers one question:

> How does the resolved environment reach the thing that needs it?

That target might be a subprocess, a generated dotenv file, or another explicit handoff surface.

## Why it matters

Many environment failures are not contract failures and not local-storage failures. They are handoff failures.

Typical pattern:

- `check` passes
- `inspect` looks right
- the application still sees something else

At that point, the problem usually lives in projection.

<div class="envctl-callout" markdown>
You can have correct resolution and still have incorrect projection.
</div>

## What problem it solves

Projection keeps runtime handoff explicit instead of guessed.

Common projection paths are:

- `run` for subprocess injection
- `export` for stdout-oriented output
- `sync` for file-based handoff

One clear example is enough to show the idea:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">projection</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl run -- python app.py</span>
<span class="envctl-doc-terminal__line">$ envctl export --format dotenv</span></code></pre>
</div>

## What it is not

Projection is not:

- the contract
- local storage
- the resolved environment itself
- whatever variables happen to be in your shell already

It is a deliberate handoff from resolved truth to a target surface.

## How it fits in the system

Projection comes after resolution:

- the **contract** defines requirements
- local values and **profiles** define the current context
- **resolution** computes what is true
- **projection** hands that truth to tools

That is why validation alone does not guarantee correct runtime behavior. The target still has to receive the right handoff.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Resolution

Go one step earlier and see how runtime truth is computed.

[Read about resolution](resolution.md)
</div>

<div class="envctl-doc-card" markdown>
### Docker guide

See projection at a real boundary where mistakes are easy to make.

[Open Docker guide](../guides/docker.md)
</div>

<div class="envctl-doc-card" markdown>
### run reference

Explore the default subprocess projection path directly.

[Open run reference](../reference/commands/run.md)
</div>

</div>
