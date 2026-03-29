# envctl

`envctl` is a local environment control plane.

Instead of committing `.env.local` files or managing symlinks, `envctl` defines
a **contract-first workflow**:

 * The repository declares *what it needs*  
 * The developer provides *values locally*  
 * `envctl` resolves and injects the environment safely

---

## Mental model

Think of `envctl` as:

- a **schema** → `.envctl.schema.yaml`
- a **local vault** → your private values
- a **resolver** → merges everything deterministically

No secrets in the repo. No duplication. No guessing.

---

## Core commands

### Validate the contract

```bash
envctl check
````

* Ensures all required variables are defined
* Fails if something is missing

---

### Fill missing values (interactive)

```bash
envctl fill
```

* Prompts for missing variables
* Stores values in your local vault
* Never writes secrets to the repo

---

### Inspect resolved environment

```bash
envctl inspect
```

* Shows final resolved values
* Masks sensitive ones

Example:

```text
APP_NAME=demo
PORT=3000
DATABASE_URL=********
```

---

### Explain a value

```bash
envctl explain DATABASE_URL
```

Shows where a value comes from:

* default
* user input
* contract
* etc.

---

### Run a command with injected env

```bash
envctl run -- python app.py
```

* Injects environment in memory
* Does NOT create `.env.local`

---

### Generate `.env.local` (optional)

```bash
envctl sync
```

* Creates `.env.local`
* Treated as a generated artifact
* Safe to delete anytime

---

### Export for shell usage

```bash
envctl export
```

Example:

```bash
export APP_NAME=demo
export PORT=3000
```

Useful for:

```bash
eval "$(envctl export)"
```

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
    description: Application name

  PORT:
    type: int
    required: true
    default: 3000

  DATABASE_URL:
    type: url
    required: true
    sensitive: true
```

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

### First time in a repo

```bash
envctl init
envctl fill
envctl check
```

---

### Daily usage

```bash
envctl run -- <command>
```

---

### After pulling changes

```bash
envctl check
envctl fill
```

---

### When debugging

```bash
envctl inspect
envctl explain KEY
```

---

## Security model

* Secrets never leave your machine
* `.env.local` is optional and disposable
* Contract contains **no secrets**
* Sensitive values are masked in output

---

## Design principles

* Contract-first
* Deterministic resolution
* No hidden state
* Explicit over implicit
* Local-first, no cloud dependency

---

## Roadmap (short)

* Better contract validation
* Type constraints and patterns
* CI integration (read-only checks)
* Plugin system

---

## Why not `.env` files?

Because:

* They get duplicated
* They get out of sync
* They leak secrets

`envctl` replaces them with a **controlled, reproducible system**.
