# Roadmap

This roadmap explains how `envctl` has evolved and where it is heading next.

The goal is not just to list versions, but to show how the model has become clearer over time.

---

## v1.0.0 "_Foundations_"

The first stable version focused on a solid local foundation for managing environment files safely and consistently.

### What v1.0.0 established

* layered architecture across CLI, services, domain, repository, config, and utils
* XDG-based configuration with optional JSON config
* project identification through repository fingerprint, remote URL, or local path
* per-project vault directories such as `<slug>--<id>`
* a conservative local-first operating model

### Why that mattered

v1.0.0 was about building trust in the basics:

* safe local storage outside repositories
* clear initialization
* explicit user-driven mutation
* small commands with visible behavior

That version gave `envctl` a stable base, but it still thought a little too much in terms of environment files rather than environment state.

---

## v2.0.0 "_The Shift_"

v2.0.0 was the big conceptual shift.

This is where `envctl` became a local environment control plane rather than just a tool for moving env files around.

### What changed

* environment started being treated as a resolved state, not just a file
* the repository was decoupled from vault location and filesystem links
* the project contract became the center of the model
* projection modes became explicit workflow choices

### Contract model

* `.envctl.schema.yaml` became the main source of truth for project requirements
* required and optional variables could be declared explicitly
* descriptions, basic types, non-sensitive defaults, and sensitivity flags became part of the shared model
* secrets stayed out of source control

### Resolution model

* values were resolved through a clear pipeline
* the local provider remained the default value source
* missing values, defaults, and explicit values became easier to distinguish

### Projection model

* `envctl run -- <command>` injects resolved state in memory
* `envctl sync` generates `.env.local` as an artifact
* `envctl export` prints shell export lines
* generated files are treated as outputs, not the source of truth

### Visibility and diagnostics

* `envctl check` established contract validation as a first-class workflow
* early diagnostic and inspection flows started to take shape
* later v2 releases expanded these into a broader visibility model

This was the release where the tool became much clearer about what it actually is.

---

## v2.2.0 "_Consolidation_"

v2.2.0 was the consolidation release for the early v2 model.

### Contract-aware variable operations

* `add` creates a contract definition and a local value
* `set` updates value only
* `unset` removes value only
* `remove` removes the contract definition and local value

### Contract inference

* type inference
* sensitivity inference
* description generation
* support for defaults, examples, patterns, and choices where appropriate

### CLI and service structure

* more modular command structure
* cleaner separation between CLI, services, repositories, adapters, and domain
* clearer command-specific orchestration

### Validation hardening

* stronger typing
* contract validation with `pydantic`
* more consistent error handling
* safer resolution and mutation flows

### Vault tooling

* `vault check`
* `vault edit`
* `vault path`
* `vault show`
* `vault prune`

### Developer tooling

* Makefile-based workflows
* better test coverage
* improved formatting, linting, and type checking support

### Project identity and recovery

* explicit local Git binding with canonical project ids
* recovery by remote, project key, and known paths
* repair and rebind workflows for broken or missing local state
* backward-compatible reading of older persisted vault state

This phase did not redefine the model. It made the model usable in a more complete and maintainable way.

---

## v2.3.0 "_Multiplicity_"

v2.3.0 completes the transition to **profile-aware workflows** as a first-class part of the model.

At its core, this version is about multiplicity: multiple environments, explicitly defined, without ambiguity.

The key idea is simple: multiple local value sets should be supported cleanly, without weakening the explicit local-first design.

### Profiles

* explicit profile selection with `--profile`
* `ENVCTL_PROFILE` environment override
* configurable `default_profile`
* implicit `local` profile using `values.env`
* explicit profiles stored under `profiles/<name>.env`
* no hidden inheritance between profiles

### Profile-aware resolution

* `check`, `inspect`, `explain`, and `status` resolve against the active profile
* `sync`, `export`, and `run` project the active profile
* `doctor` reports the active profile and the physical profile vault path
* `vault` commands operate on profile-specific files

### Profile-aware value mutation

* `set`, `unset`, and `fill` operate on the active profile
* `add` writes the initial value into the active profile while updating the contract
* `remove` removes the contract definition and cleans values from all persisted profiles

### Profile tooling

* `profile list`
* `profile create`
* `profile copy`
* `profile remove`
* `profile path`

### Machine-readable output

* structured JSON output for core read commands
* explicit inclusion of active profile
* serializers aligned with domain result types

### Runtime model cleanup

