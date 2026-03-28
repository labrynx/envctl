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
- clear separation between domain logic and filesystem persistence

The codebase is intentionally local-first and conservative. It avoids hidden behavior, implicit mutation, and broad utility modules with mixed responsibilities.

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

Services should not depend on Typer or command-line formatting.

Repositories should not decide command behavior.

Utilities should remain small and reusable.

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
* handling framework-specific callbacks such as `--version` and confirmation prompts

The CLI layer should not:

* inspect repository metadata directly
* manipulate files directly
* implement command rules
* decide domain outcomes

### Current CLI structure

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
* `cli/formatters.py` renders `doctor`, `status`, and `remove` results
* `cli/commands/*.py` contain one command wrapper each

This structure keeps CLI concerns isolated and makes the service layer reusable in tests.

---

## Service layer

Location:

```text
src/envctl/services/
```

The service layer contains one orchestration module per command.

A service is the place where a command's workflow is coordinated. A typical service:

* loads configuration
* resolves repository context
* calls repository helpers
* calls utility helpers
* performs sequencing and safety checks
* returns a domain object or a small structured result

The service layer should not:

* contain terminal formatting logic
* depend on Typer
* parse CLI flags directly
* become a dumping ground for helper functions that belong elsewhere

### Current services

```text
services/
├── config_service.py
├── doctor_service.py
├── init_service.py
├── remove_service.py
├── repair_service.py
├── set_service.py
├── status_service.py
└── unlink_service.py
```

### Design rule

If logic is specific to one command and not reusable, it may stay in the service.

If it looks reusable across commands, it probably belongs in `utils/`, `repository/`, or occasionally `domain/`.

---

## Domain layer

Location:

```text
src/envctl/domain/
```

The domain layer defines the structured objects that represent internal application state and command results.

Examples:

* `AppConfig`
* `ProjectContext`
* `ProjectMetadata`
* `DoctorCheck`
* `StatusReport`
* `RemoveResult`
* `UnlinkResult`

The domain layer gives names and structure to the concepts that matter in `envctl`.

It exists to avoid passing around loose dictionaries and unstructured tuples for meaningful application concepts.

### What belongs here

* immutable dataclasses
* explicit command result models
* application concepts that are independent from Typer
* typed structures used across services and repositories

### What does not belong here

* filesystem helpers
* JSON parsing helpers
* CLI rendering
* command registration
* host-specific logic such as symlink probing

---

## Repository layer

Location:

```text
src/envctl/repository/
```

The repository layer bridges persisted local state and structured domain objects.

In `envctl`, this mostly means:

* reading and writing repository metadata
* resolving a `ProjectContext` from repository state

This layer exists because metadata persistence is not just a low-level filesystem concern, but also not a command orchestration concern.

### Current repository modules

* `metadata_repository.py`
* `project_context.py`

### Responsibilities

#### `metadata_repository.py`

Responsible for:

* writing metadata
* reading metadata
* validating whether stored metadata is structurally usable
* converting raw JSON into a typed `ProjectMetadata`

#### `project_context.py`

Responsible for:

* building a fresh `ProjectContext` during initialization
* resolving an existing `ProjectContext` from stored metadata
* failing explicitly when a repository is not initialized

### Why this is separate from `utils/`

Metadata and project context resolution are domain-aware.

They are not generic utility functions in the same sense as atomic file writing or permission helpers.

Placing them in `repository/` makes this boundary explicit.

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

### Current config modules

* `defaults.py`
* `loader.py`
* `writer.py`

### Why this is separate

Configuration is application-level behavior, not generic utility behavior.

It knows about:

* the config path
* the vault path
* the env filename
* the metadata filename

That makes it more specific than a helper module.

---

## Utility layer

Location:

```text
src/envctl/utils/
```

The utility layer contains small helper functions that are reusable and ideally focused on one kind of task.

### Current utility modules

* `atomic.py`
* `dotenv.py`
* `filesystem.py`
* `git.py`
* `output.py`
* `permissions.py`
* `project_ids.py`
* `project_names.py`
* `project_paths.py`
* `symlinks.py`
* `tilde.py`

### Design rules for utilities

A utility module should:

* do one thing well
* avoid knowing too much about command workflows
* avoid returning command-specific result structures
* remain reusable in future commands

A utility module should not become a mixed “misc” file.

### Examples

#### Good utility candidates

* atomic file writing
* path rendering with `~`
* slug generation
* repo fingerprint calculation
* dotenv key normalization
* symlink support probing

#### Bad utility candidates

* “remove envctl state”
* “repair broken repo”
* “render status report”
* “decide if a command should prompt”

Those are command- or domain-specific concerns.

---

## Command flow example: `envctl init`

The `init` command is a good example of the intended flow.

### CLI layer

`cli/commands/init.py`

Responsibilities:

* receive the optional `PROJECT` argument
* call `run_init(project_name=project)`
* print the resulting context

It does not:

