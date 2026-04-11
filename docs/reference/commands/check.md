# check

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>check</code> is the fast validation gate.
    Use it when you want a short answer about whether the selected environment currently satisfies the contract.
  </p>
</div>

```bash
envctl check
```

## Purpose

`check` is the fast diagnostic gate.

Use it when you want a short yes-or-no answer about whether the currently selected environment is valid.

## What it does

* validates the resolved environment for the active scope
* keeps output short and focused on actual problems
* reports missing required values, invalid values, expansion reference errors, and unknown keys
* prints one likely next action for each problem
* validates semantic string formats declared in the contract through `format`
* exits non-zero on failure
* fails fast if the selected explicit profile does not exist

## Scope and selectors

Global selectors change what `check` validates:

* `--group LABEL` validates only variables whose normalized `groups` include `LABEL`
* `--set NAME` validates one named contract set
* `--var KEY` validates one explicit variable

These selectors are mutually exclusive. When none is provided, `check` validates the full contract.

## What `check` does not do

`check` does not:

* modify local values
* generate missing values
* write `.env.local`
* try to project an invalid environment anyway

If you need to fix missing values interactively, use [`fill`](fill.md). If you need the full runtime picture, use [`inspect`](inspect.md).

## When to use it

Use `check`:

* before `run`, `sync`, or `export`
* before CI or preflight automation
* after pulling contract changes
* when you want the quickest reliable answer about readiness

## When not to use it

Do not use `check` when the real question is “why is one key behaving this way?” In that case, use `envctl inspect KEY`.

Do not use `check` when you need a generated dotenv file or subprocess environment. It validates; it does not project.


## Observability options

`check` supports optional observability flags to make validation flow easier to inspect while troubleshooting.

* `--trace` enables trace output for validation stages
* `--trace-format human|jsonl` selects trace output format (`human` by default)
* `--trace-output stderr|file|both` controls destination (`stderr` by default)
* `--trace-file PATH` writes traces to a file when output includes `file`
* `--profile-observability` includes profile-selection and profile-loading trace details
* `--debug-errors` includes extra error context intended for diagnosis

These options do **not** change validation rules, selected scope, or exit behavior. They only increase visibility into what `check` is already doing.

## Observability examples

```bash
envctl check --trace
envctl check --trace --trace-format jsonl
```

## Typical examples

```bash
envctl check
envctl --profile dev check
envctl --group Runtime check
envctl --set docker_runtime check
envctl --var DATABASE_URL check
```

## Related commands

* use [`inspect`](inspect.md) when the short answer is not enough
* use [`run`](run.md), [`sync`](sync.md), or [`export`](export.md) only after the environment validates cleanly
* use [`fill`](fill.md) when required values are missing

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Resolution

Reconnect validation to the step that computes what is true.

[Read about resolution](../../concepts/resolution.md)
</div>

<div class="envctl-doc-card" markdown>
### inspect

Use this when pass/fail is not enough.

[Open inspect reference](inspect.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging

Use a methodical flow when validation is only the first clue.

[Open debugging guide](../../guides/debugging.md)
</div>

</div>
