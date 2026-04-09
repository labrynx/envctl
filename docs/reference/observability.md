# Observability event contract

`envctl` emits structured observation events when tracing is enabled (`ENVCTL_OBSERVABILITY_TRACE=1`).

## Event schema (stable)

Each emitted event conforms to this stable schema:

- `event` (string, required): canonical event name.
- `timestamp` (ISO-8601 datetime, required): UTC emission time.
- `execution_id` (string, required): unique ID for one CLI execution.
- `status` (string, required): lifecycle status (`start`, `finish`, `error`, or contextual states).
- `duration_ms` (integer, optional): elapsed operation time in milliseconds.
- `module` (string, optional): Python module that emitted the event.
- `operation` (string, optional): operation/function identifier.
- `fields` (object, optional): sanitized metadata (counts/state only; no secret values).

## Canonical event names

The canonical names are centralized in `src/envctl/observability/events.py`:

- `command.start`, `command.finish`, `command.error`
- `context.resolve.start`, `context.resolve.finish`, `context.resolve.error`
- `contract.compose.start`, `contract.compose.finish`, `contract.compose.error`
- `resolution.start`, `resolution.finish`, `resolution.error`
- `run.exec.start`, `run.exec.finish`, `run.exec.error`
- `vault.start`, `vault.finish`, `vault.error`
- `error.handled`, `error.unhandled`

These names and required fields are intended to remain stable for CI, telemetry parsing, and tooling integrations.

## Sensitivity guarantees

Observation `fields` are sanitized before emission:

- common secret-like keys are redacted
- non-scalar values are summarized rather than emitted verbatim
- instrumentation should report counts, booleans, and states only

Avoid adding raw environment values, key material, or file contents to event fields.

## Observability change checklist

Before merging observability-related changes, verify all items:

- **Stable event contract**: keep canonical event names and required schema fields stable; if a compatibility break is unavoidable, document it explicitly and coordinate downstream parser updates.
- **Mandatory sanitization**: ensure every new `fields` payload path passes through sanitization and does not include raw environment values, secrets, key material, or file contents.
- **Renderer snapshots updated**: refresh and review human renderer snapshots and JSONL output expectations whenever observable output changes.

## Suggested test suites for observability

Use both unit and integration coverage:

- **Unit tests** (`tests/unit/observability`): validate event contracts, sanitization behavior, renderers, emitters, timing, and recorder APIs in isolation.
- **Integration tests** (`tests/integration/cli/test_trace_observability.py`): validate end-to-end CLI trace emission, including real command lifecycle events and output formats.

## Focused validation commands

Run targeted checks during development and CI:

```bash
# Unit suite focused on observability internals
pytest tests/unit/observability -q

# Integration coverage for CLI trace observability
pytest tests/integration/cli/test_trace_observability.py -q
```
