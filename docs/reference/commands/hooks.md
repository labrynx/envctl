# hooks

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>hooks</code> manages the small set of Git hooks that <code>envctl</code> owns.
    Use it when you need exact behavior for hook status, install, repair, or removal.
  </p>
</div>

```bash
envctl hooks status
envctl hooks install [--force]
envctl hooks repair [--force]
envctl hooks remove
```

## Purpose

`hooks` manages the small set of Git hooks that `envctl` owns itself.

This command group exists for one product goal only: keep `envctl guard secrets` wired into the local Git flow in a visible, verifiable, and repairable way.

## Scope

`envctl` does **not** act as a generic hooks framework.

It only manages these supported hooks:

* `pre-commit`
* `pre-push`

Both wrappers run the same internal policy:

```bash
envctl guard secrets
```

## Commands

### `envctl hooks status`

Inspects the supported hooks and reports whether they are:

* `healthy`
* `missing`
* `drifted`
* `foreign`
* `not_executable`
* `unsupported`

This is the command to use when you want to verify that local Git protection is still in place.

### `envctl hooks install`

Creates missing managed hooks and rewrites drifted managed hooks back to the canonical wrapper.

By default it does **not** overwrite foreign hooks.

### `envctl hooks repair`

Converges the supported managed hooks back to a functional state.

That includes:

* creating missing managed hooks
* rewriting drifted managed hooks
* fixing executable permissions on POSIX platforms

### `envctl hooks remove`

Removes the managed hooks that `envctl` owns.

It does not remove foreign hooks.

## `--force`

`--force` is supported by:

* `envctl hooks install`
* `envctl hooks repair`

It allows `envctl` to overwrite foreign hooks for the supported hook names inside the effective managed hooks path.

It does **not** allow:

* operating on unsupported hooks paths outside the repository perimeter
* extending management to unsupported hook names
* merging multiple hook implementations automatically

## Hooks path policy

`envctl` resolves the effective hooks directory through Git itself.

It only manages hooks when that effective hooks path stays inside the current repository tree.

If the effective hooks path resolves outside the repository, `envctl` reports `unsupported` and does not modify it.

This is an intentional product boundary.

## Exit codes

`hooks` commands are strict on purpose.

### `hooks status`

* exits `0` only when the managed hooks are healthy
* exits non-zero when protection is missing, drifted, conflicted, or unsupported

### `hooks install`, `repair`, `remove`

* exit `0` only when the final operation result is complete and conflict-free
* may still apply useful changes before returning non-zero if the final state remains partial or conflicted

## JSON output

`hooks` commands support `--output json`.

The hooks JSON contract is versioned independently and currently emits:

* `schema_version: 1`
* `ok`
* `command`
* `data.hooks_path`
* `data.overall_status`
* `data.changed` for mutating operations
* `data.results[]`

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Hooks concept

Reconnect the command surface to the conceptual scope and limits.

[Read about hooks](../../concepts/hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### guard

See the policy command the managed wrappers actually execute.

[Open guard reference](guard.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks troubleshooting

Open this when hook state is missing, drifted, foreign, or unsupported.

[Open hooks troubleshooting](../../troubleshooting/hooks.md)
</div>

</div>

## Relationship to `init`

`envctl init` attempts to install managed hooks automatically as part of repository bootstrap.

If that installation cannot complete cleanly, `init` does **not** abort the whole repository setup. Instead, it warns and leaves hook management available through the `hooks` command group.

## Related commands

* use [`guard`](guard.md) for the policy the wrappers execute
* use [`init`](init.md) for first-run repository bootstrap
