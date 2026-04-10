# Debugging

## Problem

Something is failing, but it is not obvious whether the issue is:

* missing values
* the wrong active profile
* bad expansion
* invalid contract data
* or a projection problem

## Goal

Move from broad diagnosis to one concrete cause without guessing.

## Steps

Start with the smallest overview:

```bash
envctl status
```

Then validate the environment directly:

```bash
envctl check
```

If you need the full runtime picture, inspect it:

```bash
envctl inspect
```

If the problem narrows down to one key, inspect just that key:

```bash
envctl inspect DATABASE_URL
```

If you need to compare resolved state with physical stored values, drop down one level:

```bash
envctl vault show
```

If you need execution-level observability events, use `--trace`:

```bash
envctl check --trace
envctl check --trace --trace-format human
envctl check --trace --trace-format jsonl --trace-output file
```

Use `--trace` when you need execution phases, timings, and an `execution_id` you can share in issues.

Recommended modes:

* `--trace --trace-format human`: compact high-signal flow for terminal debugging
* `--trace --trace-format jsonl`: structured contract for tooling, issue attachments, or diffing
* `--trace --trace-output file`: persist one trace artifact under `.envctl/observability/`

## Result

You move from:

* broad readiness
* to contract-level validation
* to full resolved state
* to one-key inspection
* to stored vault data only if needed

That gives you a repeatable debugging path instead of jumping randomly between commands.

## What to attach to an issue

When reporting a reproducible problem, prefer attaching:

* the exact command you ran
* whether you selected a non-default profile
* the relevant `envctl check` or `envctl inspect` output
* the `execution_id` from trace output
* a sanitized JSONL trace excerpt (`--trace --trace-format jsonl`)
* a short summary of the slowest phases (name + duration)
* your platform, shell, Python version, and `envctl` version

Do not include:

* real secret values
* vault files
* master keys
* generated env artifacts containing sensitive data

## Why this works

Each command answers a different question:

* `status` gives readiness
* `check` gives pass/fail validation
* `inspect` gives full resolved context
* `inspect KEY` gives one-key explanation
* `vault show` gives physical stored values

The guide works because it follows the structure of the model instead of skipping straight to low-level inspection.

* [Resolution](../concepts/resolution.md)
* [check](../reference/commands/check.md)
* [inspect](../reference/commands/inspect.md)
* [vault](../reference/commands/vault.md)
