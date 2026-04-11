# Recovery

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Troubleshooting</span>
  <p class="envctl-section-intro__body">
    Recovery in <code>envctl</code> should be deliberate.
    The goal is not to poke files until something works, but to return to a known-good state with the smallest possible blast radius.
  </p>
</div>

## When to use this page

Use this page when:

- the model has become unclear or inconsistent
- you no longer trust one local layer
- you need a controlled way back instead of random fixes

<div class="envctl-callout" markdown>
Good recovery is usually **narrow**. Do not reset more than the layer that is actually broken.
</div>

## Start by identifying the broken layer

Usually the issue is one of these:

- contract validation
- local profile values
- hooks
- projection
- local expectations rather than actual state

The safe recovery path depends on that distinction.

## Recovery path 1: validation fails after a contract change

```bash
envctl check
envctl fill
envctl check
```

Use this when the contract evolved but the local profile has not caught up yet.

## Recovery path 2: the wrong profile is active

```bash
envctl --profile local check
envctl --profile dev-alt check
envctl --profile local run -- python app.py
```

Often nothing is corrupted at all. The wrong local context was simply selected.

## Recovery path 3: one profile is no longer worth trusting

```bash
envctl profile remove dev-alt
envctl profile create dev-alt
envctl --profile dev-alt fill
envctl --profile dev-alt check
```

Use this when a profile has drifted so far that patching it is more confusing than rebuilding it cleanly.

## Recovery path 4: hooks are missing or drifted

```bash
envctl hooks status
envctl hooks repair
envctl hooks status
```

If a foreign hook intentionally owns that name and you want envctl to take over again, only then consider a forced repair.

## Recovery path 5: validation passes but runtime behavior is still wrong

```bash
envctl inspect DATABASE_URL
envctl run -- python app.py
envctl export --format dotenv
```

At that point, recovery is usually about re-establishing the exact projection path, not changing the contract or stored values.

## Recovery path 6: onboarding got messy

```bash
envctl config init
envctl init
envctl check
envctl fill
```

Use this when the machine’s local state is so unclear that the safest move is to walk the intended bootstrap path again.

## What not to do

Avoid:

- editing multiple layers at once
- deleting local state before checking the active profile
- forcing hook replacement before understanding ownership
- treating exported dotenv files as the source of truth

Those moves usually make the next diagnosis worse.

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Common errors

Use pattern-based diagnosis before choosing a recovery path.

[Open common errors](common-errors.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks troubleshooting

Go deeper when the issue is clearly in local Git protection.

[Open hooks troubleshooting](hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### Debugging guide

Use the full step-by-step model when the failure layer is still unclear.

[Open debugging guide](../guides/debugging.md)
</div>

</div>