* compute the project ID
* write metadata
* create the vault structure itself

### Service layer

`services/init_service.py`

Responsibilities:

* load config
* build the project context
* ensure vault directories exist
* create the managed env file if missing
* write metadata
* create the repository symlink if safe
* raise explicit errors on unsafe states

### Repository layer

`repository/project_context.py`

Responsibilities:

* determine repo root
* resolve slug
* compute stable project ID
* derive repo and vault paths
* return a typed `ProjectContext`

`repository/metadata_repository.py`

Responsibilities:

* persist the repository metadata record

### Utility layer

Used by the init flow:

* `utils.filesystem.ensure_dir`
* `utils.filesystem.ensure_file`
* `utils.permissions.ensure_private_dir_permissions`
* `utils.permissions.ensure_private_file_permissions`
* `utils.project_ids.build_repo_fingerprint`

### Result

The service returns a `ProjectContext`, which the CLI formats for the user.

### Simplified flow

```text
init command
  -> run_init()
     -> load_config()
     -> build_project_context()
     -> ensure vault structure
     -> ensure managed env file
     -> write metadata
     -> create symlink
     -> return ProjectContext
  -> print result
```

---

## Command flow example: `envctl status`

`status` shows the other main pattern: read-only evaluation.

### CLI layer

`cli/commands/status.py`

Responsibilities:

* call `run_status()`
* render the resulting `StatusReport`

### Service layer

`services/status_service.py`

Responsibilities:

* load config
* resolve repo root
* load metadata
* build a context from metadata if possible
* inspect repo and vault state
* derive a structured status report

### Repository layer

* reads typed metadata
* reconstructs project context deterministically

### Domain layer

`StatusReport` is the explicit output structure.

### Why this matters

Instead of returning loose strings or mixed dictionaries, the service returns a structured object that is easy to:

* test
* render differently later
* extend with machine-readable output in future versions

This is especially useful if `status --json` is added later.

---

## Why `domain` and `repository` were introduced

Originally, the project used a flatter layout with:

* a single `models.py`
* larger `utils` modules
* a central `cli.py`

That structure was acceptable for a small v1, but it starts to become fragile as soon as more commands and more output modes appear.

The refactor introduced two missing ideas:

### `domain`

This makes command results and internal concepts explicit.

Without `domain`, the project tends to drift toward:

* loose dictionaries
* broader helper functions
* weaker boundaries between command output and internal state

### `repository`

This makes persistence and context resolution explicit.

Without `repository`, metadata logic tends to leak into:

* services
* `utils`
* status and init code paths independently

That duplication becomes a maintenance problem over time.

---

## Guidelines for adding new code

When adding new functionality, use the following questions.

## Should this go in `cli/`?

Put it in `cli/` if it is about:

* Typer command registration
* help and callbacks
* prompt bridges
* terminal output rendering
* exit-code handling

## Should this go in `services/`?

Put it in `services/` if it is about:

* orchestrating one command
* coordinating config, repositories, and helpers
* sequencing validations and side effects
* returning a domain result

## Should this go in `domain/`?

Put it in `domain/` if it is:

* a typed result object
* a stable application concept
* something multiple layers need to refer to structurally

## Should this go in `repository/`?

Put it in `repository/` if it is about:

* metadata persistence
* rebuilding typed state from persisted state
* translating filesystem-backed records into domain objects

## Should this go in `utils/`?

Put it in `utils/` if it is:

* small
* focused
* reusable
* not strongly coupled to one command or one domain outcome

---

## Anti-patterns to avoid

### 1. Fat utility modules

Do not reintroduce big files that mix:

* filesystem primitives
* metadata persistence
* dotenv updates
* context resolution

That is exactly what the refactor is trying to avoid.

### 2. Typer inside services

Services should remain independent from the CLI framework.

Do not import Typer into services.

### 3. Raw dictionaries for meaningful domain concepts

If something has a stable shape and meaning, it probably deserves a domain model.

### 4. Output logic inside services

Do not have services build terminal-friendly paragraphs or colored strings.

That belongs in the CLI layer.

### 5. Persistence logic inside command wrappers

CLI commands should not read or write metadata directly.

---

## Future evolution

This structure is intended to support future work such as:

* `check`
* `fill`
* `status --json`
* `doctor --json`
* richer metadata fields
* controlled adoption flows
* backup-related options in repair flows

The current layering makes those additions easier because:

* domain results are already structured
* repository state resolution is centralized
* CLI rendering is already separate from business logic

---

## Summary

The internal architecture of `envctl` is designed to keep the project:

* understandable
* local-first
* deterministic
* testable
* easy to extend without turning into a monolithic CLI script

At a practical level:

* the **CLI** talks to the user
* the **services** orchestrate commands
* the **domain** defines meaningful structures
* the **repository** resolves persisted local state
* the **config** layer handles tool configuration
* the **utils** provide focused helpers

When in doubt, prefer explicit boundaries over convenience.
