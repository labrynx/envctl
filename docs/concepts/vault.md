# Vault

The vault stores local values outside version control.

If the contract says what the project requires, the vault is where one machine keeps the real values it currently has.

!!! warning "The vault is not `.env.local`"
    The vault is persistent local storage. `.env.local` is only a generated projection artifact when you use `sync`.

## What the vault is

The vault is:

* local
* machine-owned
* outside Git
* the physical storage layer for real values

This is where values written by commands such as `add`, `set`, and `fill` ultimately live.

## What the vault is not

The vault is not:

* the contract
* a generated `.env.local`
* user-level config
* the resolved runtime environment

Those distinctions matter because they keep storage, intent, and runtime behavior from collapsing into one blurry thing.

## Vault vs contract

The clean split looks like this:

* the **contract** defines what the project needs
* the **vault** stores what this machine actually has

That is why contract files belong in the repository, while vault data does not.

If the vault were committed to Git, it would stop being local state and start leaking machine-specific or sensitive data into shared project history.

## Vault vs profiles

Profiles are not a separate storage system from the vault.

They are different local value sets inside the same vault-backed project state.

In other words:

* the vault is the storage layer
* profiles are named slices of local values inside that storage

That is why switching profiles changes which local values are active, but does not change the shared project definition.

## Vault vs `.env.local`

This is the mapping people get wrong most often.

The vault is **not** `.env.local`.

`.env.local` is a generated artifact when you use `sync`.
The vault is the real local storage backing the model.

That means:

* the vault is persistent local state
* `.env.local` is disposable output
* the vault is storage
* `.env.local` is projection

If a generated env file is deleted, you can recreate it.
If the vault is wrong, the underlying local state is wrong.

## Why this matters

Keeping the vault separate from both the contract and generated artifacts helps avoid a few classic mistakes:

* treating `.env.local` as the source of truth
* committing local values by accident
* confusing “what the project needs” with “what this machine currently has”

In short:

> the contract is shared intent, the vault is local truth

## Read next

Follow local storage into the rest of the model:

<div class="grid cards envctl-read-next" markdown>

-   **Contract**

    Revisit the shared requirements that the vault never replaces.

    [Read about the contract](contract.md)

-   **Profiles**

    See how named local contexts sit on top of vault-backed state.

    [Read about profiles](profiles.md)

-   **Projection**

    Understand why `.env.local` is output, not storage.

    [Read about projection](projection.md)

</div>
