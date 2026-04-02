# AGENTS.md

## Purpose

This file is the repository-specific operating contract for AI coding agents working in `envctl`.

Agents MUST treat the repository itself as the primary source of truth. Every major implementation rule in this file is grounded in repository evidence drawn from the current source layout, contributor docs, concept docs, tests, naming patterns, and repeated implementation patterns. Agents MUST prefer repository evidence over generic best practices.

This document preserves and strengthens the original repository conventions. The following foundation rules remain mandatory.

### File naming

* New files MUST follow the naming conventions of their sibling files.
* If a proposed file name does not match the conventions of its directory, agents SHOULD rename or relocate it instead of introducing a one-off naming pattern.

Repository evidence:

* command packages use `.../command.py` and grouped `.../app.py`
* presenters use `*_presenter.py`
* focused utils use responsibility-specific names such as `project_paths.py`, `masking.py`, `filesystem.py`
* tests mirror the same structure with `test_<module>.py`

### Layer boundaries

* Each file MUST match the responsibility of the layer where it lives.
* `domain/` MUST contain pure domain models, grammar, and business rules without process or infrastructure access.
* `adapters/` MUST contain access to external systems and process-level inputs such as filesystem formats, Git, editors, prompting, dotenv parsing, or process environment access.
* `services/` MUST orchestrate use cases and compose domain plus adapters. They MUST NOT absorb low-level infrastructure access or pure domain grammar that belongs elsewhere.

Repository evidence:

* `docs/internals/architecture.md`
* `CONTRIBUTING.md` architectural note
* pure models in `src/envctl/domain/*.py`
* integration boundaries in `src/envctl/adapters/*.py`
* orchestration in `src/envctl/services/*.py`

### Refactoring rule

* If a change reveals that a file no longer matches the objective of its layer, agents MUST split or move the code into the appropriate layers before finishing the task.

Repository evidence:

* recent changelog entries explicitly moved formatting and prompt logic out of commands into presenters and prompts
* the repository already evolved away from legacy formatter-based output toward clearer layer ownership

## What This Project Is

`envctl` is a local-first, contract-driven environment control plane for project environments.

Its core model MUST stay explicit:

* contract: repository-declared requirements
* vault: local machine-owned values
* profile: selected local namespace of stored values
* resolution: deterministic selection, expansion, and validation of effective values
* projection: explicit exposure of resolved values through `run`, `sync`, or `export`

Repository evidence:

* `README.md`
* `docs/getting-started/mental-model.md`
* `docs/concepts/resolution.md`
* `docs/concepts/projection.md`

Agents MUST preserve this model across code, tests, and docs.

## What This Project Is Not

Agents MUST NOT turn `envctl` into:

* a generic secrets manager
* a cloud-backed credential platform
* a system with hidden mutation in read-only commands
* a tool where generated `.env.*` files become the source of truth
* a CLI where business rules, persistence, and presentation are mixed together
* a system that blurs profile selection, runtime mode, resolution, and projection

Repository evidence:

* `README.md` explicitly says `envctl` is not a secrets manager
* `CONTRIBUTING.md` project philosophy and things to avoid
* `docs/reference/security.md`
* `docs/workflows/ci.md`
* `docs/getting-started/mental-model.md`

## Core Architectural Principles

* Agents MUST preserve architectural boundaries.
* Agents MUST NOT force new code into an existing layer when it does not fit.
* If no current layer or module properly models a new responsibility, agents SHOULD introduce a new coherent abstraction, module, or layer extension that fits the repository’s style.
* Architectural extension is acceptable only when principled and clearly better than misplacing logic.
* Accidental architectural drift is NOT acceptable.
* Agents SHOULD prefer small structural refactors over layering hacks on top of a bad fit.
* Behavior MUST remain explicit and easy to trace. Avoid hidden mutation, hidden fallback, and convenience shortcuts that obscure the model.
* Agents MUST NOT introduce convenience abstractions that weaken ownership boundaries.
* A shared abstraction is justified only when it has a single clear responsibility, correct layer placement, evidence of real reuse or strong near-term reuse, and a name and API consistent with repository-local patterns.

