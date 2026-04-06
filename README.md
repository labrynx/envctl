# envctl

**Your `.env.local` files drift between machines, hide missing variables, and break when you least expect it. envctl fixes that.**

[![CI](https://github.com/labrynx/envctl/actions/workflows/ci.yml/badge.svg)](https://github.com/labrynx/envctl/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](https://github.com/labrynx/envctl/blob/main/LICENSE)

---

## Why this exists

Most projects handle environment variables in a messy way:

- `.env.local` files are undocumented
- values get copied between machines
- something works locally until it suddenly does not
- CI and local setups behave differently
- nobody is fully sure which variables are required

It works — until it breaks.

`envctl` brings structure to this without turning environment setup into a second project.

---

## What is envctl?

`envctl` is a local-first environment control plane built around a **contract-first model**.

It separates three things that usually get mixed together:

- **what the project needs** → defined in the repository contract, discovered as `.envctl.yaml` first and `.envctl.schema.yaml` as legacy fallback
- **what you have locally** → stored in a private local vault, outside git
- **what actually runs** → a validated environment resolved when needed

That gives you:

- clear, documented variables
- no secrets in git
- fewer setup mistakes
- more predictable local and team workflows
- explicit validation before execution

---

## Install

```bash
pip install envctl
````

Or from source:

```bash
git clone https://github.com/labrynx/envctl
cd envctl
pip install -e .
```

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

* `config init` creates your local envctl config
* `init` connects the current repository to envctl
* `fill` asks only for missing values
* `check` validates the environment before you run anything
* `run` injects a clean resolved environment into the child process

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

`envctl` is **not** a cloud secrets manager.

It is a way to make environment handling explicit, predictable, and local-first.

> your repository defines what is needed, your machine provides the values, and envctl resolves the final environment.

---

## A typical workflow

```bash
# one developer adds a new requirement
envctl add API_KEY sk-example
git add .envctl.yaml  # or .envctl.schema.yaml if the repo still uses the legacy root
git commit -m "require API_KEY"

# another developer pulls the change
envctl check
envctl fill
envctl run -- python app.py
```

The contract is shared in git.
The values stay local.
The runtime environment is rebuilt consistently when needed.

---

## How it works

### Root contract discovery

`envctl` looks for the main repository contract at the repo root in this order:

1. `.envctl.yaml`
2. `.envctl.schema.yaml`

If both exist, `envctl` uses `.envctl.yaml` and warns that `.envctl.schema.yaml` is now treated as a legacy root contract. For migration examples, prefer `.envctl.yaml`, but older repositories may still commit `.envctl.schema.yaml` until they switch.

The root contract may import other contract files. The final result is still one composed contract with one global variable namespace, one vault per project, and no implicit override between imported files.


At a high level:

* **contract** → defines which variables exist and how they should look
* **vault** → stores the real local values
* **profile** → selects which local value set to use (`local`, `dev`, `staging`, ...)
* **resolution** → builds the final validated environment
* **projection** → applies it through `run`, `sync`, or `export`

Think of it like this:

> the repository defines the rules, your machine provides the values, and envctl builds the environment you actually run.

---

## Contract scopes

By default, envctl works against the full contract. You can also target a narrower scope when you only want to validate, inspect, export, sync, or run part of it:

```bash
envctl check
envctl --group Application check
envctl --set docker_runtime check
envctl --var DATABASE_URL inspect
```

Scope selectors are mutually exclusive: `--group`, `--set`, and `--var` cannot be used together.

Variables now use `groups` as an array. Legacy `group` is still accepted for compatibility, but it is deprecated and normalized internally. Legacy `required` is also accepted, but ignored functionally.

A named set can combine three things:

- other sets
- one or more groups
- explicit variables

That lets you define reusable slices of the contract without forcing authors to maintain a meaningful order in the YAML file. envctl normalizes ordering internally so output stays stable and reproducible.

## Profiles

Instead of juggling multiple `.env` files:

```bash
envctl --profile dev fill
envctl --profile staging check
envctl --profile staging run -- python app.py
```

Each profile is explicit and independent.
No hidden inheritance, no magic fallback between profiles.

---

## Docker note

```bash
envctl run -- docker run ...
```

`envctl` injects variables into the **Docker client process**.

To pass them into the container, you still need one of these:

* `-e`
* `--env`
* `--env-file`

A common pattern is:

```bash
docker run --env-file <(envctl export --format dotenv) ...
```

---

## CI mode

```bash
ENVCTL_RUNTIME_MODE=ci envctl check
```

In CI:

* validation still works
* mutating commands are blocked

That keeps automation predictable and avoids accidental local-style writes in CI environments.

---

## Common commands

```bash
envctl check
envctl inspect
envctl inspect DATABASE_URL
envctl inspect --contracts
envctl inspect --sets
envctl inspect --set docker_runtime
envctl inspect --groups
envctl inspect --group Runtime
envctl status

envctl add DATABASE_URL <value>
envctl set PORT 4000
envctl unset PORT

envctl run -- <command>
envctl sync
envctl export

envctl profile list
envctl profile create staging

envctl vault check
envctl vault show
envctl vault encrypt
envctl vault decrypt
```

For diagnosis, the main path is now:

- `envctl check` for a short pass/fail view
- `envctl inspect` for the full report, including contract composition
- `envctl inspect KEY` for one variable in depth
- `envctl inspect --contracts` for the resolved contract graph
- `envctl inspect --sets` or `--set NAME` for global set views
- `envctl inspect --groups` or `--group NAME` for global group views

`envctl doctor` and `envctl explain KEY` still work for compatibility, but they are deprecated aliases.

---

## When envctl is a good fit

envctl is a strong fit if:

* `.env.local` files drift between machines
* onboarding is fragile
* CI and local environments do not behave the same way
* you work with multiple environments
* you want a local-first workflow without depending on a hosted service

---

## When envctl is not the right tool

envctl may be unnecessary if:

* you only have one static `.env` file
* the project is very small and has no real setup complexity
* you already rely fully on a centralized secrets platform and do not want local-first handling

---

## Security model

* the contract contains **no secrets**
* secrets stay on your machine
* sensitive values are masked in normal output
* vault files use restrictive permissions
* optional encryption at rest is available for vault files

### Vault encryption at rest

If you enable encryption, envctl stores vault files in an encrypted, self-identifying format instead of plaintext.

Enable it in your config:

```json
{
  "encryption": {
    "enabled": true
  }
}
```

Then migrate existing vault files once:

```bash
envctl vault encrypt
```

This creates a local key file at:

```text
~/.envctl/vault/master.key
```

That key is stored with restrictive permissions.

After encryption is enabled:

* `vault edit` works transparently
* `vault check` reports whether the file is plaintext, encrypted, using the wrong key, or corrupted
* decrypt failures are explicit instead of looking like generic parse errors

To migrate back to plaintext:

```bash
envctl vault decrypt
```

Then disable encryption in config.

### Important limitation

Encryption at rest helps protect vault files on disk.

It does **not** protect against a fully compromised machine or a compromised user session.

> envctl assumes a trusted machine.
> If your machine is compromised, your secrets are compromised too.

Back up your `master.key` carefully.
If you lose it, encrypted vault data cannot be recovered.

---

## Documentation

* [Quickstart](https://github.com/labrynx/envctl/blob/main/docs/getting-started/quickstart.md)
* [Mental model](https://github.com/labrynx/envctl/blob/main/docs/getting-started/mental-model.md)
* [Commands reference](https://github.com/labrynx/envctl/blob/main/docs/reference/commands.md)
* [Profiles reference](https://github.com/labrynx/envctl/blob/main/docs/reference/profiles.md)
* [Vault reference](https://github.com/labrynx/envctl/blob/main/docs/reference/vault.md)
* [Encryption reference](https://github.com/labrynx/envctl/blob/main/docs/reference/encryption.md)
* [Config reference](https://github.com/labrynx/envctl/blob/main/docs/reference/config.md)
* [CI workflow](https://github.com/labrynx/envctl/blob/main/docs/workflows/ci.md)
* [Team workflow](https://github.com/labrynx/envctl/blob/main/docs/workflows/team.md)
* [Security](https://github.com/labrynx/envctl/blob/main/docs/reference/security.md)
* [Internal architecture](https://github.com/labrynx/envctl/blob/main/docs/internals/architecture.md)
