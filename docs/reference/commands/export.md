# export

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>export</code> is stdout-oriented projection.
    Use it when another shell command or tool wants the resolved environment rendered directly to standard output.
  </p>
</div>

```bash
envctl export
envctl export --format shell
envctl export --format dotenv
envctl --output json export
```

## Purpose

`export` is stdout-oriented projection.

It prints the resolved environment to standard output instead of creating a file or launching a subprocess.

## What it does

* resolves the active environment first
* prints shell export lines by default
* prints dotenv `KEY=value` lines with `--format dotenv`
* emits structured JSON with the global `--output json` flag
* prints the final expanded values, not the original placeholder expressions
* respects global selectors such as `--group`, `--set`, and `--var`
* fails fast if the selected explicit profile does not exist

## When to use it

Use `export` when another shell command or script wants the resolved result directly from stdout.

If the caller is another tool and you want a stable structured payload, use `envctl --output json export`.

## When not to use it

Do not use `export` as storage. It is projection output, not a source of truth.

If another tool needs a file on disk, use [`sync`](sync.md). If you want to execute a command directly with the resolved environment, use [`run`](run.md).

## Typical examples

```bash
envctl export
envctl export --format dotenv
envctl --group Runtime export --format dotenv
envctl --output json export
```

## Related commands

* use [`run`](run.md) for in-memory subprocess injection
* use [`sync`](sync.md) for generated dotenv files
* use [`check`](check.md) when you only need pass-or-fail validation

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Projection

Reconnect `export` to the projection layer it implements.

[Read about projection](../../concepts/projection.md)
</div>

<div class="envctl-doc-card" markdown>
### run

Use this when the target tool can consume environment variables directly.

[Open run reference](run.md)
</div>

<div class="envctl-doc-card" markdown>
### sync

Use this when the target tool needs a file on disk.

[Open sync reference](sync.md)
</div>

</div>
