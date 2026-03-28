# Architecture in Depth

This document explains the internal structure of `envctl` beyond the user-facing command model.

It is intended for contributors and maintainers who need to understand how commands are implemented, how responsibilities are separated, and where new logic should live.

## Goals of the internal architecture

The internal structure of `envctl` is designed to preserve a few core properties:

- explicit behavior
- deterministic flows
- small focused modules
- testable business logic
- minimal coupling to the CLI framework
- clear separation between workflow orchestration and low-level persistence
- no hidden mutation in read-only commands

The codebase is intentionally local-first and conservative. It avoids hidden behavior, implicit background work, and broad utility modules with mixed responsibilities.

---

## High-level layering

The package is organized into the following internal layers:

- **CLI layer** (`cli/`)
- **Service layer** (`services/`)
- **Domain layer** (`domain/`)
- **Repository layer** (`repository/`)
- **Config layer** (`config/`)
- **Utility layer** (`utils/`)

These layers are not strict in the enterprise-framework sense, but they define intended responsibilities and dependency direction.

### Intended dependency direction

In general, dependencies should flow like this:

```text
CLI -> Services -> Domain / Repository / Config / Utils
Repository -> Domain / Utils
Config -> Domain / Utils
Utils -> no domain knowledge when possible
```

The CLI should not implement business logic.

Services should not depend on Typer or terminal formatting.

Repositories should not decide command policy.

Utilities should remain small and reusable.

---

## Core architectural model

At a product level, `envctl` is based on three concerns:

* **contract**
* **resolution**
* **projection**

The internal architecture should reinforce that model.

### Contract

The contract defines what a project expects.

Typical responsibilities:

* load `.envctl.schema.yaml`
* parse declared variables
* represent required vs optional keys
* represent allowed defaults and sensitivity flags
* validate shape and structure

### Resolution

Resolution determines the effective environment state.

Typical responsibilities:

* load explicit local values from the provider
* combine them with contract defaults when allowed
* identify missing required values
* explain how each key is satisfied or why it is not

### Projection

Projection makes the resolved state usable.

Typical responsibilities:

* render shell exports
* inject variables into a subprocess
* materialize a generated `.env.local` file
* preserve safe overwrite behavior

That conceptual split matters. It prevents the tool from drifting back into “just manipulate one file” thinking.

---

## Layer responsibilities

## CLI layer

Location:

```text
src/envctl/cli/
```

The CLI layer is responsible for:

* defining Typer commands
* parsing arguments and options
* mapping service results into terminal output
* mapping domain exceptions into exit codes
* handling framework-specific callbacks such as `--version`

The CLI layer should not:

* parse contract files directly
* read or write provider storage directly
* implement workflow policy
* decide how resolution behaves
* build command logic inline

### Typical CLI structure

```text
cli/
├── app.py
├── callbacks.py
├── decorators.py
├── formatters.py
└── commands/
```

### Examples

* `cli/app.py` defines the Typer application and registers commands
* `cli/decorators.py` converts `EnvctlError` exceptions into exit code `1`
* `cli/formatters.py` renders structured results for humans
* `cli/commands/*.py` contain one command wrapper each

This keeps CLI concerns isolated and makes the service layer reusable in tests.

---

## Service layer

Location:

```text
src/envctl/services/
```

The service layer contains one orchestration module per command or workflow.

A service is the place where a command's workflow is coordinated. A typical service:

* loads configuration
* resolves repository context
* loads a contract
* accesses local provider state
* performs sequencing and safety checks
* returns a domain object or a small structured result

The service layer should not:

* contain terminal formatting logic
* depend on Typer
* parse CLI flags directly
* become a dumping ground for generic helpers

### Typical service families in v2

Services usually fall into one of these groups:

* **bootstrap and readiness**

  * `config_service.py`
  * `init_service.py`
  * `doctor_service.py`
  * `status_service.py`

* **contract and resolution**

  * `check_service.py`
  * `fill_service.py`
  * `inspect_service.py`
  * `explain_service.py`
  * `resolution_service.py`

* **projection**

  * `export_service.py`
  * `run_service.py`
  * `sync_service.py`

* **local provider mutation**

  * `set_service.py`

### Design rule

If logic is specific to one workflow and not reusable, it may stay in the service.

If it looks reusable across commands, it probably belongs in `utils/`, `repository/`, or occasionally `domain/`.

---

## Domain layer

Location:

```text
src/envctl/domain/
```

The domain layer defines the structured objects that represent internal application state and command results.

