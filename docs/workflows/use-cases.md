# Use Cases

This document collects practical ways to use `envctl`.

It is meant to help in three situations:

- when you are learning the tool for the first time
- when you want examples of real workflows
- when you just want to answer the question, “How do I do X?”

The cases move from basic to more advanced scenarios.

## Mental model reminder

Before jumping into examples, keep this simple map in mind:

- **contract** → what the project needs
- **vault** → what your machine has stored
- **profile** → which local value set is active
- **resolution** → what is actually used
- **projection** → how the result is exposed to tools

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

* your local config is created
* the repository is prepared for `envctl`
* missing required values are requested
* the environment is validated

---

# 2. Run your app without `.env.local`

## Goal

Run your app directly from the resolved environment.

```bash
envctl run -- python app.py
```

## Why this is useful

* no need to create `.env.local`
* fewer secrets written to disk
* the same model used by `check` and `inspect` also drives runtime

If the command is `docker run` or `docker compose run`, `envctl` still only injects into the Docker client process. Required container variables must be forwarded explicitly with `-e`, `--env`, or `--env-file`.

For container workflows, prefer an explicit env-file handoff:

```bash
docker run --env-file <(envctl export --format dotenv) my-image
```

Example:

```bash
envctl run -- docker run --rm -p 7002:7002 \
  -e ARIA_EVENTD_PORT \
  -e ARIA_LOG_DIR \
  -e ARIA_RELATIONAL_STORE_MODE \
  -e ARIA_RELATIONAL_STORE_PROVIDER \
  -e ARIA_RELATIONAL_STORE_DSN \
  -e ARIA_EVENT_BUS_MODE \
  -e ARIA_EVENT_BUS_PROVIDER \
  -e ARIA_EVENT_BUS_URL \
  aria-eventd:dev
```

If a containerized workflow should disable NATS instead, forward a coherent contract explicitly:

```bash
envctl run -- docker run --rm \
  -e ARIA_EVENT_BUS_MODE=disabled \
  -e ARIA_EVENT_BUS_PROVIDER=none \
  aria-eventd:dev
```

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

This is helpful when the question is not “what is stored?” but “what will actually be used?”

---

# 4. Debug one variable

## Goal

Understand why one variable is missing, invalid, or unexpected.

```bash
envctl explain DATABASE_URL
```

## Useful when

* a value is missing
* a value is invalid
* behavior is surprising
* a default is being used when you expected a stored value

---

# 5. Add a new variable to the project

## Goal

Introduce a new variable into the shared model.

```bash
envctl add REDIS_URL redis://localhost:6379
```

## What happens

* a contract entry is created or updated
* the initial value is stored in the active profile
* metadata may be inferred automatically

Remember that `add` is a shared project change, not just a local tweak.

---

# 6. Change a value locally

## Goal

Update a local value without changing the contract.

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

## When this is useful

* testing fallback behavior
* forcing `fill` to ask again
* removing a temporary override

---

# 8. Remove a variable entirely

## Goal

Delete a variable from the shared project model.

```bash
envctl remove PORT
```

## What happens

* the variable is removed from the contract
* the value is removed from all persisted profiles

This is a contract change, so it affects the project, not just your local setup.

---

# 9. After pulling contract changes

## Goal

Bring your local setup back in line with an updated contract.

```bash
envctl check
envctl fill
```

## Typical situation

* new required variables were added
* validation fails until local values are provided

---

# 10. Generate `.env.local` for compatibility

## Goal

Work with a tool that expects an env file on disk.

```bash
envctl sync
```

```bash
envctl sync --output /tmp/env.env
docker run --env-file /tmp/env.env my-image
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

```bash
docker run --env-file <(envctl export --format dotenv) my-image
```

## Notes

* mainly useful in POSIX-like shells
* `run` is usually the cleaner default when possible

---

# 12. Diagnose local issues

## Goal

Check host and project readiness.

```bash
envctl doctor
```

## Typical checks

* config issues
* runtime mode
* active profile
* vault permissions
* missing contract
* repository detection problems

---

# 13. View project status

## Goal

Get a quick workflow-oriented overview.

```bash
envctl status
```

## Typical use

* understand whether the project is ready to run
* see what action should come next

---

# 14. Inspect the physical vault file

## Goal

Check the current profile’s stored vault file.

```bash
envctl vault check
envctl vault path
envctl vault show
```

## Useful when

* you want to debug stored values directly
* you want the actual path of the physical vault file
* you want to confirm which profile file is active

---

# 15. Clean stale values

## Goal

Remove keys that are no longer declared in the contract.

```bash
envctl vault prune
```

## When useful

* the contract changed
* old variables still remain in the active profile’s vault file

---

# 16. Work with a different profile

## Goal

Use another local value set without changing the contract.

```bash
envctl --profile dev check
envctl --profile dev run -- python app.py
```

## Why this works well

* same contract
* different local values
* explicit and easy to follow

---

# 17. Create a new profile

## Goal

Start a clean local value namespace.

```bash
envctl profile create staging
```

## Typical use

You want one setup for normal development and another one for staging-like testing.

---

# 18. Copy one profile into another

## Goal

Use an existing profile as a starting point.

```bash
envctl profile copy dev staging
```

## Why this is helpful

* avoids re-entering every value by hand
* lets you create a close variant of an existing setup

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

You want a default setup and a second environment.

```bash
envctl set APP_NAME demo
envctl set DATABASE_URL postgres://localhost/dev
envctl --profile staging set APP_NAME demo-staging
envctl --profile staging set DATABASE_URL postgres://localhost/staging
```

Now you can run either one:

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

Then commit the contract change:

```bash
git add .envctl.schema.yaml
git commit
```

Other developers then satisfy that contract locally:

```bash
envctl fill
```

## Why this matters

* `add` is a shared change
* contract updates should be reviewed
* values stay local

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

## Why this sequence works

* `status` gives the broad picture
* `check` confirms whether the contract is satisfied
* `inspect` shows the resolved state
* `explain` zooms in on one key
* `vault show` reveals the physical stored values

---

# 24. Start fresh with a new project identity

## Goal

Create a new isolated environment for the same checkout.

```bash
envctl project rebind --new-project --empty
```

## Use case

This can be useful for:

* duplicated repositories
* experimental branches
* intentional identity splits

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
* recovery is needed after path or machine changes

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

This gives a clean path from clone to runnable project without passing around `.env.local` files.

---

# 27. Advanced local multi-environment workflow

## Scenario

You want `dev`, `staging`, and `ci` profiles on one machine.

```bash
envctl profile create dev
envctl profile create staging
envctl profile copy local dev
envctl profile copy dev staging

envctl --profile dev set APP_NAME demo-dev
envctl --profile staging set APP_NAME demo-staging
envctl --profile ci set APP_NAME demo-ci
```

Then you can validate or project each one explicitly:

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

`vault edit` is for explicit low-level work when you really need it.

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

A simple summary of the command model is:

* `add` → introduce variables into the shared model
* `set` → change active-profile values
* `unset` → remove active-profile values
* `remove` → delete variables from the shared model
* `profile ...` → manage local value namespaces
* `vault ...` → inspect or maintain physical vault files

And the core model remains:

> The contract defines what exists.
> The vault defines what is stored.
> The active profile selects one local value set.
> The resolved environment is what runs.
