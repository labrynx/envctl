# Debugging

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Guide</span>
  <p class="envctl-section-intro__body">
    Debugging with <code>envctl</code> works best when you stop guessing and inspect the model step by step:
    validation, profile selection, resolution, and finally projection.
  </p>
</div>

## When to use this guide

Use this page when:

- `envctl` behaves differently from what you expected
- the application sees the wrong value
- CI, Docker, or local runtime diverges
- you are not sure which layer is actually wrong

## Starting point

Start with the smallest question first:

<div class="envctl-doc-terminal">
  <div class="envctl-doc-terminal__bar">
    <div class="envctl-doc-terminal__dots">
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--red"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--yellow"></span>
      <span class="envctl-doc-terminal__dot envctl-doc-terminal__dot--green"></span>
    </div>
    <span class="envctl-doc-terminal__title">check first</span>
  </div>
  <pre class="envctl-doc-terminal__body"><code><span class="envctl-doc-terminal__line">$ envctl check</span></code></pre>
</div>

If validation fails, stay at that layer first. Do not debug a downstream runtime before the model is valid.

## A practical debugging flow

### 1. Confirm the profile

Many “wrong value” problems are really “wrong profile” problems.

```bash
envctl --profile local check
envctl --profile dev-alt check
```

### 2. Inspect the key or the smallest useful scope

```bash
envctl inspect DATABASE_URL
envctl --group Runtime inspect
envctl --var DATABASE_URL inspect
```

Smaller surfaces make debugging faster.

### 3. Compare validation and projection

If `check` passes but the target process still behaves differently, the problem is usually no longer validation. It is projection.

### 4. Test the exact runtime handoff

```bash
envctl run -- python app.py
envctl export --format dotenv
```

Debug the path you actually use, not the one you assume exists.

## Signals that usually matter

- **validation fails** → contract or local values are still wrong
- **switching profile changes the result** → the issue is local context selection
- **inspect looks right but runtime does not** → the issue is likely projection
- **hooks or CI fail first** → that is often a clue about where the mismatch appears

## A useful rule

When something feels off, this order is usually enough:

1. validate with `check`
2. confirm the intended profile
3. inspect the key or subset that matters
4. test the real projection path
5. only then debug the downstream application itself

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### inspect

Use inspection commands when you need to stop guessing.

[Open inspect reference](../reference/commands/inspect.md)
</div>

<div class="envctl-doc-card" markdown>
### Resolution

Understand how envctl decides what is true at runtime.

[Read about resolution](../concepts/resolution.md)
</div>

<div class="envctl-doc-card" markdown>
### Common errors

See the most frequent failure shapes and their usual first move.

[Open common errors](../troubleshooting/common-errors.md)
</div>

</div>
