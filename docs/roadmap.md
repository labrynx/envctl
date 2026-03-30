# Roadmap

## v1 (completed baseline)

The first stable version focused on a solid, secure, and deterministic foundation for managing environment files locally.

- **Core architecture**
  - Layered design (CLI, services, domain, repository, config, utils)
  - Framework-aware CLI with service-oriented command orchestration
  - XDG-based configuration with optional JSON config file
  - Unique project identification using repository fingerprint (remote URL or local path)
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
  
## v2.3+

The next iteration should strengthen expressiveness and machine integration without weakening the explicit local-first model.

- **Validation improvements**
  - Richer type constraints
  - More expressive validation patterns
  - Better contract authoring guidance
  - Optional contract linting

- **Machine-readable output**
  - Stable JSON output for selected commands
  - Better scripting and automation support
  - Output models aligned with domain result types

- **Developer onboarding**
  - Better first-run workflows
  - Improved guided completion for missing values
  - More helpful readiness and recovery messaging

## v2.4+

Further improvements should reduce friction while preserving explicitness.

- **Multiple environments**
  - Profile-aware workflows such as `dev`, `test`, `staging`, and `prod`
  - Explicit profile selection in commands
  - Profile-aware resolution and projection

- **Provider extensibility**
  - Pluggable resolution providers
  - Local provider remains the default
  - Optional external providers introduced carefully
  - Deterministic fallback and explicit error handling

- **Import/export workflows**
  - Explicit import helpers
  - Safer export workflows
  - No hidden synchronization between developers

## Later

These ideas are valuable but should only be explored once the control plane model is mature.

- Extended provider ecosystem
- Read-only CI validation mode
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

## Summary

The roadmap direction is now clearer than in early v2:

- the conceptual model is established
- the operational model is in place
- the next steps are about expressiveness, polish, and extensibility

That is a much healthier stage than “still deciding what the tool is".
