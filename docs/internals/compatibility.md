# Migration and compatibility

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Advanced reference</span>
  <p class="envctl-section-intro__body">
    This page collects the compatibility rules that still exist, how they map to the current model, and what new usage should prefer.
    Use it when old behavior still matters to implementation, migration, or support.
  </p>
</div>

## Root contract file

The canonical root contract file is:

```text
.envctl.yaml
```

For compatibility, `envctl` still accepts `.envctl.schema.yaml`.

## Deprecated commands

| Deprecated | Use instead |
| --- | --- |
| `envctl doctor` | `envctl inspect` |
| `envctl explain KEY` | `envctl inspect KEY` |

## Contract fields

### `group` → `groups`

`group` is still accepted for compatibility and normalized internally to `groups: [value]`. New contracts should use `groups`.

### `required`

`required` is still accepted for compatibility, but it no longer changes runtime behavior. Do not use it in new contracts.

## JSON output

Some command payloads still include a `report` field for compatibility. New integrations should rely on canonical fields such as `summary`, `variables`, `problems`, `runtime`, and `contract_graph`.

## Contract composition

Older setups may assume a single-file contract. `envctl` now supports composition through imports while still producing one resolved contract model.

## Profiles

Profiles are explicit and isolated:

- they do not inherit from each other
- there is no hidden fallback between profiles

## Contributor workflow policy

The canonical contributor workflow uses `uv` and `uv.lock` as the source of truth for dependency resolution:

```bash
uv sync --dev
make validate
````

This ensures that all contributors and CI environments operate on the same locked dependency graph.

The `uv.lock` file is part of the repository contract and must be kept in sync with `pyproject.toml` changes.

## Documentation stack policy

The docs site currently targets the MkDocs 1.x / Material 9.x line. `mkdocs build --strict` is expected to pass locally and in CI.

## Release artifact policy

Release integrity currently relies on lightweight, observable controls:

- source and wheel artifacts built in CI
- smoke tests before publication
- `SHA256SUMS` manifests
- CycloneDX SBOM generation
- GitHub provenance attestations

## Master key compatibility

Legacy raw master keys are still accepted temporarily:

- new key files are written as `ENVCTL-MASTER-KEY-V1:<key-id>:<base64-key>`
- legacy raw Fernet keys remain readable for now
- writable legacy keys are migrated automatically
- legacy support is deprecated and scheduled for removal in `v2.6.0`

## Related pages

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### Command reference

Open this when compatibility rules still affect CLI behavior.

[Open command reference](../reference/commands/index.md)
</div>

<div class="envctl-doc-card" markdown>
### Configuration reference

See where compatibility rules still shape defaults and discovery.

[Open configuration reference](../reference/configuration.md)
</div>

<div class="envctl-doc-card" markdown>
### Platform support

Reconnect legacy behavior and portability assumptions.

[Open platform support](../reference/platforms.md)
</div>

</div>
