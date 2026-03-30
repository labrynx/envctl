# envctl

`envctl` is a local environment control plane.

Instead of committing `.env.local` files, duplicating secrets across machines, or relying on symlink-based workflows, `envctl` follows a **contract-first model**:

- the repository declares **what it needs**
- each developer stores **values locally**
- `envctl` **resolves, validates, and projects** the environment safely

No secrets in the repository. No hidden coupling. No guessing.

---

## Mental model

Think of `envctl` as four explicit parts:

- a **contract** → `.envctl.schema.yaml`
- a **local vault** → your private machine-local values
- a **resolver** → combines values deterministically
- a **projection layer** → injects or materializes the environment when needed

Projection modes are interchangeable representations of the same resolved state, whether in-memory (`run`), file-based (`sync`), or shell-based (`export`).

That separation matters:

- the **contract** defines what exists
- the **vault** stores what is currently set
- the **resolved environment** is what the application actually sees
- generated files such as `.env.local` are **artifacts**, not the source of truth

---

## Repository binding

Each checkout is associated with a canonical local project identity.

This binding is stored in local Git config and points the checkout to the correct vault project.

Typical commands:

```bash
envctl project bind <project-id>
envctl project unbind
envctl project rebind --new-project
envctl project repair
```

`envctl` can also recover project identity from persisted local state using repository remote, contract metadata, and known checkout paths.

Binding controls where values live, not what they are.

---

## Core commands

### Validate the contract

```bash
envctl check
```

* Ensures all required variables are resolved
* Reports missing required keys
* Reports invalid values when type validation fails
* Fails with a non-zero exit code if the contract is not satisfied

---

### Fill missing values interactively

```bash
envctl fill
```

* Prompts only for missing required variables
* Uses contract metadata such as description, sensitivity, and defaults
* Stores values in your local vault
* Never writes secrets to the repository

---

### Inspect resolved environment

```bash
envctl inspect
```

* Shows the final resolved environment
* Masks sensitive values
* Helps understand what the runtime will actually receive

Example:

```text
Resolved values:
  APP_NAME = demo (vault)
  PORT = 3000 (default)
  DATABASE_URL = po************** (vault)
```

---

### Explain one value

```bash
envctl explain DATABASE_URL
```

Shows how one variable is resolved.

Typical output includes:

* whether the key is declared in the contract
* whether the value comes from local storage, defaults, or process environment
* whether the value is valid
* why resolution failed, when relevant

---

### Run a command with injected environment

```bash
envctl run -- python app.py
```

* Resolves and validates the environment first
* Injects values directly into the subprocess environment
* Does **not** require writing `.env.local`

This is usually the cleanest projection mode.

---

### Generate `.env.local` explicitly

```bash
envctl sync
```

* Creates `.env.local`
* Treats it as a generated artifact
* Safe to regenerate
* Safe to delete

Use this only when another tool requires a real env file on disk.

---

### Export for shell usage

```bash
envctl export
```

Example:

```bash
export APP_NAME='demo'
export PORT='3000'
```

Useful for:

```bash
eval "$(envctl export)"
```

This mode is mainly intended for POSIX-like shells.

---

## Managing variables

`envctl` makes variable operations explicit.

### Add a variable (contract + value)

```bash
envctl add DATABASE_URL postgres://user:pass@localhost:5432/app
# or
envctl add DATABASE_URL
# prompt for value
```

* Adds the variable to the contract when missing
* Stores the value locally
* Prompts for the value when not provided inline
* Infers metadata automatically:

  * type
  * sensitivity
  * description
  * defaults, patterns, choices when appropriate
* Supports interactive review for fine-tuning metadata

This is the main command for introducing a new variable into the shared model.

### Set a value (value only)

```bash
envctl set PORT 4000
```

* Updates the local value
* Does **not** modify the contract

Use this when the variable already exists in the contract and only the local value needs to change.

---

### Unset a value (value only)

```bash
envctl unset PORT
```

* Removes the local value from the vault
* Keeps the contract definition

Use this when a value should be cleared locally without changing shared requirements.

---

### Remove a variable (contract + value)

```bash
envctl remove PORT
```

* Removes the variable from the contract
* Removes the local value
* Intended for deleting the variable from the shared model