Repository evidence:

* `docs/internals/architecture.md`
* `CONTRIBUTING.md`
* `CHANGELOG.md` entries about separating prompts, presenters, and command orchestration

## Working Method

Before making changes, agents MUST:

* inspect the nearest sibling modules, tests, and docs for local patterns
* identify the owning layer for the change before editing code
* check whether an existing helper, presenter, serializer, prompt builder, repository helper, or test builder already covers the need
* prefer small, well-placed changes over broad speculative refactors
* keep edits scoped to the problem unless a structural refactor is necessary to preserve architecture, correctness, or testability

When the correct location is unclear, agents SHOULD:

* trace similar behavior in existing modules
* follow established dependency direction
* choose the option that improves long-term maintainability and testability
* explicitly note uncertainty rather than inventing a new pattern casually

Agents SHOULD avoid unnecessary churn.

Agents MUST NOT rename, move, reformat, or restructure unrelated code unless doing so is required to preserve architecture, correctness, testability, or documented semantics.

## Repository Structure And Layer Boundaries

### `src/envctl/cli/`

The CLI layer owns Typer integration and command interaction boundaries.

CLI code MAY contain:

* Typer command and group definitions
* option and argument parsing
* command-path and JSON or text mode branching
* calls into services
* calls into presenters, serializers, and prompt builders
* confirmation orchestration using input adapters and prompt builders
* policy decorators such as writable-runtime and text-only enforcement

CLI code MUST NOT contain:

* contract semantics
* resolution rules
* repository persistence logic
* raw dotenv, YAML, or JSON storage logic
* long inline output construction when a presenter or serializer should own it

Repository evidence:

* `src/envctl/cli/app.py`
* `src/envctl/cli/commands/*/command.py`
* `src/envctl/cli/decorators.py`
* `tests/unit/cli/commands/*`
* `tests/integration/cli/*`

### `src/envctl/cli/presenters/`

Presenters own human-oriented terminal rendering.

They SHOULD contain:

* text layout
* section ordering
* masking-aware value display
* command result rendering

They MUST NOT contain:

* business decisions
* persistence
* interactive prompting
* repository access

Repository evidence:

* `src/envctl/cli/presenters/action_presenter.py`
* `src/envctl/cli/presenters/resolution_presenter.py`
* presenter-specific unit tests in `tests/unit/cli/presenters/*`

### `src/envctl/cli/prompts/`

Prompt builders own reusable prompt text, especially for destructive operations.

They SHOULD contain:

* confirmation message construction
* reusable prompt wording patterns

They MUST NOT contain:

* user input execution
* persistence logic
* business-rule decisions beyond reflecting an already-computed plan

Repository evidence:

* `src/envctl/cli/prompts/confirmation_prompts.py`
* `tests/unit/cli/prompts/test_confirmation_prompts.py`
* changelog entries about composite confirmation messages

### `src/envctl/cli/serializers.py`

Serializers own structured JSON output.

They SHOULD contain:

* JSON-safe conversion of domain and result objects
* masking-aware structured output
* stable machine-readable payload shapes

They MUST NOT contain:

* human-oriented formatting
* command flow logic
* persistence logic

Repository evidence:

* `src/envctl/cli/serializers.py`
* `tests/unit/cli/test_serializers.py`
* `tests/integration/cli/test_json_output.py`

### `src/envctl/services/`

Services orchestrate use cases.

They SHOULD contain:

* command and application workflows
* coordination of domain, repository, config, adapters, and focused utils
* explicit validation before mutation or projection
* structured return values for CLI consumers

They MUST NOT contain:

* Typer-specific logic
* inline terminal presentation
* prompt text construction
* hidden mutation in read-only operations

Repository evidence:

* `src/envctl/services/check_service.py`
* `src/envctl/services/fill_service.py`
* `src/envctl/services/add_service.py`
* `src/envctl/services/remove_service.py`
* `src/envctl/services/export_service.py`
* service unit tests under `tests/unit/services/*`

### `src/envctl/domain/`

The domain layer MUST remain pure.

It SHOULD contain:

* core models
* request and result dataclasses that represent business meaning
* contract rules and invariants
* expansion grammar and parsing
* resolution and report models

It MUST NOT depend on:

* Typer
* filesystem access
* Git
* process environment
* YAML, JSON, or dotenv I/O
* shell execution

Repository evidence:

* `src/envctl/domain/contract.py`
* `src/envctl/domain/expansion.py`
* `src/envctl/domain/resolution.py`

### `src/envctl/repository/`

The repository layer reconstructs and persists repository and vault state.

It SHOULD contain:

* contract load and write logic
* persisted state reading, migration, and upsert logic
* project-context reconstruction and recovery
* repository identity reconstruction

It SHOULD answer “what exists and how is it reconstructed or persisted?” rather than “what should be printed?” or “how should this use case flow end-to-end?”

Repositories reconstruct and persist state. They MUST NOT become use-case orchestrators.

Repository evidence:

* `src/envctl/repository/contract_repository.py`
* `src/envctl/repository/state_repository.py`
* `src/envctl/repository/project_context.py`

### `src/envctl/config/`

The config layer owns user-level envctl configuration.

It SHOULD contain:

* config loading and validation
* config writing
* default-profile and runtime-mode resolution

Repository evidence:

* `src/envctl/config/loader.py`
* `src/envctl/config/writer.py`
* `tests/unit/config/*`

### `src/envctl/adapters/`

Adapters isolate external systems and process-level inputs.

They SHOULD contain:

* dotenv parsing and rendering
* Git access
* editor launching
* prompt and input primitives
* process-environment access

Repository evidence:

* `src/envctl/adapters/dotenv.py`
* `src/envctl/adapters/git.py`
* `src/envctl/adapters/input.py`
* `src/envctl/adapters/process_environment.py`

### `src/envctl/utils/`

Utils are allowed only for small, focused, reusable support code.

Good fits include:

* atomic writes
* narrow filesystem helpers
* masking
* shell export quoting
* project and profile path derivation
* name, id, and path normalization helpers

Agents MUST NOT create vague catch-all modules such as `helpers.py`, `misc.py`, or broad shared modules with mixed responsibilities.

Repository evidence:

* existing focused utils naming and scope in `src/envctl/utils/*`
* docs warning against oversized utils in `docs/internals/architecture.md`

### `tests/`

Tests are architectural evidence, not just regression checks.

Agents MUST treat tests as design signals, especially:

* layer-focused unit suites
* CLI integration flows
* support builders and fixtures in `tests/support/`
* CI-mode, JSON-output, profile, and projection behavior tests

Repository evidence:

* `tests/unit/**`
* `tests/integration/cli/**`
* `tests/support/builders.py`
* `tests/support/contexts.py`

## Dependency And Coupling Rules

The intended dependency direction is layered and responsibility-driven:

* `cli` depends on services and CLI-facing presentation helpers
* `services` depend on domain, repository, config, adapters, and focused utils
* `repository` depends on domain, adapters, and focused utils when needed
* `domain` remains pure and dependency-light

Agents MUST preserve this direction and MUST NOT introduce reverse or shortcut dependencies that bypass ownership boundaries.

Additional coupling rules:

* CLI-facing modules MAY depend on services, presenters, serializers, prompts, and runtime helpers.
* Services MAY depend on domain, repository, config, adapters, and focused utils.
* Services orchestrate use cases. They MUST NOT re-implement persistence primitives that belong in repositories.
* Repository MAY depend on domain, adapters, and focused utils.
* Domain MUST NOT depend on CLI, repository, config, or adapters.
* Presenters, prompts, and serializers MUST remain CLI-facing and MUST NOT be imported into domain or repository logic.
* Adapters MUST NOT depend on CLI or services.
* Utils MUST NOT absorb service or CLI business behavior.
* Agents SHOULD keep imports aligned with layer ownership and existing local patterns.
* Agents MUST NOT introduce new cross-layer import paths that bypass the intended architecture.

Repository evidence:

* `docs/internals/architecture.md`
* the actual import directions in `src/envctl/**`

