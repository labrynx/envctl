# Repo Conventions

## File naming

- New files should follow the naming conventions of their sibling files.
- If a proposed file name does not match the conventions of its directory, prefer renaming or relocating it instead of introducing a one-off naming pattern.

## Layer boundaries

- Each file must match the responsibility of the layer where it lives.
- `domain/` should contain pure domain models, grammar, and business rules without process or infrastructure access.
- `adapters/` should contain access to external systems and process-level inputs such as filesystem, Git, editors, dotenv parsing, or process environment access.
- `services/` should orchestrate use cases and compose domain plus adapters; avoid placing low-level infrastructure access or pure domain grammar directly in service modules when they belong to another layer.

## Refactoring rule

- If a change reveals that a file no longer matches the objective of its layer, split or move the code into the appropriate layers before finishing the task.
