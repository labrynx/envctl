# Use Cases

This document provides practical, progressive use cases for `envctl`.

It is designed as:

- onboarding material for new users
- a training reference for real workflows
- a quick lookup for “how do I do X?”

The cases are ordered from **basic → intermediate → advanced → real-world scenarios**.

## Mental model reminder

Before diving in:

- **contract** → what the project needs
- **vault** → what your machine has stored
- **profile** → which local value set is active
- **resolution** → what is actually used
- **projection** → how it is applied

---

# 1. First-time setup

## Goal

Start using `envctl` in a repository for the first time.

## Steps

```bash
envctl config init
envctl init
envctl fill
envctl check
```

## What happens

* config is created
* the repository is initialized
* missing values are requested
* the environment is validated

---

# 2. Run your app without `.env.local`

## Goal

Run your app using the resolved environment directly.

```bash
envctl run -- python app.py
```

## Why

* no need to create `.env.local`
* avoids leaking secrets to disk
* uses the same resolution model as `check` and `inspect`

---

# 3. Inspect what your app actually sees

## Goal

Understand the current resolved environment.

```bash
envctl inspect
```

## Example output

```text
APP_NAME = demo (vault)
PORT = 3000 (default)
DATABASE_URL = po******** (vault)
```

---

# 4. Debug one variable

## Goal

Understand why something is failing.

```bash
envctl explain DATABASE_URL
```

## Useful when

* a value is missing
* a value is invalid
* behavior is unexpected
* a default is being used when you expected a stored value

---

# 5. Add a new variable to the project

## Goal

Introduce a new variable to the shared model.

```bash
envctl add REDIS_URL redis://localhost:6379
```

## What happens

* a contract entry is created or updated
* the initial value is stored in the active profile
* metadata is inferred automatically

---

# 6. Change a value locally

## Goal

Update a value without affecting the contract.

```bash
envctl set PORT 4000
```

## Important

* the contract is **not** modified
* only the active profile changes

---

# 7. Remove a local value only

## Goal

Clear a value but keep the contract definition.

```bash
envctl unset PORT
```

## When to use it

* testing fallback behavior
* forcing `fill` to ask again
* removing a temporary override

---

# 8. Remove a variable entirely

## Goal

Delete a variable from the project.

```bash
envctl remove PORT
```

## What happens

* the variable is removed from the contract
* the value is removed from all persisted profiles

---

# 9. After pulling changes

## Goal

Sync your local setup with an updated contract.

```bash
envctl check
envctl fill
```

## Typical situation

* new required variables were added
* validation fails until you provide values

---

# 10. Generate `.env.local` for compatibility

## Goal

Work with tools that require a file on disk.

```bash
envctl sync
```

## Notes

* the file is generated
* it is safe to delete
* it is not the source of truth

---

# 11. Export values to the shell

## Goal

Use the resolved environment in the current shell session.

```bash
eval "$(envctl export)"
```

## Notes

* this is mainly aimed at POSIX-like shells
* `run` is usually a cleaner default when possible

---

# 12. Diagnose local issues

## Goal

Check host and project readiness.

```bash
envctl doctor
```

## Detects

* config issues
* runtime mode
* active profile
* vault permissions
* missing contract
* repo detection problems

---

# 13. View project status

## Goal

Get a workflow-oriented overview.

```bash
envctl status
```

## Typical use

* understand whether the project is ready to run
* identify what action to take next

---

# 14. Inspect the physical vault file

## Goal

Check the current profile vault file.

```bash
envctl vault check
envctl vault path
envctl vault show
```

## Useful when

* you want to debug stored values
* you want to inspect the actual vault file path
* you want to confirm the current active profile file

---

# 15. Clean stale values

## Goal

Remove keys that are no longer declared in the contract.

```bash
envctl vault prune
```

## When useful

* the contract changed
* old variables remain in the active profile vault

---

# 16. Work with a different profile

## Goal

Use another local value set without changing the contract.

```bash
envctl --profile dev check
envctl --profile dev run -- python app.py
```

## Why

* same contract
* different local values
* explicit and easy to reason about

---

# 17. Create a new profile

## Goal

