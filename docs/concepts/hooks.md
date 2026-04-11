# Hooks

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Concept</span>
  <p class="envctl-section-intro__body">
    <code>envctl</code> can manage a very small Git-hook safety layer.
    The point is not generic automation. The point is narrow local protection against committing or pushing envctl-managed secret material by mistake.
  </p>
</div>

## What hooks are

In the `envctl` model, managed hooks are local wrappers around:

```text
envctl guard secrets
```

They exist to stop obvious secret-handling mistakes before commit and push.

## Why they matter

Hooks add a lightweight local safety net:

- before a commit is created
- before a push leaves the machine

That makes them useful, especially for teams, but they remain a narrow protection layer.

## What problem they solve

Managed hooks solve one focused problem:

> prevent accidental local Git operations from carrying envctl-managed secret material forward unnoticed

They do not try to solve broader CI policy, arbitrary automation, or multi-tool hook orchestration.

## What hooks are not

Managed hooks are not:

- a general-purpose automation framework
- a hook-merging system
- a replacement for CI enforcement
- a guarantee against `--no-verify`

That narrow scope is intentional. It avoids hidden behavior and fragile integrations.

## Managed vs foreign hooks

`envctl` distinguishes:

- **managed hooks**: created by `envctl`, marked as `managed-by: envctl`, and fully controlled by it
- **foreign hooks**: created by something else or manually modified

If a hook is not managed by `envctl`, it is left alone by default.

## How hooks fit in the system

Managed hooks sit beside the core model, not inside it:

- the **contract** defines requirements
- the **vault** stores local values
- **resolution** and **projection** govern runtime truth
- **hooks** add a local Git safety layer around that model

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Using hooks

See the operational workflow for install, status, repair, and removal.

[Open hooks guide](../guides/hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### hooks reference

See the exact command surface for the hook management commands.

[Open hooks reference](../reference/commands/hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### Security reference

Connect hook protection back to the broader security model and its limits.

[Open security reference](../reference/security.md)
</div>

</div>