## Rules For Helpers, Shared Utilities, And Duplication Avoidance

This repository already has focused abstractions for repeated behavior. Agents MUST strengthen those local abstractions instead of inventing parallel ones.

Before creating any new helper, abstraction, presenter, formatter, serializer, prompt builder, path function, repository helper, masking helper, or test builder, agents MUST first look for:

* sibling-level patterns
* repeated argument shapes
* repeated formatting conventions
* repeated filesystem and path handling
* repeated state access logic
* repeated resolution, projection, masking, and output flows

Agents MUST search for existing equivalents in the closest relevant layer before adding anything new.

Preferred order:

1. reuse an existing abstraction
2. strengthen or extend an existing local abstraction
3. extract a shared abstraction at the correct layer
4. only then create a new abstraction

Agents MUST NOT create near-duplicate helpers with slightly different names unless there is a strong architectural reason.

If a new helper differs from an existing one only by small argument or formatting variations, agents SHOULD first attempt to generalize or extend the existing abstraction instead of creating a second helper.

This rule applies especially to repeated logic involving:

* profile path handling
* sync target path handling
* vault file read and write flows
* masking behavior
* terminal status formatting
* JSON serialization shapes
* confirmation prompt construction
* command success, warning, and error summaries
* project-context loading
* contract load and write logic
* resolution validity checks before projection
* test context, report, and value builders

Repository evidence:

* path helpers centralized in `src/envctl/utils/project_paths.py`
* terminal helpers in `src/envctl/utils/output.py`
* masking in `src/envctl/utils/masking.py`
* JSON shape helpers in `src/envctl/cli/serializers.py`
* prompt builders in `src/envctl/cli/prompts/confirmation_prompts.py`
* presenter reuse across commands in `src/envctl/cli/presenters/*`
* repeated test builders in `tests/support/builders.py` and `tests/support/contexts.py`
* changelog entries explicitly calling out unification of confirmation text and removal of duplicated inline formatting

Consolidation MUST improve clarity and preserve layer correctness. It MUST NOT create:

* a vague general-purpose helper module
* a god-module that mixes unrelated concerns
* a shared abstraction that crosses CLI, service, or domain boundaries improperly

## Helper And Abstraction Decision Rules

When deciding whether a new abstraction is justified, agents MUST evaluate existing local patterns first.

### Prefer extending an existing abstraction when:

* a sibling module already owns the same kind of responsibility
* the new function has a repeated argument shape already seen nearby
* the output format matches an established presenter or serializer style
* the path, state, masking, or projection logic already exists with a narrow variation
* a test support builder already models the same shape

### Prefer extracting a new focused abstraction when:

* the same logic appears in multiple files in the same layer
* the duplication is semantic, not just textual
* the extracted abstraction can have a single clear responsibility
* the extraction reduces drift and keeps dependency direction correct

### Prefer a new module only when:

* no existing sibling abstraction is a good fit
* extending an existing module would blur its responsibility
* the new responsibility is coherent and likely reusable
* the naming and structure can follow repository-local patterns

Agents MUST prefer strengthening a local abstraction already present in the repository over inventing a parallel one.

Repository evidence:

* explicit local abstractions already exist for prompts, presenters, serializers, path builders, decorators, and test builders
* recent refactors in `CHANGELOG.md` moved logic into those abstractions rather than duplicating it

## CLI, Presentation, And Interaction Boundaries

The repository has a strong separation between command wiring, prompting, presentation, and orchestration. Agents MUST preserve it.

### CLI commands

Commands MUST remain thin orchestration shells.

They SHOULD:

* read CLI state
* call services
* branch between JSON and text output
* invoke presenters or serializers
* invoke confirmation through prompt builders and input adapters
* use existing decorators for error handling and runtime-policy enforcement

They MUST NOT:

* embed long human-facing message construction inline
* implement core business rules inline
* duplicate JSON payload shaping inline
* perform raw contract or vault persistence inline

Repository evidence:

* `src/envctl/cli/commands/check/command.py`
* `src/envctl/cli/commands/fill/command.py`
* `src/envctl/cli/commands/remove/command.py`
* `src/envctl/cli/decorators.py`

