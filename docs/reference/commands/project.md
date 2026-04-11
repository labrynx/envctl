# project

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    <code>project</code> manages repository identity and local binding continuity.
    Use it when a checkout needs explicit binding, rebind, unbind, or recovery operations.
  </p>
</div>

```bash
envctl project bind ID
envctl project unbind
envctl project rebind
envctl project repair
```

## Purpose

Project commands preserve repository identity and local continuity.

They exist to keep the binding between a repository and its local vault state understandable and recoverable.

## What these commands do

These commands manage repository identity and local binding continuity.

## Available subcommands

* `envctl project bind ID`
* `envctl project unbind`
* `envctl project rebind`
* `envctl project repair`

## When to use it

Use `project` commands when local binding is broken, ambiguous, moved, or needs recovery.

## When not to use it

Do not reach for `project` commands for normal day-to-day value changes. They are identity and recovery tools, not routine environment mutation commands.

## Notes

These commands matter most when local binding is broken, moved, or needs recovery.

## Related commands

* see [`status`](status.md) and [`inspect`](inspect.md) when you are diagnosing whether the local project context itself is healthy

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Binding

Reconnect project commands to the conceptual identity layer.

[Read about binding](../../concepts/binding.md)
</div>

<div class="envctl-doc-card" markdown>
### Metadata and local state

See the local support state that helps recovery remain coherent.

[Read about metadata](../../concepts/metadata.md)
</div>

<div class="envctl-doc-card" markdown>
### Recovery

Open this when the problem already feels like state recovery, not normal usage.

[Open recovery guide](../../troubleshooting/recovery.md)
</div>

</div>
