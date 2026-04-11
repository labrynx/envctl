# guard

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>guard secrets</code> is the focused policy command behind envctl-managed Git protection.
    Use it when you need the exact behavior of the secret-guard safety check.
  </p>
</div>

```bash
envctl guard secrets
```

## Purpose

`guard secrets` is a safety net.

It checks the staged Git index for envctl-specific secret material before you commit something dangerous.

## What it does

Scans the staged Git index for envctl-specific secret material and exits with a non-zero status when it finds something unsafe to commit.

It currently detects:

* encrypted vault payloads
* canonical master keys
* the current project's legacy raw master key during the compatibility window

## When to use it

Use `guard secrets` when you want a pre-commit safety net against accidentally committing envctl-specific secret material.

## When not to use it

Do not treat `guard` as a general secret scanner for every possible credential in the repository. It is a focused protection layer for envctl-specific artifacts.

## Integration

This is the policy command used by the managed Git wrappers installed through:

* `envctl init`
* `envctl hooks install`
* `envctl hooks repair`

`envctl` keeps those wrappers intentionally minimal and routes the real logic back through Python with `envctl hook-run <hook>`.

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Hooks concept

Go back to the narrow role of envctl-managed hooks.

[Read about hooks](../../concepts/hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### hooks

See the command group that installs and repairs the managed wrappers.

[Open hooks reference](hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks troubleshooting

Use this when the safety layer itself looks drifted or confusing.

[Open hooks troubleshooting](../../troubleshooting/hooks.md)
</div>

</div>
