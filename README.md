# envctl

**Your `.env.local` files drift between machines, hide missing variables, and break when you least expect it. envctl fixes that.**

[![CI](https://github.com/labrynx/envctl/actions/workflows/ci.yml/badge.svg)](https://github.com/labrynx/envctl/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/labrynx/envctl/blob/main/LICENSE)

---

## What is envctl?

`envctl` is a local-first environment control tool.

It makes environment variables explicit, validated, and predictable — without introducing a cloud dependency.

Instead of relying on ad-hoc `.env` files, envctl separates three concerns:

- **contract** → what the project requires (`.envctl.yaml`)
- **vault** → your local values, stored outside git
- **runtime** → the validated environment your app actually runs with

That gives you:

- documented variables
- no secrets in git
- consistent environments across machines
- validation before execution

---

## Quickstart

```bash
envctl config init
envctl init
envctl fill
envctl check
envctl run -- python app.py
```

What this does:

- `config init` → sets up your local envctl config
- `init` → connects the repository to envctl
- `fill` → asks only for missing values
- `check` → validates the environment
- `run` → executes your command with a clean, resolved environment

---

## Why not just `.env.local`?

Because it does not scale cleanly.

|                                | `.env.local` | direnv       | Doppler / Infisical | **envctl** |
| ------------------------------ | ------------ | ------------ | ------------------- | ---------- |
| Documents variables            | ❌            | ❌            | Partial             | ✅          |
| Validates values               | ❌            | ❌            | ❌                   | ✅          |
| Keeps secrets out of git       | ⚠️           | ✅            | ✅ cloud             | ✅ local    |
| Supports multiple environments | manual files | manual files | ✅                   | ✅ profiles |
| Works without cloud            | ✅            | ✅            | ❌                   | ✅          |

`envctl` is **not a cloud secrets manager**.

It is a way to make environment handling explicit, predictable, and local-first.

---

## A typical workflow

```bash
# add a new requirement
envctl add API_KEY sk-example
git add .envctl.yaml
git commit -m "require API_KEY"

# another developer
envctl check
envctl fill
envctl run -- python app.py
```

The contract is shared in git.  
The values stay local.  
The runtime environment is rebuilt consistently when needed.

---

## Core concepts

- **contract** → defines variables and constraints
- **vault** → stores local values
- **profile** → selects a value set (`local`, `dev`, `staging`, ...)
- **resolution** → builds the final environment
- **projection** → applies it (`run`, `sync`, `export`)

Think of it like this:

> the repository defines the rules, your machine provides the values, and envctl builds the environment you actually run.

---

## Common commands

```bash
envctl check
envctl inspect
envctl inspect DATABASE_URL

envctl run -- <command>
envctl export
envctl sync

envctl profile list
envctl profile create staging
```

---

## When envctl is a good fit

envctl is a strong fit if:

- `.env.local` files drift between machines
- onboarding is fragile
- CI and local environments behave differently
- you work with multiple environments
- you want a local-first workflow without a hosted service

---

## When envctl is not the right tool

envctl may be unnecessary if:

- you only have one static `.env` file
- the project is very small
- you already rely fully on a centralized secrets platform

---

## Security

- the contract contains no secrets
- values stay on your machine
- sensitive values are masked in output
- optional encryption at rest is available

> envctl assumes a trusted machine.  
> If your machine is compromised, your secrets are compromised too.

---

## Documentation

- [Quickstart](docs/getting-started/quickstart.md)
- [Mental model](docs/getting-started/mental-model.md)
- [Commands reference](docs/reference/commands.md)
- [Profiles](docs/reference/profiles.md)
- [Vault](docs/reference/vault.md)
- [Security](docs/reference/security.md)
- [Migration and compatibility](docs/internals/compatibility.md)
