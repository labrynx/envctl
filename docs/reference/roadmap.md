# Roadmap

## v1 (completed baseline)

The first stable version focused on a solid, secure, and deterministic foundation for managing environment files locally.

- **Core architecture**
  - Layered design (CLI, services, domain, repository, config, utils)
  - Framework-aware CLI with service-oriented command orchestration
  - XDG-based configuration with optional JSON config file
  - Unique project identification using repository fingerprint, remote URL, or local path
  - Per-project vault directories (`<slug>--<id>`)
  - Conservative local-first operating model

- **Foundation**
  - Safe local storage outside repositories
  - Deterministic initialization
  - Explicit user-driven mutation
  - Focus on small commands and predictable flows

## v2.0 (completed)

This version redefined `envctl` as a local environment control plane, shifting from file management to environment resolution, validation, and projection.

- **Core paradigm shift**
  - Environment is treated as a resolved state, not just a file
  - Repository is decoupled from vault location and filesystem links
  - Project contract becomes the center of the model
  - Projection modes become explicit workflow choices

- **Environment contract**
  - `.envctl.schema.yaml` becomes the source of truth
  - Defines required and optional variables
  - Supports descriptions, basic types, non-sensitive defaults, and sensitivity flags
  - Keeps secret values out of source control

- **Resolution model**
  - Deterministic resolution pipeline
  - Local provider remains the default value source
  - Clear distinction between missing, defaulted, and explicitly provided values

- **Projection model**
  - `envctl run -- <command>` injects the resolved environment in memory
  - `envctl sync` materializes `.env.local` as a derived artifact
  - `envctl export` prints shell export lines
  - Generated files are treated as artifacts, not sources of truth

- **Visibility and diagnostics**
  - `envctl check` validates contract satisfaction
  - `envctl inspect` shows resolved state safely
  - `envctl explain KEY` explains one variable’s resolution path
  - `envctl status` summarizes workflow readiness
  - `envctl doctor` checks local environment readiness

## v2.1–v2.2 (completed consolidation)

This phase consolidated the v2 model and made it operationally complete.

- **Contract-aware variable operations**
  - `add` creates contract definition + local value
  - `set` updates value only
  - `unset` removes value only
  - `remove` removes contract definition + local value

- **Contract inference**
  - Type inference
  - Sensitivity inference
  - Description generation
  - Defaults, examples, patterns, and choices where appropriate

- **CLI and service architecture**
  - Modular command structure
  - Better separation between CLI, services, repositories, adapters, and domain
  - Cleaner command-specific orchestration

- **Validation hardening**
  - Stronger typing
  - Contract validation with `pydantic`
  - More consistent error handling
  - Safer resolution and mutation workflows

- **Vault tooling**
  - `vault check`
  - `vault edit`
  - `vault path`
  - `vault show`
  - `vault prune`

- **Developer tooling**
  - Makefile-based workflows
  - Better test coverage
  - Improved formatting, linting, and type checking support

- **Project identity and recovery**
  - explicit local Git binding with canonical project ids
  - recovery by remote, project key, and known paths
  - repair and rebind workflows for broken or missing local state
  - backward-compatible reading of older persisted vault state

## v2.3 (current target)

This phase introduces **profile-aware workflows** without weakening the explicit local-first model.

### Profiles

- explicit profile selection with `--profile`
- `ENVCTL_PROFILE` environment override
- configurable `default_profile`
- implicit `local` profile using `values.env`
- explicit profiles stored under `profiles/<name>.env`
- no hidden inheritance between profiles

### Profile-aware resolution

- `check`, `inspect`, `explain`, and `status` resolve against the active profile
- `sync`, `export`, and `run` project the active profile
- `doctor` reports active profile and physical profile vault path
- `vault` commands operate on physical profile files

### Profile-aware value mutation

- `set`, `unset`, and `fill` operate on the active profile
- `add` writes the initial value into the active profile while updating the global contract
- `remove` removes the contract definition and cleans the value from all persisted profiles

### Profile tooling

- `profile list`
- `profile create`
- `profile copy`
- `profile remove`
- `profile path`

### Machine-readable output

- stable JSON output for selected commands
- explicit inclusion of active profile where relevant
- CLI serializers aligned with domain result types

### Runtime model cleanup

- `runtime_mode` and `profile` are separate concepts
- config validation tightened
- profile selection rules made explicit across CLI and services

### Developer onboarding

- better first-run workflows
- improved guided completion for missing values
- more helpful readiness and recovery messaging
- richer examples and onboarding documentation

### Breaking changes

v2.3 is intended as a cleanup release, not a compatibility-preserving one.

Notable breaking changes include:

- profile-aware workflows are now first-class
- `add` stores the initial value in the active profile
- `remove` removes values from all persisted profiles, not only the current local vault
- vault commands now operate on profile-specific physical files
- internal service result shapes are aligned to the new v2.3 model
- `default_profile` is part of the application configuration model
- runtime mode and profile are explicitly distinct concepts

## v2.4+

Further improvements should reduce friction while preserving explicitness.

- **Validation improvements**
  - richer type constraints
  - more expressive validation patterns
  - better contract authoring guidance
  - optional contract linting

- **Provider extensibility**
  - pluggable resolution providers
  - local provider remains the default
  - optional external providers introduced carefully
  - deterministic fallback and explicit error handling

- **Import/export workflows**
  - explicit import helpers
  - safer export workflows
  - no hidden synchronization between developers

## Later

These ideas are valuable but should only be explored once the control plane model is mature.

- Extended provider ecosystem
- Read-only CI validation mode as a more complete operational mode
- IDE integrations
- Advanced contract features introduced carefully
- Optional encryption helpers outside the core model

## Out of scope (for now)

These are intentionally excluded from the short-term roadmap.

- Cloud-first sync as a required part of the product
- Mandatory remote storage
- External secret providers as a core dependency
- Implicit synchronization between developers
- Hidden background daemons or automatic watchers
- Full encryption-at-rest inside the vault by default
- A terminal UI as a priority over contract, resolution, and projection workflows
- Hidden profile inheritance chains
- Profile-specific contract schemas as a default model

## Summary

The roadmap direction is now clearer than in early v2:

- the conceptual model is established
- the operational model is in place
- v2.3 adds explicit profile-aware workflows and model cleanup
- the next steps are about expressiveness, polish, and extensibility

That is a much healthier stage than “still deciding what the tool is”.
