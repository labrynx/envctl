# Using hooks

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guide</span>
  <p class="envctl-section-intro__body">
    Use Git hooks when you want immediate local feedback before commit and push.
    In <code>envctl</code>, hooks exist for one focused reason: keep <code>envctl guard secrets</code> wired into the local Git flow in a visible, repairable way.
  </p>
</div>

## When to use this guide

Use this page when:

- you want envctl-managed hook protection in a repository
- hook status looks unclear or drifted
- you need to install, repair, force, or remove managed wrappers

If you want the concept, read [Hooks](../concepts/hooks.md) first.

## Starting point

In most repositories, the normal path is:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">bootstrap hooks</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl init</span>
<span class="envctl-doc-terminal__line">$ envctl hooks status</span></code></pre>
</div>

`init` attempts to install managed hooks during repository bootstrap. If that does not complete cleanly, inspect or repair hooks explicitly afterwards.

## Step 1: check current hook state

```bash
envctl hooks status
```

Typical states:

- `healthy`
- `missing`
- `drifted`
- `foreign`
- `not_executable`
- `unsupported`

Practical reading:

- **healthy** → protection is in place
- **missing** → install it
- **drifted** / **not_executable** → repair it
- **foreign** → something else owns that hook name
- **unsupported** → envctl refuses to manage that hooks path

## Step 2: install or repair

If wrappers are missing:

```bash
envctl hooks install
```

If wrappers exist but look wrong:

```bash
envctl hooks repair
```

Both commands stay conservative by default and leave foreign hooks alone.

## Step 3: force only when you mean takeover

```bash
envctl hooks install --force
envctl hooks repair --force
```

!!! warning "Use `--force` intentionally"
    `--force` allows `envctl` to overwrite foreign hooks for supported hook names in the effective managed hooks path.
    It is not a general “fix everything” switch.

## Step 4: remove only envctl-managed wrappers

```bash
envctl hooks remove
```

This removes managed wrappers only. It does not remove foreign hooks.

## Common branches

- if the hooks path is **unsupported**, fix the Git hooks path first
- if the hooks are **foreign**, decide whether envctl should really take ownership
- if hooks are **healthy** but behavior still looks wrong, the issue may be staged content or workflow assumptions, not the wrapper itself

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### guard secrets

See exactly what the managed wrappers execute.

[Open guard reference](../reference/commands/guard.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks troubleshooting

Go deeper when hook state itself is missing, drifted, foreign, or unsupported.

[Open hooks troubleshooting](../troubleshooting/hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks reference

Inspect the exact command surface and semantics.

[Open hooks reference](../reference/commands/hooks.md)
</div>

</div>
