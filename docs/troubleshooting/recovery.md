# Recovery

Recovery is for situations where the local state is not just “failing one check”, but has become unhealthy enough that normal workflows no longer feel reliable.

This page is a playbook for getting back to a sane state.

## When to use this page

Use this page when:

* local binding feels broken or ambiguous
* the vault looks inconsistent
* a profile exists but no longer behaves the way you expect
* the contract and local state appear out of sync

If you are only debugging one command failure, start with [Common errors](common-errors.md) first.

## Recovery path 1: contract changed, local values are now incomplete

This is the most common recovery case.

### What happened

The project contract evolved, but your machine has not yet caught up.

### What to do

Validate first:

```bash
envctl check
```

Then fill only what is now missing:

```bash
envctl fill
```

If one key is still confusing:

```bash
envctl inspect KEY
```

### Healthy end state

`check` passes again and the selected profile satisfies the current contract.

## Recovery path 2: wrong or missing explicit profile

### What happened

You expected one local setup, but the active profile is different, missing, or underfilled.

### What to do

Create the profile if needed:

```bash
envctl profile create dev
```

Then refill and validate it explicitly:

```bash
envctl --profile dev fill
envctl --profile dev check
```

### Healthy end state

The intended profile exists, validates cleanly, and can be selected explicitly in normal workflows.

## Recovery path 3: projected file is misleading or stale

### What happened

A generated dotenv file has drifted away from the current resolved state or has started being treated as the source of truth.

### What to do

Regenerate it from the current model:

```bash
envctl sync
```

If the file is not actually required, switch back to direct runtime projection:

```bash
envctl run -- python app.py
```

### Healthy end state

Projection artifacts are back to being disposable outputs instead of hand-edited state.

## Recovery path 4: Docker or downstream tooling still does not see the right environment

### What happened

The resolved environment is valid, but the downstream tool is consuming it through the wrong interface.

This is common with Docker, shell chaining, or tools that explicitly expect a file.

### What to do

Choose the handoff shape that the downstream tool actually consumes:

```bash
envctl run -- make test
envctl export --format dotenv > /tmp/app.env
docker run --env-file /tmp/app.env my-image
```

Do not assume that host-side process injection automatically becomes container-side state.

### Healthy end state

The downstream tool receives the resolved environment through an explicit interface that matches its own expectations.

## Recovery path 5: binding is broken or ambiguous

### What happened

The current checkout no longer points cleanly at the expected local project state.

Typical triggers include:

* moved repositories
* copied checkouts
* partially restored local state
* local Git config no longer matching the vault state

### What to do

Start with the safest repair path:

```bash
envctl project repair
```

If you know you need lower-level control:

* `envctl project bind ID`
* `envctl project unbind`
* `envctl project rebind`

Use those only when you understand which local project identity you want to restore.

### Healthy end state

The current checkout resolves to one clear local project identity and normal commands can trust the local context again.

## Recovery path 6: vault contents look wrong

### What happened

The question is no longer “what is the resolved runtime state?” but “what is physically stored right now?”.

### What to do

Inspect the physical stored values:

```bash
envctl vault show
```

If you need the exact storage location:

```bash
envctl vault path
```

If old or undeclared keys are cluttering the vault:

```bash
envctl vault prune
```

Use `vault edit` only when you intentionally need low-level repair of the stored file itself.

### Healthy end state

The stored vault data matches the contract shape you actually expect, and higher-level commands stop surfacing confusing state.

## Recovery path 7: start from known-good basics

If the local setup is deeply confusing and you no longer trust what changed where, fall back to a simple recovery sequence:

```bash
envctl check
envctl inspect
envctl fill
envctl check
```

If the problem is clearly lower-level than resolution:

```bash
envctl vault show
envctl project repair
```

This gives you a path back from:

* validation
* to full context
* to missing-value recovery
* to binding or storage repair if needed

## The recovery rule that matters most

Always recover toward the model, not around it.

That means:

* fix the contract if the shared requirements are wrong
* fix local values if the machine state is incomplete
* fix binding if the checkout identity is wrong
* regenerate projection artifacts instead of editing them into existence

Recovery is easiest when each layer returns to its proper responsibility.
