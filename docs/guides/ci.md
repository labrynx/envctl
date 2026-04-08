# CI

## Problem

In CI, the easiest failure mode is letting automation quietly mutate or patch environment state instead of telling you what is wrong.

That makes pipelines harder to trust.

## Goal

Use `envctl` in CI as a clear validation and projection layer, not as hidden repair logic.

## Steps

For the default CI path, validate explicitly:

```bash
envctl check
```

If the pipeline uses a dedicated profile, select it intentionally:

```bash
ENVCTL_PROFILE=ci envctl check
```

If a later CI step needs the resolved environment itself, choose the narrowest handoff that fits:

```bash
envctl run -- make integration-test
```

or:

```bash
envctl export --format dotenv > /tmp/app.env
```

## Result

Your pipeline either:

* passes because the selected environment satisfies the contract
* or fails with explicit diagnostics about what is missing or invalid

That keeps CI readable and predictable.

## Why this works

CI is usually the wrong place to invent values, fill prompts, or repair local state invisibly.

`envctl` works best there as an explicit validation gate, with projection only when a downstream step really needs it.

* [check](../reference/commands/check.md)
* [run](../reference/commands/run.md)
* [Projection](../concepts/projection.md)
* [Resolution](../concepts/resolution.md)