* `runtime_mode` and `profile` are fully separated
* configuration validation is stricter
* profile selection rules are explicit and predictable

### Developer onboarding

* clearer first-run flows
* improved guided completion for missing values
* better readiness and recovery messaging

### Breaking changes

* profile-aware workflows are now first-class
* `add` stores its initial value in the active profile
* `remove` removes values from all profiles
* vault commands are profile-aware
* `default_profile` is part of config
* runtime mode and profile are fully independent

---

## v2.4.0 "_Intent_"

v2.4.0 focuses on **execution confidence and predictability**.

At its core, this version is about intent: understanding what will happen before it happens.

The goal is simple: before mutating anything, users should be able to clearly see what will happen.

### What changes

v2.4.0 formalizes the **planning-first execution model** introduced in v2.3.0.

While earlier versions introduced plan-based execution for selected commands, v2.4.0 makes this model consistent across the CLI.

### Execution planning

Mutating commands follow a structured flow:

```text
plan → confirm → execute
```

Execution plans describe:

* affected profiles
* contract mutations (if any)
* value changes (old → new)
* generated artifacts

### Plan as a first-class concept

Plans become explicit domain objects:

* `AddPlan`
* `SetPlan`
* `RemovePlan`
* `SyncPlan`

This reinforces the separation between:

* inspection
* intent
* execution

### Dry-run support

```bash
envctl <command> --dry-run
```

Allows users to inspect the execution plan without applying changes.

### Improved confirmations

Interactive confirmations reflect the actual execution plan:

```text
This will:
  - update the contract
  - modify 2 profiles
  - remove 1 value permanently
```

### Why this matters

This release shifts `envctl` from a command-based tool to a **predictable execution system**.

Users no longer need to guess what a command might do.
They can see it before it happens.

---

## v2.5.0 "_Visibility_"

v2.5.0 focuses on **state awareness and observability**.

At its core, this version is about visibility: being able to understand the entire environment as a single object.

### What changes

v2.5.0 explores the concept of an **environment snapshot**.

### Environment snapshots (proposed)

```bash
envctl snapshot
```

The goal is to produce a structured representation of:

* resolved values
* missing variables
* validation status
* value origins

This snapshot is:

* machine-readable
* reproducible
* suitable for automation

### Environment diffing (proposed)

```bash
envctl diff --profile dev staging
```

Allows comparison between environments:

* understanding differences across profiles
* debugging environment-specific issues
* validating promotion workflows

### Drift detection (proposed)

```bash
envctl drift
```

Detects inconsistencies such as:

* undeclared variables
* missing required values
* stale profile entries

### Optional lock file (proposed)

```text
.envctl.lock.json
```

Captures a non-sensitive snapshot of the environment for reproducibility and auditing.

### Why this matters

The goal of this release is to make the environment:

* visible
* comparable
* inspectable as a whole

Instead of reasoning about individual variables, users can reason about the **entire state**.

---

## Future evolution

After v2.5.0, the focus shifts toward **extensibility and controlled flexibility**, without compromising the core model.

The goal is not to turn `envctl` into a full environment management platform, but to keep it focused on explicit, local-first workflows.

### Resolution providers

Allowing values to be resolved from different sources:

* local (default)
* process environment
* files
* optional external providers

These must remain:

* explicit
* opt-in
* deterministic

### Provider extensibility

A plugin model for resolution providers, enabling integrations without making them core dependencies.

### Policy-aware validation

Different execution contexts may enforce different rules:

* stricter validation in CI
* relaxed behavior locally
* explicit runtime policy selection

### Advanced validation

* richer type constraints
* more expressive validation rules
* contract linting and authoring guidance

### Import and export workflows

* explicit import helpers
* safer export strategies
* no hidden synchronization between developers

---

## Out of scope for now

These are intentionally not short-term goals:

* cloud-first sync as a required part of the product
* mandatory remote storage
* implicit synchronization between machines
* hidden background processes or watchers
* full encryption at rest inside the core model
* profile inheritance chains
* profile-specific contract schemas as the default model

---

## Summary

The direction remains deliberate:

* the conceptual model is established
* the operational model is stable
* v2.3 introduces profile-aware environments
* v2.4 introduces execution predictability
* v2.5 introduces full state visibility
* future work focuses on extensibility without losing clarity

The goal is not to add features quickly, but to evolve the system without losing its core properties:

* explicit behavior
* deterministic resolution
* local-first design
* no hidden magic
