# Projection

Projection is the part of `envctl` that makes the resolved environment usable.

By the time projection happens, the important work has already been done: the contract has been read, the active profile has been selected, values have been resolved, and validation has happened.

That also means any valid contract-declared `${VAR}` placeholders have already been expanded.
Unknown or invalid placeholder references block projection earlier during resolution.

Projection is simply how that resolved state is exposed to another tool.

It does not define state. It only makes existing state usable.

## Why projection exists

Different tools expect environment data in different ways.

Some are happy to receive environment variables directly in memory. Others still expect a file like `.env.local`. Some workflows need shell export lines.

Instead of treating those outputs as the main source of truth, `envctl` treats them as explicit ways to expose already-resolved state.

That distinction matters a lot. It keeps generated outputs from quietly turning into hidden configuration.

## Modes

### run

```bash
envctl run -- app
```

```bash
envctl --group Application run -- app
```

This injects values into the subprocess environment.

* no file is created
* values are passed in memory
* expanded values are passed exactly as resolved
* values reach the immediate subprocess only
* this is usually the safest projection mode
* `--group LABEL` injects only variables declared with that exact contract group

If the target tool supports it, `run` is often the cleanest option because it avoids writing secrets to disk for that workflow.

If the immediate subprocess is `docker run` or `docker compose run`, Docker still requires explicit container forwarding such as `-e`, `--env`, or `--env-file`.

For container-oriented workflows, prefer an explicit env-file handoff instead of relying on `envctl run` to reach the container:

```bash
docker run --env-file <(envctl export --format dotenv) my-image
```

Example:

```bash
envctl run -- docker run --rm -p 7002:7002 \
  -e ARIA_EVENTD_PORT \
  -e ARIA_LOG_DIR \
  -e ARIA_RELATIONAL_STORE_MODE \
  -e ARIA_RELATIONAL_STORE_PROVIDER \
  -e ARIA_RELATIONAL_STORE_DSN \
  -e ARIA_EVENT_BUS_MODE \
  -e ARIA_EVENT_BUS_PROVIDER \
  -e ARIA_EVENT_BUS_URL \
  aria-eventd:dev
```

Forwarding only part of the contract can leave the container with an incoherent runtime configuration. If you do not want NATS in the containerized workflow, forward a coherent disabled contract instead:

```bash
envctl run -- docker run --rm \
  -e ARIA_EVENT_BUS_MODE=disabled \
  -e ARIA_EVENT_BUS_PROVIDER=none \
  aria-eventd:dev
```

### sync

```bash
envctl sync
```

```bash
envctl sync --output-path /tmp/env.env
```

```bash
envctl --group Database sync
```

This creates `.env.local`.

* the file is generated explicitly
* it is a compatibility artifact
* it is safe to delete and regenerate
* it contains the final expanded values, not the original `${...}` expressions
* `--output-path PATH` writes the same generated dotenv projection to an explicit file path
* when groups are present, dotenv projection output includes readable section headers
* `--group LABEL` writes only variables declared with that exact contract group

This mode is useful when another tool really wants a file on disk.

### export

```bash
envctl export
```

```bash
envctl export --format dotenv
```

```bash
envctl --group Application export --format dotenv
```

This prints shell export lines.

* useful for shell-based workflows
* more shell-specific than `run`
* should be treated as output, not storage
* prints the final expanded values
* `--format dotenv` prints raw dotenv `KEY=value` lines to stdout
* dotenv export does not include the sync header
* `--group LABEL` prints only variables declared with that exact contract group

## The rule that matters most

Projection output is **not** the source of truth.

It is always derived from the resolved environment.

That is true whether the output is:

* a subprocess environment
* a generated `.env.local`
* shell export lines

## Why this matters

Keeping projection separate from state helps avoid problems like:

* stale `.env.local` files
* conflicting sources of truth
* hidden behavior that is hard to debug

A projected file may be useful, but it is still just an output of the model, not the model itself.

## See also

* [Resolution](resolution.md)
