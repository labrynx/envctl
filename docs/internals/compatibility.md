# Migration and compatibility

envctl has evolved toward a more consistent and predictable model.

This page collects the compatibility rules that still exist, how they map to the current model, and what new usage should prefer.

---

## Root contract file

The canonical root contract file is:

```text
.envctl.yaml
```

For compatibility, envctl still accepts:

```text
.envctl.schema.yaml
```

### Behavior

- envctl looks for `.envctl.yaml` first
- if it is not present, envctl falls back to `.envctl.schema.yaml`
- if both files exist, `.envctl.yaml` wins

### Recommendation

Use `.envctl.yaml` for all new repositories and migrations.

---

## Deprecated commands

The following commands are deprecated aliases:

| Deprecated | Use instead |
| --- | --- |
| `envctl doctor` | `envctl inspect` |
| `envctl explain KEY` | `envctl inspect KEY` |

### Behavior

- both aliases still work
- both emit a deprecation warning
- both are thin compatibility facades over `inspect`

### Recommendation

Use `inspect` and `inspect KEY` in all new documentation, scripts, and habits.

---

## Contract fields

### `group` → `groups`

Contracts now use:

```yaml
groups:
  - Runtime
  - Application
```

instead of:

```yaml
group: Runtime
```

#### Behavior

- `group` is still accepted
- it is normalized internally to `groups: [value]`
- it may emit compatibility warnings

#### Recommendation

Use `groups` in all new contract files.

---

### `required`

The `required` field is still accepted for compatibility, but it no longer changes runtime behavior.

#### Behavior

- it is accepted without error
- it is ignored by the engine

#### Recommendation

Do not use `required` in new contracts.

---

## JSON output

Some command payloads still include a `report` field.

### Behavior

- `report` is kept for JSON compatibility
- the canonical structure is exposed through fields such as:
  - `summary`
  - `variables`
  - `problems`
  - `runtime`
  - `contract_graph`

### Recommendation

New integrations should rely on the canonical fields instead of `report`.

---

## Contract composition

Older setups may still assume a single-file contract.

envctl now supports contract composition through imports while keeping one resolved contract model.

### Behavior

- imported contracts are composed into one resolved contract
- resolution remains deterministic
- imported files do not create isolated namespaces

### Recommendation

Model contracts around one shared namespace, even when splitting them across files.

---

## Profiles

Profiles are explicit and isolated.

### Behavior

- profiles do not inherit from each other implicitly
- there is no hidden fallback between profiles

### Recommendation

Create and manage profiles explicitly.

---

## Timeline

Compatibility features remain supported for now, but they are transitional by nature.

For concrete removal plans, refer to the changelog and release notes.

---

## Local development workflow policy

The canonical contributor workflow currently uses:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
make validate
```

### Behavior

- contributor docs and CI expectations are aligned to the editable `pip` workflow first
- `.venv` is the supported baseline for local reproduction
- `make validate` is the canonical local quality gate

### `uv.lock`

`uv.lock` is intentionally tracked, but it currently plays a narrower role.

### Behavior

- it records one tested dependency resolution state
- it may support optional local `uv` workflows
- it is not yet the canonical CI input

### Recommendation

Treat `.venv` + editable `pip install -e ".[dev]"` as the default contributor contract unless the CI/tooling policy changes explicitly.

---

## Documentation stack policy

The documentation site currently targets the MkDocs 1.x / Material 9.x line.

### Behavior

- `mkdocs build --strict` is expected to pass locally and in CI
- docs and overrides are maintained against the currently supported stack
- major-version migration of MkDocs/Material is not assumed to be safe by default

### Recommendation

- keep the current line stable unless there is a deliberate migration plan
- treat upstream major-version changes as compatibility work, not routine dependency churn
- record and review any future migration plan before changing the supported docs stack

---

## Release artifact policy

Release integrity is currently strengthened with lightweight, observable controls rather than a full attestation chain.

### Behavior

- release builds generate both wheel and source artifacts in CI
- smoke tests install the built wheel before publication
- a `SHA256SUMS` manifest is generated for released package artifacts and SBOM metadata
- a CycloneDX SBOM is generated for the built wheel
- GitHub artifact attestations are generated for release artifacts
- the checksum manifest is attached to the GitHub release alongside the package files

### Recommendation

Treat checksum verification as the minimum offline baseline for released artifacts.

If stronger provenance is added later, it should extend this policy explicitly rather than replace it silently.


## Master key compatibility

Legacy raw master keys are still accepted for compatibility, but only as a transition path.

### Behavior

- new key files are written as `ENVCTL-MASTER-KEY-V1:<key-id>:<base64-key>`
- legacy raw Fernet keys remain readable for now
- when a legacy key is loaded from disk and the file is writable, envctl migrates it automatically to the canonical format
- legacy support is deprecated and scheduled for removal in `v2.6.0`

### Recommendation

Do not create or distribute raw master keys anymore. Treat the canonical self-identifying format as the only supported format going forward.
