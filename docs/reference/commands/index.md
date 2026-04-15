# Commands

<div class="envctl-section-intro">
  <span class="envctl-section-intro__eyebrow">Reference</span>
  <p class="envctl-section-intro__body">
    This page organizes the CLI by intent rather than by alphabet.
    Use it when you know roughly what you want to do and need the exact command surface for that job.
  </p>
</div>

If you want examples and workflow context, see [Guides](../../guides/index.md). If you want the model behind these commands, see [Concepts](../../concepts/index.md).

## Global options

Available global options:

- `--version`, `-V`
- `--profile`, `-p`
- `--group`, `-g`
- `--set`
- `--var`
- `--json`
- `--install-completion`
- `--show-completion`

### Profile selection precedence

1. `--profile`
2. `ENVCTL_PROFILE`
3. config `default_profile`
4. `local`

### Contract scope selectors

- `--group LABEL` targets variables whose normalized `groups` include `LABEL`
- `--set NAME` targets one named contract set
- `--var KEY` targets one explicit variable

These selectors are mutually exclusive.

## Command groups

<div class="grid cards" markdown>

-   :material-rocket-launch-outline:{ .lg .middle } **Bootstrap**

    Prepare local config and repository state.

    - [config](config.md)
    - [init](init.md)

-   :material-file-document-edit-outline:{ .lg .middle } **Shared contract**

    Change the repository-owned environment requirements.

    - [add](add.md)
    - [remove](remove.md)

-   :material-pencil-outline:{ .lg .middle } **Local values**

    Change only the values stored for the active profile.

    - [set](set.md)
    - [unset](unset.md)
    - [fill](fill.md)

-   :material-magnify:{ .lg .middle } **Inspect and validate**

    Understand or validate resolved state before runtime.

    - [check](check.md)
    - [inspect](inspect.md)
    - [status](status.md)

-   :material-export:{ .lg .middle } **Projection**

    Hand resolved state to subprocesses, files, or stdout.

    - [run](run.md)
    - [sync](sync.md)
    - [export](export.md)

-   :material-layers-triple-outline:{ .lg .middle } **Profiles**

    Manage named local value contexts.

    - [profile](profile.md)

-   :material-database-lock-outline:{ .lg .middle } **Vault**

    Inspect and maintain physical local storage.

    - [vault](vault.md)

-   :material-identifier:{ .lg .middle } **Project identity**

    Manage binding and local project recovery.

    - [project](project.md)

-   :material-shield-alert-outline:{ .lg .middle } **Hooks and guard**

    Operate the local Git safety layer.

    - [guard](guard.md)
    - [hooks](hooks.md)

</div>

## Read next

<div class="envctl-doc-card-grid" markdown>

<div class="envctl-doc-card" markdown>
### check

Start here for the fastest pass/fail validation answer.

[Open check reference](check.md)
</div>

<div class="envctl-doc-card" markdown>
### run

Start here for the default in-memory projection path.

[Open run reference](run.md)
</div>

<div class="envctl-doc-card" markdown>
### Concepts

Go back here when the behavior only makes sense once the layers are clear.

[Open concepts](../../concepts/index.md)
</div>

</div>
