# Resolution

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    Resolution is the step where <code>envctl</code> determines what is actually true for the current run.
    It is the bridge between the shared contract and the currently selected local values.
  </p>
</div>

## What it is

Resolution answers one question:

> Given this contract and this local context, what is the effective environment right now?

It is the point where the model stops being abstract.

## Why it matters

A contract can look fine and local values can look fine, yet runtime behavior can still be surprising. What matters is not only what exists, but how it becomes effective.

That is what resolution defines.

<div class="envctl-callout" markdown>
The contract defines shared requirements. Resolution computes current truth inside that model.
</div>

## What problem it solves

Resolution gives `envctl` one explicit place to answer:

- which concrete values are in play now
- whether the selected local context satisfies the contract
- what should be validated or projected next

That is why `check` depends on resolution:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">validation</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span></code></pre>
</div>

Underneath, that asks whether the resolved environment satisfies the contract.

## What it is not

Resolution is not:

- the contract itself
- a random merge of files
- inherited shell state by accident
- projection into a subprocess or file

It computes what is true. It does not decide how that truth is handed off.

## How it fits in the system

The sequence is:

- the **contract** defines requirements
- local values and **profiles** provide the current context
- **resolution** computes the effective environment
- **projection** hands that result to a process, file, or tool

That separation is why validation, inspection, and runtime handoff can stay clear instead of collapsing into one fuzzy step.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Projection

See how resolved truth reaches subprocesses, files, and downstream tools.

[Read about projection](projection.md)
</div>

<div class="envctl-doc-card" markdown>
### inspect

Use inspection commands when you need to make resolution visible.

[Open inspect reference](../reference/commands/inspect.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging

Use a methodical flow when the resolved environment is not what you expected.

[Open debugging guide](../guides/debugging.md)
</div>

</div>
