# Commands

`envctl` commands are easier to understand when grouped by responsibility.

If you want practical examples, see the [guides](../../guides/index.md).
If you want the model behind the commands, see the [concepts section](../../concepts/index.md).
For legacy behavior and migration notes, see the [compatibility guide](../../internals/compatibility.md).

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

Named profiles must be created explicitly before use with `envctl profile create <name>`.

### Contract scope selectors

- `--group LABEL` targets variables whose normalized `groups` include `LABEL`
- `--set NAME` targets one named contract set
- `--var KEY` targets one explicit variable

These selectors are mutually exclusive.

When none is provided, `envctl` uses the full contract.

Scope selectors operate on the current contract model. For legacy field behavior such as `group`, `required`, or older root contract names, see the [compatibility guide](../../internals/compatibility.md).

## Command groups

<div class="grid cards" markdown>

-   :material-file-document-outline:{ .lg .middle } **Contract mutation**

    Change the shared project contract.

    - [add](add.md)
    - [remove](remove.md)

-   :material-pencil-outline:{ .lg .middle } **Value mutation**

    Change local values only.

    - [set](set.md)
    - [unset](unset.md)
    - [fill](fill.md)

-   :material-magnify:{ .lg .middle } **Resolution**

    Inspect or validate resolved state.

    - [check](check.md)
    - [inspect](inspect.md)
    - [status](status.md)

-   :material-export:{ .lg .middle } **Projection**

    Expose resolved state to other tools.

    - [run](run.md)
    - [sync](sync.md)
    - [export](export.md)

-   :material-account-cog-outline:{ .lg .middle } **Profiles**

    Manage local value namespaces.

    - [profile](profile.md)

-   :material-database-lock-outline:{ .lg .middle } **Vault**

    Inspect or maintain physical local vault files.

    - [vault](vault.md)

-   :material-identifier:{ .lg .middle } **Project identity**

    Manage binding and recovery.

    - [project](project.md)

-   :material-shield-alert-outline:{ .lg .middle } **Security**

    Prevent secret material from being committed.

    - [guard](guard.md)

</div>

## Command pages

### Bootstrap and config

- [init](init.md)
- [config](config.md)

### Must-have commands

- [add](add.md)
- [set](set.md)
- [unset](unset.md)
- [remove](remove.md)
- [fill](fill.md)
- [check](check.md)
- [inspect](inspect.md)
- [run](run.md)
- [sync](sync.md)
- [export](export.md)

### Important supporting commands

- [status](status.md)
- [profile](profile.md)
- [project](project.md)
- [vault](vault.md)
- [guard](guard.md)

## Deprecated aliases

The canonical diagnostic path is:

- `envctl check`
- `envctl inspect`
- `envctl inspect KEY`

For compatibility, the following aliases still work:

- `envctl doctor` → `envctl inspect`
- `envctl explain KEY` → `envctl inspect KEY`

They are deprecated and should not be used in new documentation or scripts.
