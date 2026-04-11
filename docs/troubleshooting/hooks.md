# Hooks troubleshooting

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Troubleshooting</span>
  <p class="envctl-section-intro__body">
    When hook behavior looks wrong, the key is to distinguish between managed wrappers,
    foreign ownership, unsupported hook paths, and simple local drift.
    Most hook issues are understandable once you inspect them as a state problem.
  </p>
</div>

## What this page helps with

Use this page when:

- pre-commit no longer blocks staged secret material
- pre-push behavior changed unexpectedly
- `envctl hooks status` reports something unclear
- a hook file exists but does not behave like `envctl` used to
- the repository seems to have multiple hook expectations at once

## Start with status

Always start here:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">hooks status</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl hooks status</span></code></pre>
</div>

Do not jump straight to reinstalling. First establish what `envctl` thinks the current hook state is.

## How to read the common states

### `healthy`

This means the managed wrapper is present and matches what `envctl` expects.

Usually, if behavior still feels wrong in this state, the issue is elsewhere:

- what you staged is not what you think you staged
- the hook did run, but the result was misunderstood
- another workflow layer is confusing the diagnosis

### `missing`

This means the managed wrapper is not there.

Typical fix:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">install missing</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl hooks install</span></code></pre>
</div>

### `drifted`

This means the hook looks like it used to be managed, but no longer matches the canonical wrapper.

Typical fix:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">repair drifted</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl hooks repair</span></code></pre>
</div>

### `foreign`

This means some other implementation owns that supported hook name.

That is not automatically an error. It just means `envctl` is not currently the hook owner there.

Typical options:

- leave it alone if another hook system is intentionally in charge
- use `--force` only if you intentionally want envctl to replace that ownership

### `not_executable`

This means the hook exists but is not executable in the expected POSIX sense.

Typical fix:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">repair executable</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl hooks repair</span></code></pre>
</div>

### `unsupported`

This means the effective hooks path resolved by Git is outside the repository perimeter or otherwise not supported for envctl management.

That is a boundary decision, not a bug. `envctl` refuses to mutate hook locations it does not consider safely managed.

## The most common hook problems

## 1. `envctl init` ran, but hooks are still not active

This usually means one of these:

- init completed, but managed hook installation did not converge
- another hook owner was already present
- the effective hooks path is unsupported

Check status first:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">post-init check</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl hooks status</span></code></pre>
</div>

Then decide whether you need `install`, `repair`, or no action at all.

## 2. Hooks used to work, then stopped

This often points to drift or ownership change.

Typical path:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">restore hooks</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl hooks status</span>
<span class="envctl-doc-terminal__line">$ envctl hooks repair</span>
<span class="envctl-doc-terminal__line">$ envctl hooks status</span></code></pre>
</div>

## 3. Another tool is managing hooks

This is where people often overreact.

If another tool intentionally owns `pre-commit` or `pre-push`, then `foreign` is simply describing reality.

The real question is:

> Which tool should own those supported hook names in this repository?

If the answer is “not envctl”, then no repair is needed.

If the answer is “envctl should own them again”, then a forced install or repair may be appropriate.

## 4. `guard secrets` behaves differently than expected

At that point, the issue may not be hook installation anymore.

It may be:

- the staged content is not what you think it is
- the files changed names or paths
- the hook runs, but the output is being misread
- the real issue is in `guard secrets`, not in the wrapper

Test the underlying command directly:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">guard direct</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl guard secrets</span></code></pre>
</div>

That helps separate hook-wrapper problems from guard-command problems.

## Repair vs install

A simple rule:

- use **`install`** when wrappers are missing and you want to place them
- use **`repair`** when wrappers exist but look wrong, drifted, or partially broken

When in doubt, `status` should tell you which one fits better.

## When to use `--force`

Use `--force` only when you explicitly want envctl to replace foreign ownership for supported hook names.

That is not the normal path.

It is an intentional takeover.

<div class="envctl-callout" markdown>
If you are not sure whether you want to replace a foreign hook, you probably do not want `--force` yet.
</div>

## A healthy hook workflow

A healthy repository usually looks like this:

- `envctl init` attempts bootstrap
- `envctl hooks status` is readable and boring
- managed wrappers stay canonical
- `guard secrets` can also be run directly
- CI still exists as a second line of defense

That is enough. Hook systems become fragile when they try to do too much.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Hooks guide

Go back to the normal operational model for managed wrappers.

[Open hooks guide](../guides/hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### Guard reference

Inspect the command that the wrappers are protecting around.

[Open guard reference](../reference/commands/guard.md)
</div>

<div class="envctl-doc-card" markdown>
### Recovery

Use the broader recovery page if hooks are only one part of a bigger local setup issue.

[Open recovery guide](recovery.md)
</div>

</div>
