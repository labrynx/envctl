# Troubleshooting

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Troubleshooting</span>
  <p class="envctl-section-intro__body">
    Most <code>envctl</code> problems become easier once you locate them in the right layer:
    contract, local values, profiles, resolution, projection, or hooks.
    This section helps you debug in that order instead of guessing blindly.
  </p>
</div>

## Start here

When something breaks, do not start with random edits.

Start by reducing the question.

A useful first split is:

- **the environment is invalid**
- **the environment is valid, but the target runtime still behaves differently**
- **the local Git protection or hook flow is not behaving as expected**

That immediately narrows the search.

## The fastest first check

If you want the quickest signal, begin with:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">first check</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span></code></pre>
</div>

That tells you whether the selected environment satisfies the contract.

If it fails, stay at that layer first. Do not jump to runtime debugging too early.

## A practical troubleshooting order

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### 1. Validate

Run `check` first.

If the environment is not valid, nothing else downstream is stable.

</div>

<div class="envctl-doc-card" markdown>
### 2. Confirm the profile

Make sure you are debugging the profile you actually intended to use.

</div>

<div class="envctl-doc-card" markdown>
### 3. Inspect the key or scope

Do not inspect the whole world if only one variable matters.

</div>

<div class="envctl-doc-card" markdown>
### 4. Verify projection

If validation passes, compare the actual handoff path: `run`, `export`, `sync`, or another consumer.

</div>

</div>

## Common classes of problems

### Missing values

Typical signs:

- `check` reports missing required variables
- onboarding stalls after pull
- CI fails with contract violations

Usually this means:

- the contract changed
- the local profile has not been filled yet
- the wrong profile is selected

### Unexpected values

Typical signs:

- `check` passes
- the application still uses the wrong backend, port, account, or URL

Usually this means:

- the wrong profile is active
- the local value differs from what you assumed
- the downstream tool is consuming a different projection path than expected

### Hook problems

Typical signs:

- pre-commit or pre-push behavior changed suddenly
- the repository says hooks are installed, but protection does not behave as expected
- Git hooks look drifted or foreign

Usually this means:

- managed wrappers were modified
- another hook owner took over
- the effective hooks path is not where you think it is

### Projection problems

Typical signs:

- `check` succeeds
- the exported file or runtime process still does not match expectations

Usually this means:

- validation is fine
- projection into the target tool is the real issue

## Which page to open next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Common errors

Start here if you want quick pattern-based diagnosis.

[Open common errors](common-errors.md)
</div>

<div class="envctl-doc-card" markdown>
### Recovery

Use this when you already know something is broken and want a controlled path back.

[Open recovery guide](recovery.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks troubleshooting

Use this when the issue is around pre-commit, pre-push, or managed wrappers.

[Open hooks troubleshooting](hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging guide

Use this when you want a more methodical inspection flow.

[Open debugging guide](../guides/debugging.md)
</div>

</div>

## Keep the model in mind

A lot of troubleshooting becomes easier once you remember the core split:

- the repo describes requirements
- local storage holds real values
- profile selection chooses the local context
- resolution decides what is true
- projection decides what reaches the target tool

If you keep those layers separate, most failures stop looking mysterious.

## Read next

If you are not sure where to go, I would open these in order:

1. [Common errors](common-errors.md)
2. [Debugging guide](../guides/debugging.md)
3. [Hooks troubleshooting](hooks.md)