Examples may include:

* `AppConfig`
* `ProjectContext`
* `ProjectContract`
* `ContractVariable`
* `ResolutionResult`
* `ResolvedValue`
* `DoctorCheck`
* `StatusReport`

The domain layer gives names and structure to the concepts that matter in `envctl`.

It exists to avoid loose dictionaries and unstructured tuples for meaningful application concepts.

### What belongs here

* immutable dataclasses
* explicit command result models
* contract models
* resolution models
* structured diagnostics

### What does not belong here

* filesystem helpers
* JSON or YAML parsing mechanics
* CLI rendering
* command registration
* shell execution details

---

## Repository layer

Location:

```text
src/envctl/repository/
```

The repository layer bridges persisted local state and structured domain objects.

In v2, this mostly means:

* reading the repository contract
* reconstructing project context from repository and config
* reading and writing local provider state
* translating local persisted records into typed domain objects

This layer exists because persistence and state reconstruction are more than raw filesystem tasks, but less than full command orchestration.

### Typical repository modules

* `contract_repository.py`
* `project_context.py`
* `state_repository.py`

### Responsibilities

#### `contract_repository.py`

Responsible for:

* locating the repository contract
* parsing `.envctl.schema.yaml`
* validating that its structure is usable
* converting raw file content into typed contract models

#### `project_context.py`

Responsible for:

* determining repository root
* resolving slug and fingerprint
* deriving contract paths and local vault paths
* building a typed `ProjectContext`

#### `state_repository.py`

Responsible for:

* reading locally stored values
* writing explicit local values
* persisting provider-side state in a consistent format

### Why this is separate from `utils/`

Contract loading and state reconstruction are domain-aware.

They are not generic helpers in the same sense as atomic file writing or shell quoting.

Placing them in `repository/` makes that boundary explicit.

---

## Config layer

Location:

```text
src/envctl/config/
```

The config layer is responsible for:

* resolving default paths
* loading optional user config
* validating config values
* writing the initial config file

### Typical config modules

* `defaults.py`
* `loader.py`
* `writer.py`

### Why this is separate

Configuration is application-level behavior, not generic utility behavior.

It knows about:

* the config path
* the vault path
* the projected env filename

That makes it more specific than a low-level helper module.

---

## Utility layer

Location:

```text
src/envctl/utils/
```

The utility layer contains small helper functions that are reusable and ideally focused on one kind of task.

### Typical utility modules

* `atomic.py`
* `dotenv.py`
* `filesystem.py`
* `git.py`
* `masking.py`
* `output.py`
* `permissions.py`
* `project_ids.py`
* `project_names.py`
* `project_paths.py`
* `shells.py`
* `tilde.py`

### Design rules for utilities

A utility module should:

* do one thing well
* avoid knowing too much about workflow orchestration
* avoid returning command-specific result structures
* remain reusable across services

A utility module should not become a mixed “misc” file.

### Good utility candidates

* atomic file writing
* path rendering with `~`
* slug generation
* repository fingerprint calculation
* dotenv normalization
* secret masking
* shell quoting

### Bad utility candidates

* “resolve the whole environment for this command”
* “decide whether `check` should fail”
* “render a status paragraph”
* “ask the user which value to keep”

Those belong in services or the CLI layer.

---

## Command flow example: `envctl init`

`init` is a good example of a bootstrap flow.

### CLI layer

`cli/commands/init.py`

Responsibilities:

* receive the optional `PROJECT` argument
* call `run_init(project_name=project)`
* print the resulting project context or initialization summary

It does not:

* compute the repository fingerprint
* parse the contract
* create provider storage directly

### Service layer

`services/init_service.py`

Responsibilities:

* load config
* build project context
* ensure local vault directories exist when needed
* detect whether a contract file exists
* prepare local state for future resolution workflows
* remain deterministic and side-effect conscious

### Repository layer

`repository/project_context.py`

Responsibilities:

* determine repo root
* resolve slug
* compute stable project identity
* derive contract and local storage paths
* return a typed `ProjectContext`

### Utility layer

Used by the init flow:

* `utils.filesystem.ensure_dir`
* `utils.permissions.ensure_private_dir_permissions`
* `utils.project_ids.build_repo_fingerprint`

### Simplified flow

```text
init command
  -> run_init()
     -> load_config()
     -> build_project_context()
     -> ensure local storage exists
     -> detect contract
     -> return initialization result
  -> print result
```

---

## Command flow example: `envctl check`

`check` shows the central v2 pattern.

