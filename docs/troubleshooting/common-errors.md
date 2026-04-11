# Common errors

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Troubleshooting</span>
  <p class="envctl-section-intro__body">
    These are the most common failure shapes when using <code>envctl</code>.
    The goal is not to memorize messages, but to identify the right layer quickly and take the smallest useful next step.
  </p>
</div>

## 1. Required variable is missing

**Usually means**

- the contract changed and the active profile has not caught up
- the wrong profile is selected

**First move**

```bash
envctl check
envctl fill
envctl check
```

If profile selection looks suspicious:

```bash
envctl --profile local check
envctl --profile dev-alt check
```

## 2. `check` passes but the application still sees the wrong value

**Usually means**

- the wrong profile is active
- the runtime is not consuming the projection path you think it is

**First move**

```bash
envctl inspect DATABASE_URL
envctl run -- python app.py
envctl export --format dotenv
```

If validation is already green, treat this as a projection problem until proven otherwise.

## 3. A teammate pulled the repo and now their setup fails

**Usually means**

- the contract changed
- their local values did not catch up yet

**First move**

```bash
envctl check
envctl fill
envctl run -- python app.py
```

That is a normal contract-change ripple, not necessarily repository corruption.

## 4. Hooks do not seem to be working

**Usually means**

- managed wrappers are missing or drifted
- another hook implementation owns the supported names
- the effective hooks path is unsupported

**First move**

```bash
envctl hooks status
envctl hooks repair
```

Only use `--force` when you intentionally want envctl to take ownership from a foreign implementation.

## 5. Docker or another tool sees something different from your shell

**Usually means**

- projection is implicit or ambiguous
- the target tool is not consuming the same handoff path you validated

**First move**

```bash
envctl check
envctl run -- docker compose up
```

If the tool needs a file instead:

```bash
envctl export --format dotenv > .env.runtime
```

## 6. CI fails but local development works

**Usually means**

- CI uses a different profile or projection path
- CI is missing values that exist locally

**First move**

```bash
ENVCTL_PROFILE=ci envctl check
```

Model CI explicitly and reproduce that path locally if possible.

## 7. You are not sure where the problem lives

Use this order:

1. `envctl check`
2. confirm the intended profile
3. inspect the variable or subset that matters
4. verify the actual projection path
5. only then debug the downstream application

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Debugging guide

Use the longer methodical flow when the problem is not obvious yet.

[Open debugging guide](../guides/debugging.md)
</div>

<div class="envctl-doc-card" markdown>
### Hooks troubleshooting

Go deeper if the issue is around managed Git protection.

[Open hooks troubleshooting](hooks.md)
</div>

<div class="envctl-doc-card" markdown>
### Recovery

Use this when you already know something is broken and want a controlled path back.

[Open recovery guide](recovery.md)
</div>

</div>