---

## Operational model

`envctl` enforces a strict separation between shared requirements and local state.

| Operation | Contract action | Local value action |
|-----------|-----------------|--------------------|
| add       | create/update   | set                |
| set       | no change       | set                |
| unset     | no change       | delete             |
| remove    | delete          | delete             |

More precisely:

* `add` creates or updates the **definition** and stores a **value**
* `set` changes the **value only**
* `unset` clears the **value only**
* `remove` deletes both the **definition** and the **value**

This avoids implicit coupling and keeps the workflow understandable.

---

## Vault commands

The vault is the local physical storage layer.

### Check the vault file

```bash
envctl vault check
```

* Verifies the vault file exists
* Verifies it is parseable
* Verifies permissions look private enough

---

### Open the vault file

```bash
envctl vault edit
```

* Opens the current vault file in your configured editor
* Useful for explicit low-level inspection or recovery

---

### Show the vault path

```bash
envctl vault path
```

Prints the exact path of the current local vault file.

---

### Show stored values

```bash
envctl vault show
```

* Shows stored local values
* Masks them by default
* Reflects raw storage state, not the fully resolved environment

This differs from `inspect`, which shows resolved runtime state.

If you use `--raw`, envctl asks for explicit confirmation before showing unmasked values.

---

### Prune undeclared values

```bash
envctl vault prune
```

* Removes keys from the local vault that are not declared in the contract
* Helps clean up stale local values after contract changes

---

## Contract file

The repository contract lives in:

```text
<repo-root>/.envctl.schema.yaml
```

Example:

```yaml
version: 1
variables:
  APP_NAME:
    type: string
    required: true
    sensitive: false
    description: Application name

  PORT:
    type: int
    required: true
    sensitive: false
    default: 3000
    description: Application port

  DATABASE_URL:
    type: url
    required: true
    sensitive: true
    description: Primary database connection URL
```

The contract may define:

* type
* required vs optional
* description
* sensitivity
* non-sensitive defaults
* example values
* validation patterns
* allowed choices

The contract must **not** contain secrets.

---

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

envctl config init
envctl init
envctl fill
envctl check
envctl run -- python app.py
```

---

## Typical workflow

### First time in a repository

```bash
envctl init
envctl fill
envctl check
```

If the contract does not exist yet, `init` can create a starter contract or infer one from `.env.example`.

`init` also establishes the local project binding and prepares persisted vault state.

---

### Day-to-day usage

```bash
envctl run -- <command>
```

This is usually the preferred way to work once local values are already set.

---

### After pulling changes

```bash
envctl check
envctl fill
```

This is the normal flow when the contract changes and new required variables appear.

---

### When debugging

```bash
envctl inspect
envctl explain KEY
envctl vault show
```

A useful distinction:

* `inspect` shows **resolved state**
* `vault show` shows **stored local values**

---

## Configuration

User configuration controls local tool behavior, not project requirements.

Default config path:

```text
~/.config/envctl/config.json
```

Typical example:

```json
{
  "vault_dir": "~/.envctl/vault",
  "env_filename": ".env.local",
  "schema_filename": ".envctl.schema.yaml"
}
```

Supported keys:

* `vault_dir`
* `env_filename`
* `schema_filename`

---

## Security model

* Secrets never leave your machine unless you explicitly project them
* `.env.local` is optional and disposable
* The contract contains **no secrets**
* Sensitive values are masked in normal output
* Read-only commands do not silently mutate state
* Local storage is kept outside repositories

Important limitation:

`envctl` assumes a trusted local machine. If the machine or account is compromised, your secrets are compromised.

---

## Design principles

* Contract-first
* Deterministic resolution
* Explicit over implicit
* No hidden state
* Local-first, no required cloud dependency
* Generated files are artifacts, not sources of truth

---

## Roadmap (short)

* Richer validation constraints
* Better contract authoring guidance
* Machine-readable output for selected commands
* Profile-aware workflows
* Optional provider extensibility

---

## Why not plain `.env` files?

Because they:

* get duplicated
* drift out of sync
* blur shared requirements and machine-local values
* leak secrets into the wrong places
* become the source of truth by accident

`envctl` replaces that with a **controlled, reproducible, contract-driven system**.
