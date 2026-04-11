# Docker

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guide</span>
  <p class="envctl-section-intro__body">
    Use <code>envctl</code> with Docker when you want the container runtime to receive
    an explicit, validated environment instead of relying on unclear shell state or stale local files.
  </p>
</div>

## When to use this guide

Use this page when:

- Docker or Compose should receive the resolved environment explicitly
- local runtime and container runtime tend to drift
- you need to decide between `run`, `export`, and file-based handoff

## Starting point

The goal is simple:

- validate first
- choose one explicit projection path
- give Docker only what it should actually receive

<div class="envctl-callout" markdown>
A good Docker workflow with <code>envctl</code> makes the runtime handoff more visible, not less.
</div>

## The default path: `run`

Use `run` when the Docker command can inherit environment variables from the parent process:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">docker via run</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span>
<span class="envctl-doc-terminal__line">$ envctl run -- docker compose up</span></code></pre>
</div>

Choose this when you want the narrowest handoff and do not want to write a dotenv file first.

## Use `export` when Docker expects a file

Some workflows need an explicit env file:

```bash
envctl check
envctl export --format dotenv > .env.runtime
docker compose --env-file .env.runtime up
```

Use this when Docker tooling already expects file-based input.

## Profiles fit naturally here

Profiles are often the cleanest way to keep Docker-specific local context separate:

```bash
envctl --profile docker check
envctl --profile docker run -- docker compose up
```

Same shared contract, different local value set.

## Common mistakes to avoid

- treating exported dotenv files as the source of truth
- skipping `check` because “Docker will fail anyway”
- mixing shell exports, Docker env files, and `envctl` without a clear order

## A useful rule

In practice:

- prefer **`run`** when subprocess inheritance is enough
- prefer **`export`** when Docker truly needs a file
- keep the handoff narrow and explicit

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Projection

Understand what `run`, `export`, and file handoff actually mean.

[Read about projection](../concepts/projection.md)
</div>

<div class="envctl-doc-card" markdown>
### run reference

Inspect the default subprocess projection path directly.

[Open run reference](../reference/commands/run.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging

Use a more explicit flow when the container still sees the wrong value.

[Open debugging guide](debugging.md)
</div>

</div>
