# envctl

**Your `.env.local` files are undocumented, unvalidated, and drift between machines. envctl fixes that.**

[![CI](https://github.com/alessbarb/envctl/actions/workflows/ci.yml/badge.svg)](https://github.com/alessbarb/envctl/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

`envctl` separates three things that most workflows conflate:

- **what the project needs** → a contract in `.envctl.schema.yaml`, committed to the repo
- **what you have locally** → values in a private vault, outside version control
- **what actually runs** → a validated, resolved environment, injected on demand

No secrets in git. No undocumented variables. No copy-pasting `.env` files between machines.

---

## Install

```bash
pip install envctl
```

Or from source:

```bash
git clone https://github.com/alessbarb/envctl
cd envctl
pip install -e .
```

---

## Quickstart

```bash
envctl config init      # create your local user config
envctl init             # initialize this repository
envctl fill             # interactively set missing required values
envctl check            # validate your environment against the contract
envctl run -- python app.py  # run with environment injected
```

---

## Why not just `.env.local`?

| | `.env.local` | direnv | Doppler / Infisical | **envctl** |
|---|---|---|---|---|
| Documents what variables exist | ❌ | ❌ | Partial | ✅ contract |
| Type validation | ❌ | ❌ | ❌ | ✅ |
| Values stay off git | ⚠️ easy to slip | ✅ | ✅ cloud | ✅ local vault |
| Multiple environments | manual files | manual files | ✅ | ✅ profiles |
| No cloud account required | ✅ | ✅ | ❌ | ✅ |
| Works in CI without mutation | ❌ | ❌ | ❌ | ✅ `ENVCTL_RUNTIME_MODE=ci` |

`envctl` is not a secrets manager. It is a local control plane for the environment contract your project declares. Think of it as the layer between "this project needs these variables" and "here is how I run it today."

---

## How it works

`envctl` has five parts:

- **contract** → `.envctl.schema.yaml` declares which variables exist, their types, and which are required. Committed to the repo. Contains no secrets.
- **vault** → your machine-local store for real values, kept outside the repository
- **profile** → one value namespace (`local`, `dev`, `staging`, …) within the vault
- **resolution** → combines system env, active profile values, and contract defaults deterministically
- **projection** → makes the resolved environment usable (`run`, `sync`, `export`)

The contract defines what exists. The vault stores what you have. The profile selects which values to use. The resolver decides what runs.

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
```

Values live in your local vault — never in this file.

---

## Profiles

Work with multiple environments locally without managing multiple files:

```bash
# set up dev values once
envctl --profile dev fill

# check what staging would look like
envctl --profile staging check

# run against staging values
envctl --profile staging run -- python app.py
```

Profile selection precedence:

1. `--profile` flag
2. `ENVCTL_PROFILE` environment variable
3. `default_profile` in config
4. `local` (default)

Profiles are independent value namespaces. They share the same contract. There is no hidden inheritance between profiles.

---

## Team workflow

The contract is shared. Values are local.

```bash
# developer A: add a new variable
envctl add API_KEY sk-abc123
git add .envctl.schema.yaml
git commit -m "require API_KEY"

# developer B: pull and fill
git pull
envctl check   # → shows API_KEY is missing
envctl fill    # → prompts for API_KEY only
```

---

## CI workflow

```bash
# validate only — no mutation allowed
ENVCTL_RUNTIME_MODE=ci envctl check

# or with a ci profile
ENVCTL_PROFILE=ci ENVCTL_RUNTIME_MODE=ci envctl check
```

In `ci` runtime mode, all mutation commands (`add`, `set`, `fill`, `sync`, etc.) are blocked. Read-only commands work normally.

---

## Common commands

```bash
# validation and visibility
envctl check                        # validate against contract
envctl inspect                      # show resolved values (sensitive masked)
envctl explain DATABASE_URL         # trace where a value comes from
envctl status                       # project readiness summary
envctl doctor                       # local environment diagnostics

# value management
envctl add DATABASE_URL <value>     # add to contract + active profile
envctl set PORT 4000                # update active profile value only
envctl unset PORT                   # remove from active profile only
envctl remove PORT                  # remove from contract + all profiles

# projection
envctl run -- <command>             # inject environment into subprocess
envctl sync                         # write .env.local as generated artifact
envctl export                       # emit shell export lines

# profiles
envctl profile list
envctl profile create staging
envctl profile copy local staging
envctl profile remove staging --yes

# vault inspection
envctl vault show
envctl vault check
envctl vault path
envctl vault prune                  # remove keys not in contract

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

```json
{
  "ok": true,
  "command": "check",
  "data": {
    "active_profile": "local",
    "report": {
      "is_valid": true,
      "missing_required": [],
      "values": { "DATABASE_URL": { "source": "vault", "masked": true, ... } }
    }
  }
}
```

---

## Design principles

- Contract-first: the repo declares requirements; machines provide values
- Deterministic resolution: same inputs always produce the same environment
- Explicit over implicit: nothing happens without a command
- Local-first: no required cloud dependency
- Generated files are artifacts, not sources of truth
- Profiles are value namespaces, not contract variants
- CI mode is policy, not a profile

---

## Security model

- The contract contains **no secrets** — it is safe to commit
- Secrets never leave your machine unless you explicitly project them
- `.env.local` is optional and disposable — regenerate it any time
- Sensitive values are masked in all normal output
- Read-only commands never mutate state
- Local vault files are stored with `0600` permissions by default

Important: `envctl` is a local tool. It assumes a trusted machine. If your account or machine is compromised, your local vault is compromised. envctl is not a replacement for a team secrets manager when shared access control is required.

---

## Documentation

- [Quickstart](docs/getting-started/quickstart.md)
- [Mental model](docs/getting-started/mental-model.md)
- [Commands reference](docs/reference/commands.md)
- [Profiles reference](docs/reference/profiles.md)
- [CI workflow](docs/workflows/ci.md)
- [Team workflow](docs/workflows/team.md)
- [Security](docs/reference/security.md)
- [Internal architecture](docs/internals/architecture.md)
