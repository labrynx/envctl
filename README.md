# envctl

**Your `.env.local` files are undocumented, unvalidated, and drift between machines. envctl fixes that.**

[![CI](https://github.com/labrynx/envctl/actions/workflows/ci.yml/badge.svg)](https://github.com/labrynx/envctl/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/labrynx/envctl/blob/main/LICENSE)

---

## What is this?

Most projects handle `.env` files like this:

* variables are not documented
* values get copied between machines
* something works locally… but breaks somewhere else

`envctl` gives you a simple structure to fix that.

It separates three things that usually get mixed together:

* **what the project needs** → defined in `.envctl.schema.yaml` (committed to the repo)
* **what you have locally** → stored in a private vault (never in git)
* **what actually runs** → a validated environment, built on demand

So you get:

* no secrets in git
* no undocumented variables
* no copy-pasting `.env` files

---

## Install

```bash
pip install envctl
```

Or from source:

```bash
git clone https://github.com/labrynx/envctl
cd envctl
pip install -e .
```

---

## Quickstart

```bash
envctl config init      # create your local config
envctl init             # initialize this repository
envctl fill             # set missing values (interactive)
envctl check            # validate against the contract
envctl run -- python app.py  # run with env injected
```

If you use `envctl run -- docker run ...`, `envctl` injects into the Docker client process, not directly into the container. Forward container variables explicitly with `-e`, `--env`, or `--env-file`.

---

## Why not just `.env.local`?

Because it doesn’t scale well.

|                                | `.env.local`    | direnv       | Doppler / Infisical | **envctl**                 |
| ------------------------------ | --------------- | ------------ | ------------------- | -------------------------- |
| Documents what variables exist | ❌               | ❌            | Partial             | ✅ contract                 |
| Type validation                | ❌               | ❌            | ❌                   | ✅                          |
| Values stay off git            | ⚠️ easy to slip | ✅            | ✅ cloud             | ✅ local vault              |
| Multiple environments          | manual files    | manual files | ✅                   | ✅ profiles                 |
| No cloud account required      | ✅               | ✅            | ❌                   | ✅                          |
| Works in CI without mutation   | ❌               | ❌            | ❌                   | ✅ `ENVCTL_RUNTIME_MODE=ci` |

`envctl` is not a secrets manager.

It’s a **local control plane** for your project’s environment:

> the contract says what’s needed, your machine provides values, and envctl makes them work together.

---

## How it works

There are five pieces, but the idea is simple:

* **contract** → defines what variables exist and their rules
* **vault** → stores your real values locally
* **profile** → selects a set of values (`local`, `dev`, `staging`, …)
* **resolution** → combines everything in a deterministic way
* **projection** → makes it usable (`run`, `sync`, `export`)

Think of it like this:

> the repo defines the rules, your machine provides the data, and envctl builds the final environment.

Resolution now includes placeholder expansion as part of the runtime model, so `check`, `inspect`,
`run`, `sync`, and `export` all see the same final value.

Contracts can also attach an optional human-facing `group` label to variables for organization,
filtering, and dotenv section rendering. `group` is not a namespace, is not hierarchical, and does
not change resolution or dependency semantics.

---

### Example contract

```yaml
# .envctl.schema.yaml — commit this
version: 1
variables:
  DATABASE_URL:
    type: url
    required: true
    sensitive: true
    description: Primary database connection URL
  PORT:
    type: int
    required: true
    default: 3000
    sensitive: false
  DEBUG:
    type: bool
    required: false
    default: false
    sensitive: false
  TEST_JSON:
    type: string
    format: json
    required: false
    sensitive: false
  APP_URL:
    type: string
    required: true
    sensitive: false
    group: Application
    default: http://${APP_NAME}:${PORT}
```

This file describes what exists.
It never contains real values.

---

## Variable expansion

`envctl` supports explicit placeholder expansion with `${VAR}` during resolution.

That means the expansion happens before projection, so the effective expanded value is what:

* `inspect` shows
* `check` validates
* `run` injects
* `sync` writes
* `export` prints

Example:

```dotenv
INFRA_NEO4J_USER=neo4j
INFRA_NEO4J_PASSWORD=super-secret
INFRA_NEO4J_AUTH=${INFRA_NEO4J_USER}/${INFRA_NEO4J_PASSWORD}
```

`INFRA_NEO4J_AUTH` resolves to the final runtime value, not the literal expression.

Rules:

* only `${VAR}` is supported in v1
* `$VAR` stays literal
* if `VAR` is a declared envctl key, envctl resolves that key first
* otherwise envctl falls back to the current process environment
* `${HOME}` works when `HOME` exists in the current process environment
* malformed placeholders or unresolved references make resolution invalid

Compatibility notes:

* before this feature, `${HOME}` stayed literal
* now `${HOME}` is expanded during resolution
* `${...}` literal escaping is not supported in v1

## Optional groups

Each contract variable may define an optional `group` label:

```yaml
variables:
  DATABASE_URL:
    type: url
    required: true
    sensitive: true
    group: Database
```

`group` is used only for:

* organization in the contract
* CLI targeting with `--group`
* grouped dotenv output from `sync` and `export --format dotenv`

It does not:

* create namespaces
* affect `${VAR}` expansion rules
* restrict cross-variable references
* imply hierarchy, inheritance, or prefix matching

---

## Profiles

Instead of juggling multiple `.env` files:

```bash
# set up dev once
envctl --profile dev fill

# validate staging
envctl --profile staging check

# run with staging values
envctl --profile staging run -- python app.py
```

Profile selection priority:

1. `--profile`
2. `ENVCTL_PROFILE`
3. config default
4. `local`

Each profile is independent. No hidden inheritance.

---

## Team workflow

The idea is simple:

* the **contract is shared**
* the **values are local**

```bash
# developer A
envctl add API_KEY sk-abc123
git add .envctl.schema.yaml
git commit -m "require API_KEY"

# developer B
git pull
envctl check   # shows what's missing
envctl fill    # only asks for missing values
```

No more guessing what goes into `.env`.

---

## CI workflow

```bash
ENVCTL_RUNTIME_MODE=ci envctl check
```

In CI mode:

* validation works
* mutations are blocked (`add`, `set`, `fill`, etc.)

You can also combine it with profiles:

```bash
ENVCTL_PROFILE=ci ENVCTL_RUNTIME_MODE=ci envctl check
```

---

## Common commands

```bash
# validation and visibility
envctl check
envctl inspect
envctl explain DATABASE_URL
envctl status
envctl doctor

# values
envctl add DATABASE_URL <value>
envctl add TEST_JSON '{"key":"value"}' --type string --format json
envctl set PORT 4000
envctl unset PORT
envctl remove PORT

# run / output
envctl run -- <command>
envctl sync
envctl export

# profiles
envctl profile list
envctl profile create staging
envctl profile copy local staging
envctl profile remove staging --yes

# vault
envctl vault show
envctl vault check
envctl vault path
envctl vault prune

# project identity
envctl project bind <id>
envctl project rebind
envctl project repair
```

---

## Machine-readable output

All read commands support `--json`:

```bash
envctl --json check
envctl --json status
envctl --json inspect
envctl --json doctor
```

---

## Structured string validation

If a variable is a string but carries structured content, declare that semantic format in the contract:

```yaml
variables:
  TEST_JSON:
    type: string
    format: json
```

Supported `format` values for `type: string`:

* `json`
* `url`
* `csv`

When `format` is declared, `check`, `inspect`, and runtime resolution validate payload semantics, not only raw string presence.

---

## Design principles

* Contract-first: the repo defines requirements
* Deterministic: same inputs → same result
* Explicit: nothing happens automatically
* Local-first: no required cloud
* Generated files are disposable
* Profiles are value namespaces, not variants
* CI mode is policy, not a profile

---

## Security model

* The contract contains **no secrets**
* Secrets stay on your machine
* `.env.local` is optional and disposable
* Sensitive values are masked in output
* Read-only commands never change state
* Vault files use restrictive permissions (`0600`)

Important:

> envctl assumes a trusted machine.
> If your machine is compromised, your secrets are compromised.

It’s not a replacement for a team-wide secrets manager.

---

## Documentation

* [Quickstart](https://github.com/labrynx/envctl/blob/main/docs/getting-started/quickstart.md)
* [Mental model](https://github.com/labrynx/envctl/blob/main/docs/getting-started/mental-model.md)
* [Commands reference](https://github.com/labrynx/envctl/blob/main/docs/reference/commands.md)
* [Profiles reference](https://github.com/labrynx/envctl/blob/main/docs/reference/profiles.md)
* [CI workflow](https://github.com/labrynx/envctl/blob/main/docs/workflows/ci.md)
* [Team workflow](https://github.com/labrynx/envctl/blob/main/docs/workflows/team.md)
* [Security](https://github.com/labrynx/envctl/blob/main/docs/reference/security.md)
* [Internal architecture](https://github.com/labrynx/envctl/blob/main/docs/internals/architecture.md)