Start a clean value namespace for another local environment.

```bash
envctl profile create staging
```

## Typical use

* you want one local setup for development and another for staging-like testing

---

# 18. Copy one profile into another

## Goal

Use an existing profile as a starting point.

```bash
envctl profile copy dev staging
```

## Why

* avoid re-entering every value by hand
* keep a close variant of an existing setup

---

# 19. Remove an explicit profile

## Goal

Delete one explicit profile file.

```bash
envctl profile remove staging --yes
```

## Notes

* this does not affect the contract
* this does not remove the implicit `local` profile

---

# 20. Use `local` and explicit profiles side by side

## Scenario

You want a default setup plus a second environment.

```bash
envctl set APP_NAME demo
envctl set DATABASE_URL postgres://localhost/dev
envctl --profile staging set APP_NAME demo-staging
envctl --profile staging set DATABASE_URL postgres://localhost/staging
```

Now:

```bash
envctl run -- python app.py
envctl --profile staging run -- python app.py
```

---

# 21. Share contract changes with the team

## Scenario

You add a variable:

```bash
envctl add API_KEY placeholder
```

Then:

```bash
git add .envctl.schema.yaml
git commit
```

Other developers:

```bash
envctl fill
```

## Why this matters

* `add` is a shared change
* contract updates must be reviewed
* values remain local

---

# 22. Work in CI

## Goal

Validate the environment in CI without mutating local state.

```bash
envctl check
```

## Notes

* `runtime_mode = "ci"` and `profile = "ci"` are different concepts
* `check` should stay read-only
* CI should fail fast when required values are missing

---

# 23. Debug a confusing resolution problem

## Scenario

Something fails and you are not sure why.

```bash
envctl status
envctl check
envctl inspect
envctl explain DATABASE_URL
envctl vault show
```

## Why this works

* `status` gives the broad picture
* `check` confirms validity
* `inspect` shows resolved state
* `explain` shows one key in detail
* `vault show` shows physical stored values

---

# 24. Start fresh with a new project identity

## Goal

Create a new isolated environment for the same checkout.

```bash
envctl project rebind --new-project --empty
```

## Use case

* duplicate repo
* experiment branch
* intentional identity split

---

# 25. Recover broken local state

## Goal

Repair missing or broken bindings.

```bash
envctl project repair
```

## Useful when

* the vault was moved
* local binding is missing
* recovery is needed after machine or path changes

---

# 26. Full onboarding workflow for a new developer

## Scenario

A new developer joins the project.

```bash
git clone repo
cd repo

envctl config init
envctl init
envctl fill
envctl check
envctl run -- npm start
```

---

# 27. Advanced local multi-environment workflow

## Scenario

You want `dev`, `staging`, and `ci` profiles locally.

```bash
envctl profile create dev
envctl profile create staging
envctl profile copy local dev
envctl profile copy dev staging

envctl --profile dev set APP_NAME demo-dev
envctl --profile staging set APP_NAME demo-staging
envctl --profile ci set APP_NAME demo-ci
```

Then:

```bash
envctl --profile dev check
envctl --profile staging check
envctl --profile ci export
```

---

# 28. Manual low-level recovery

## Goal

Inspect and edit the physical vault file directly.

```bash
envctl vault path
envctl vault edit
envctl vault show
```

## Use only when needed

Normally, `set`, `unset`, `fill`, and `profile` commands are safer.
`vault edit` is for explicit low-level work.

---

# Patterns summary

## Most common flows

### Daily work

```bash
envctl run -- <command>
```

### After pulling changes

```bash
envctl check
envctl fill
```

### Debugging

```bash
envctl inspect
envctl explain KEY
```

### Working with multiple local environments

```bash
envctl --profile dev run -- <command>
envctl --profile staging run -- <command>
```

---

# Final takeaway

Use:

* `add` → introduce variables
* `set` → change active-profile values
* `unset` → remove active-profile values
* `remove` → delete variables from the shared model
* `profile ...` → manage local value namespaces
* `vault ...` → inspect or maintain physical vault files

And remember:

> The contract defines what exists.
> The vault defines what is stored.
> The active profile selects one local value set.
> The resolved environment is what runs.
