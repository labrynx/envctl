![envctl](docs/assets/envctl_banner.png)

**Your `.env.local` works… until it doesn’t.**

It drifts between machines.  
It misses variables.  
It breaks when you least expect it.

envctl fixes that — and makes your environment boring again (which is exactly what you want).

**envctl makes your environment behave.**

---

<div align="center">
  
[![Tests](https://github.com/labrynx/envctl/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/labrynx/envctl/actions/workflows/ci-tests.yml)
[![Coverage](https://github.com/labrynx/envctl/actions/workflows/ci-coverage.yml/badge.svg)](https://github.com/labrynx/envctl/actions/workflows/ci-coverage.yml)

[![PyPI version](https://img.shields.io/pypi/v/envctl.svg)](https://pypi.org/project/envctl/)
[![Python versions](https://img.shields.io/pypi/pyversions/envctl.svg)](https://pypi.org/project/envctl/)
[![License](https://img.shields.io/pypi/l/envctl.svg)](https://github.com/labrynx/envctl/blob/main/LICENSE)

[![Code style: ruff](https://img.shields.io/badge/style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/types-mypy-blue.svg)](https://mypy-lang.org/)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://bandit.readthedocs.io/)
[![Imports: import-linter](https://img.shields.io/badge/imports-linter-purple.svg)](https://github.com/seddonym/import-linter)

[![Release](https://github.com/labrynx/envctl/actions/workflows/release.yml/badge.svg)](https://github.com/labrynx/envctl/actions/workflows/release.yml)

</div>

---

## What is this?

Fair.

`envctl` is a local-first environment control tool.

It takes your environment from:

> “I think this should work…”

to:

> “I know exactly what’s going on.”

No cloud. No magic. No hidden state.  
Just something you can reason about.

---

## The problem (you’ve probably seen this)

- It works on your machine… but not on your teammate’s  
- CI fails because a variable is missing (again)  
- You forgot to update `.env.local` somewhere  
- Someone committed something they shouldn’t  
- Nobody actually knows what variables are required  

And somehow… it still “kind of works”

Until it doesn’t.

---

## What envctl does differently

Instead of a loose `.env` file, envctl splits things properly:

- **contract** → what the project expects (`.envctl.yaml`)  
- **vault** → your local values (never in git)  
- **runtime** → the environment your app actually runs with  

So:

- the repo defines the rules  
- your machine provides the values  
- envctl builds the environment  

No guessing.

---

## Quickstart

From zero to running in seconds:

```bash
envctl config init
envctl init
envctl fill
envctl check
envctl run -- python app.py
````

What’s happening here:

* `config init` → sets up envctl locally
* `init` → links your repo to envctl
* `fill` → asks only for what’s missing
* `check` → validates everything before you run
* `run` → executes with a clean, resolved environment

---

## “But `.env.local` works for me”

Yeah — it does.

Until:

* you switch machines
* someone joins the project
* you add a new variable
* something silently goes missing

Here’s the difference:

|                                | `.env.local` | direnv       | Doppler / Infisical | **envctl** |
| ------------------------------ | ------------ | ------------ | ------------------- | ---------- |
| Documents variables            | ❌            | ❌            | Partial             | ✅          |
| Validates values               | ❌            | ❌            | ❌                   | ✅          |
| Keeps secrets out of git       | ⚠️           | ✅            | ✅ cloud             | ✅ local    |
| Supports multiple environments | manual files | manual files | ✅                   | ✅ profiles |
| Works without cloud            | ✅            | ✅            | ❌                   | ✅          |

`envctl` is not a secrets manager.

It’s the missing layer between your repo and your runtime.

---

## A typical workflow

Here’s what this actually looks like:

```bash
# add a new requirement
envctl add API_KEY sk-example
git add .envctl.yaml
git commit -m "require API_KEY"

# someone else pulls
envctl check
envctl fill
envctl run -- python app.py
```

That’s it. No tricks.

The contract lives in git.
The values stay on your machine.
The environment rebuilds itself when needed.

---

## Core concepts

* **contract** → variables and constraints
* **vault** → your local values
* **profile** → environments (`local`, `dev`, `staging`, …)
* **resolution** → builds the final environment
* **projection** → applies it (`run`, `sync`, `export`)

---

## Debugging (when things go weird)

```bash
ENVCTL_LOG_LEVEL=DEBUG envctl check
ENVCTL_LOG_LEVEL=DEBUG envctl inspect DATABASE_URL
ENVCTL_LOG_LEVEL=DEBUG envctl run -- python app.py
```

Values stay masked. You see what matters.

---

## When envctl is a good fit

* your `.env.local` keeps drifting
* onboarding is fragile
* CI behaves differently
* you have multiple environments
* you want to stay local-first

---

## When it’s probably overkill

* you have one static `.env` file
* the project is tiny
* everything already lives in a cloud secrets manager

---

## Security

* no secrets in the contract
* values stay on your machine
* sensitive output is masked
* optional encryption at rest

> envctl assumes your machine is trusted.
> If it isn’t — nothing will save you anyway.

---

## Documentation

* [Quickstart](docs/getting-started/quickstart.md)
* [Mental model](docs/getting-started/mental-model.md)
* [Commands reference](docs/reference/commands.md)
* [Profiles](docs/reference/profiles.md)
* [Vault](docs/reference/vault.md)
* [Security](docs/reference/security.md)
* [Migration and compatibility](docs/internals/compatibility.md)

---

If you've ever said
“it works on my machine”

…you’ll probably like envctl.