### Interactive prompts

* Interactive input MUST go through input adapters.
* Reusable confirmation messages SHOULD live in `cli/prompts/`.
* Interactive flows MUST NOT absorb business rules.
* Services SHOULD return plan-like data when the CLI needs to prompt from computed state.

Repository evidence:

* `src/envctl/adapters/input.py`
* `src/envctl/cli/prompts/confirmation_prompts.py`
* `src/envctl/domain/operations.py` plan and result dataclasses
* `src/envctl/services/fill_service.py`
* `src/envctl/services/remove_service.py`

### Presentation and serialization

* Human-readable output belongs in presenters.
* JSON output belongs in serializers.
* Sensitive values MUST remain masked in normal presentation and structured output unless a command explicitly supports raw output and follows the established confirmation pattern.
* Services SHOULD return structured data, not pre-rendered strings, unless the output is itself the projection artifact.

Repository evidence:

* `src/envctl/cli/presenters/*`
* `src/envctl/cli/serializers.py`
* `tests/unit/cli/presenters/*`
* `tests/unit/cli/test_serializers.py`
* `tests/integration/cli/test_json_output.py`

## Read-Only, Mutation, And Projection Rules

* Read-only commands MUST remain read-only.
* Mutating commands MUST remain explicit and policy-gated.
* `runtime_mode = ci` MUST restrict mutation without changing the conceptual meaning of profiles.
* Projection outputs MUST remain derived artifacts, never state sources of truth.
* `run`, `sync`, and `export` MUST operate on resolved values.
* `sync` and `export` MUST validate resolved state before producing output.

Repository evidence:

* `docs/reference/security.md`
* `docs/workflows/ci.md`
* `docs/concepts/projection.md`
* `src/envctl/cli/decorators.py`
* `src/envctl/services/sync_service.py`
* `src/envctl/services/export_service.py`
* `tests/integration/cli/test_ci_mode.py`
* `tests/integration/cli/test_profiles_projection_flow.py`

## Refactoring And Architectural Evolution Rules

Agents MUST refactor instead of patching around structural problems.

If a task exposes:

* misplaced logic
* duplicated helper code
* mixed CLI, business, and presentation concerns
* repeated path, state, or output logic in multiple places

agents SHOULD fix the structure rather than adding one more special case.

Acceptable evolution:

* extracting a new focused presenter, prompt, serializer, or helper
* splitting oversized modules by responsibility
* moving logic into the correct layer
* introducing a new coherent module when no current one is a fit

Unacceptable evolution:

* keeping business rules in CLI because the command already exists there
* stuffing unrelated logic into `utils`
* creating a parallel abstraction when a local one already exists
* preserving a bad fit because it seems cheaper in the short term

Repository evidence:

* changelog architecture cleanup entries
* existing focused abstractions in CLI and utils
* docs warning against hidden behavior and oversized utils

## Testing Expectations

Agents MUST validate changes with tests that match the affected layer and behavior.

### Required test alignment

* Domain changes MUST update domain or closest relevant unit tests.
* Service changes MUST update service unit tests.
* Repository, config, adapter, and utils changes MUST update their corresponding unit suites.
* CLI behavior changes MUST update CLI unit tests and integration tests when command flow or user-visible behavior changes.
* JSON payload changes MUST update serializer tests and integration JSON-output tests.
* Prompt and presenter changes MUST update prompt and presenter unit tests.
* Profile, resolution, projection, and CI-mode behavior changes MUST update integration tests covering those flows.

Repository evidence:

* dedicated unit suites for each layer under `tests/unit/`
* CLI integration suites under `tests/integration/cli/`
* specific JSON, CI, profile, and projection tests already present

### Test reuse rules

* Agents MUST reuse fixtures and builders from `tests/conftest.py` and `tests/support/` where possible.
* Agents MUST prefer extending shared test builders over re-creating project contexts, reports, or contracts ad hoc.
* If test setup duplication appears in multiple places, agents SHOULD extract or extend a test support helper.

Repository evidence:

