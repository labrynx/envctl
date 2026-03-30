# Projection

Projection makes the resolved environment usable.

It does not define state.
It only exposes it.

## Modes

### run

```bash
envctl run -- app
```

* injects values into subprocess
* no file created
* safest mode

---

### sync

```bash
envctl sync
```

* creates `.env.local`
* explicit artifact
* safe to delete

---

### export

```bash
envctl export
```

* prints shell export lines
* shell-specific

---

## Important rule

Projection output is NOT the source of truth.

It is always derived.

## Why this matters

Avoids:

* stale `.env.local`
* conflicting sources
* hidden state

## See also

* [Resolution](resolution.md)
