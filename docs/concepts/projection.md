# Projection

Projection is the part of `envctl` that makes the resolved environment usable.

By the time projection happens, the important work has already been done: the contract has been read, the active profile has been selected, values have been resolved, and validation has happened.

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

This injects values into the subprocess environment.

* no file is created
* values are passed in memory
* this is usually the safest projection mode

If the target tool supports it, `run` is often the cleanest option because it avoids writing secrets to disk for that workflow.

### sync

```bash
envctl sync
```

This creates `.env.local`.

* the file is generated explicitly
* it is a compatibility artifact
* it is safe to delete and regenerate

This mode is useful when another tool really wants a file on disk.

### export

```bash
envctl export
```

This prints shell export lines.

* useful for shell-based workflows
* more shell-specific than `run`
* should be treated as output, not storage

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