* `tests/conftest.py`
* `tests/support/builders.py`
* `tests/support/contexts.py`
* `tests/support/contracts.py`

### Validation commands

For meaningful changes, agents SHOULD run the relevant subset of:

* `ruff check .`
* `ruff format --check .`
* `mypy src`
* `pytest -q`

For broad changes, prefer:

* `make check`

Repository evidence:

* `pyproject.toml`
* `Makefile`

## Change Management Expectations

Agents MUST keep code, tests, and docs aligned.

When behavior, command semantics, JSON payload shapes, compatibility surfaces, or architecture changes, agents SHOULD update the relevant docs, including as appropriate:

* `README.md`
* `CHANGELOG.md`
* `docs/reference/commands.md`
* `docs/concepts/*.md`
* `docs/internals/architecture.md`
* workflow docs

Agents MUST treat command behavior, JSON payload shapes, and documented semantics as compatibility surfaces.

Changes to these surfaces REQUIRE:

* corresponding tests
* corresponding documentation updates
* deliberate justification, not incidental drift

This is especially important for changes to:

* command grouping or identity
* read-only versus mutating behavior
* profile semantics
* resolution and expansion semantics
* projection semantics
* JSON output contracts
* CLI architecture around presenters, prompts, serializers, and services

Repository evidence:

* docs are detailed and architecture-aware
* changelog tracks internal architecture changes, not only user-facing features

## Common Pitfalls For AI Agents

Agents MUST avoid these common repository-specific mistakes:

* putting business rules in CLI commands
* embedding reusable prompt text inline inside commands
* duplicating output formatting instead of using presenters or output helpers
* duplicating JSON payload shaping instead of using serializers
* re-implementing masking logic
* re-implementing profile and path helpers instead of using `project_paths`
* duplicating vault persistence flows instead of strengthening a shared local abstraction
* leaking Git, filesystem, or process-environment access into domain code
* confusing `profile` with `runtime_mode`
* making read-only commands mutate state
* treating generated `.env.*` files as authoritative state
* inventing a new naming pattern that does not match sibling modules
* adding a catch-all utils module because the right home was not chosen carefully
* resolving uncertainty by adding ad hoc code to the nearest convenient file

Repository evidence:

* repeated command, presenter, serializer, and prompt patterns
* docs and tests enforcing read-only and CI behavior
* explicit masking, path, and support-builder abstractions already present

## When In Doubt

When the correct implementation path is unclear, agents MUST prefer:

* preserving domain purity
* keeping CLI thin
* reusing an existing local abstraction
* introducing a small focused module over misplacing logic
* updating tests and docs together with behavior

Agents MUST NOT resolve uncertainty by adding ad hoc code in the nearest convenient file.

## Definition Of Done For AI-Generated Changes

A change is only done when all of the following are true:

* the code fits the repository’s layered architecture
* new logic lives in the correct existing abstraction, or in a justified new one
* local abstractions were checked first and reused or strengthened when appropriate
* no near-duplicate helper, presenter, serializer, prompt builder, or path helper was introduced without strong justification
* CLI remains thin and presentation remains isolated
* domain purity is preserved
* read-only and mutation boundaries remain explicit
* tests were added or updated at the correct layer
* relevant validation commands were run, or unrun checks were explicitly called out
* docs were updated when user-visible behavior or architecture changed
* naming and file placement match local patterns
* no secrets or generated state were introduced into tracked repository artifacts

## Forbidden Actions

Agents MUST NOT:

* store secrets in `.envctl.schema.yaml`, docs, fixtures, or committed examples
* place infrastructure or process access in `domain/`
* put business rules directly in Typer command modules
* make read-only commands mutate state
* create competing sources of truth for runtime environment state
* conflate `profile` with `runtime_mode`
* create vague `helpers.py`, `misc.py`, or broad shared modules
* create a parallel abstraction before checking for an existing local one
* duplicate path, masking, presenter, serializer, prompt, state-access, or test-builder logic without first searching for nearby reuse
* preserve an obvious architectural misfit just to minimize edits
* ship behavior changes without corresponding tests
* ship semantic command or model changes without updating the relevant docs and changelog
