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

## v2.0 (current branch target)

The next iteration redefines `envctl` as a local environment control plane, shifting from file management to environment resolution, validation, and projection.

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
  - Explicit local mutation through commands such as `set` and `fill`
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

## v2.1

Once the control plane model is stable, the next step is to strengthen extensibility and validation.

- **Provider system**
  - Pluggable resolution providers
  - Local provider remains the default
  - Optional external providers introduced carefully
  - Provider hints supported in the contract model
  - Deterministic fallback and explicit error handling

- **Validation improvements**
  - Richer type validation
  - Better error messages and reporting
  - Contract linting and authoring guidance
  - Optional unknown-key reporting modes

- **Machine-readable output**
  - Stable JSON output for selected commands
  - Better scripting and automation support
  - Output models aligned with domain result types

## v2.2+

Further improvements should reduce friction without weakening the explicit local-first model.

- **Multiple environments**
  - Profile-aware workflows such as `dev`, `test`, `staging`, and `prod`
  - Profile-aware resolution and projection
  - Explicit profile selection in commands

- **Developer onboarding**
  - Better first-run workflows
  - Improved guided completion for missing values
  - More helpful readiness and recovery messaging

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
