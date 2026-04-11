# Daily workflow

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guide</span>
  <p class="envctl-section-intro__body">
    This is the normal day-to-day rhythm once a repository is already set up.
    It is intentionally small: run, change one local value, inspect, validate, and debug only when needed.
  </p>
</div>

## When to use this page

Use this guide when:

- the repository is already initialized
- your local values mostly exist already
- you want the commands you repeat most often, not onboarding detail

## Run your app

```bash
envctl run -- <command>
```

For most daily work, `run` is the default choice. It injects the resolved environment directly into the subprocess, so you usually do not need to materialize a dotenv file.

## Change one local value

```bash
envctl set KEY VALUE
```

Use `set` when the contract stays the same and only your current local value changes.

## Inspect the current state

```bash
envctl inspect
```

Use `inspect` when you want to see the runtime view that `envctl` has actually resolved.

## Validate before blaming the runtime

```bash
envctl check
```

If something feels off, start here. A passing `check` tells you the contract-level state is valid before you debug the target tool.

## Switch local context explicitly

```bash
envctl --profile dev run -- app
```

Use a named profile when the same project needs a different local value set.

## Keep the Git safety net healthy

```bash
envctl hooks status
```

Use this when your team relies on envctl-managed hooks and you want to confirm the local wrappers are still healthy.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Quickstart

Go back if you need the original first-run flow.

[Open quickstart](../getting-started/quickstart.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging

Use the methodical flow when one command starts behaving differently than you expected.

[Open debugging guide](../guides/debugging.md)
</div>

<div class="envctl-doc-card" markdown>
### Commands reference

Look up exact syntax and options once the workflow already makes sense.

[Open command reference](../reference/commands/index.md)
</div>

</div>