### CLI layer

`cli/commands/check.py`

Responsibilities:

* call `run_check()`
* render the structured validation result
* translate failure into a non-zero exit code

### Service layer

`services/check_service.py`

Responsibilities:

* load config
* resolve project context
* load the contract
* resolve current environment state
* validate the result against the contract
* return a structured result

### Repository layer

* reads the contract
* reads local provider values
* reconstructs project context

### Domain layer

The service returns explicit result objects rather than plain strings.

### Why this matters

Returning structured objects makes it easier to:

* test behavior precisely
* add future machine-readable output
* keep human rendering separate from workflow logic

---

## Command flow example: `envctl run`

`run` shows the projection side of the architecture.

### CLI layer

`cli/commands/run.py`

Responsibilities:

* receive the child command and its arguments
* call `run_command(...)`
* exit with the child process exit code

### Service layer

`services/run_service.py`

Responsibilities:

* load config
* resolve project context
* load the contract
* resolve and validate the environment
* inject values into the subprocess environment
* execute the child process safely

### Utility layer

Common helpers may include:

* shell quoting or argument handling
* environment map preparation
* masking for diagnostic output

### Simplified flow

```text
run command
  -> run_command()
     -> load_config()
     -> build_project_context()
     -> load_contract()
     -> resolve_environment()
     -> validate_environment()
     -> spawn subprocess with injected env
     -> return child exit code
```

---

## Why `domain` and `repository` matter even more in v2

Originally, a flatter layout can work for a small CLI. But once a tool has:

* a schema/contract
* multiple resolution sources
* multiple projection modes
* richer diagnostics

a flatter structure becomes fragile.

### Why `domain` matters

Without `domain`, the project drifts toward:

* loose dictionaries
* hidden assumptions in service code
* unclear command result shapes
* harder testing

### Why `repository` matters

Without `repository`, contract loading and local state logic tend to leak into:

* services
* utils
* multiple commands independently

That duplication becomes a long-term maintenance problem.

---

## Guidelines for adding new code

When adding new functionality, use the following questions.

## Should this go in `cli/`?

Put it in `cli/` if it is about:

* Typer command registration
* help and callbacks
* terminal output rendering
* exit-code handling

## Should this go in `services/`?

Put it in `services/` if it is about:

* orchestrating one workflow
* coordinating config, repositories, and helpers
* sequencing validations and side effects
* returning a domain result

## Should this go in `domain/`?

Put it in `domain/` if it is:

* a typed result object
* a stable application concept
* part of contract or resolution semantics
* something multiple layers refer to structurally

## Should this go in `repository/`?

Put it in `repository/` if it is about:

* contract persistence and loading
* local state persistence and loading
* rebuilding typed state from persisted records
* translating files into domain objects

## Should this go in `utils/`?

Put it in `utils/` if it is:

* small
* focused
* reusable
* not strongly coupled to one workflow or domain outcome

---

## Anti-patterns to avoid

### 1. Fat utility modules

Do not create big helper files that mix:

* filesystem primitives
* contract parsing
* local state reading
* workflow policy
* rendering

That is exactly what the layered design is trying to avoid.

### 2. Typer inside services

Services should remain independent from the CLI framework.

Do not import Typer into services.

### 3. Raw dictionaries for meaningful domain concepts

If something has a stable shape and meaning, it probably deserves a domain model.

### 4. Output logic inside services

Do not have services build terminal-friendly paragraphs or colored output.

That belongs in the CLI layer.

### 5. Treating projected files as sources of truth

A generated `.env.local` file is a projection artifact.

It should not silently become the canonical state of the system.

### 6. Mixing contract and local config

Do not let user config define project requirements.

Do not let project contracts define local machine-specific paths.

---

## Future evolution

This structure is intended to support future work such as:

* richer contract validation
* additional resolution sources
* provider plugins
* machine-readable outputs
* profile-aware resolution
* read-only CI validation flows

The current layering makes those additions easier because:

* domain results are structured
* project and provider state resolution are centralized
* CLI rendering is already separate from workflow logic

---

## Summary

The internal architecture of `envctl` is designed to keep the project:

* understandable
* local-first
* deterministic
* testable
* extensible without turning into a monolithic CLI script

At a practical level:

* the **CLI** talks to the user
* the **services** orchestrate workflows
* the **domain** defines meaningful structures
* the **repository** resolves contracts and local state
* the **config** layer handles user configuration
* the **utils** provide focused helpers

When in doubt, prefer explicit boundaries over convenience.
