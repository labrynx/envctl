![envctl](docs/assets/envctl_banner.png)

**Your `.env.local` works... until it doesn't.**

Different machines behave differently.<br>
Onboarding breaks.<br>
CI fails in ways you can't reproduce.

`envctl` stops that drift.

`envctl` keeps environments consistent.

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

## What `envctl` does

`envctl` keeps environments consistent.

It gives you:

* shared requirements in the repo
* local values outside Git
* explicit runtime behavior instead of guesswork

It is not a secret manager.
It is not a dotenv loader.
It is not a shell trick.

It is a local-first way to stop `.env` drift across development, teammates, and CI.

---

## The problem

You have probably seen some version of this already:

* it works on your machine, but not on your teammate's
* CI fails because a variable is missing or shaped differently
* onboarding depends on tribal knowledge
* `.env.local` gets copied around until nobody trusts it
* nobody can clearly say which variables are actually required

That is not just a secret-storage problem.

It is an environment-consistency problem.

---

## How `envctl` fixes it

`envctl` makes environments explicit instead of implicit.

It separates the environment into clear responsibilities:

* **contract**: what the project requires
* **vault**: what each machine stores locally
* **profiles**: which local value set is active
* **resolution**: what is actually true at runtime
* **projection**: how that resolved environment is handed to tools

That means:

* the repo defines shared requirements
* each machine keeps real values local
* the runtime environment is explicit and checkable

> No hidden source of truth.<br>
> No guessing which value won.

---

## Quickstart

Install the CLI:

```bash
python3 -m pip install envctl
```

Then the shortest useful flow is:

```bash
envctl config init
envctl init
envctl fill
envctl check
envctl run -- python app.py
```

What happens:

* `config init` creates your user-level `envctl` config
* `init` prepares the repository for `envctl` and attempts to install managed Git hooks
* `fill` asks only for missing required values
* `check` validates the resolved environment
* `run` executes with the resolved environment injected directly

If another tool really needs a file on disk, use `sync`.
Otherwise, `run` is usually the cleanest path.

## Local Git protection

`envctl` can keep its own secret guard wired into Git without becoming a generic hooks manager.

The managed workflow is:

```bash
envctl hooks status
envctl hooks install
envctl hooks repair
envctl hooks remove
```

Those commands manage only `envctl`'s own `pre-commit` and `pre-push` wrappers, both of which run `envctl guard secrets`.

---

## Why it is different

`envctl` is not mainly competing with cloud secret tools or dotenv loaders.

Its primary job is different:

* cloud secret tools focus on secret distribution
* dotenv loaders and shell tooling focus on injection
* `envctl` focuses on environment coherence

That is why the core value is not “where do secrets live?”.

The core value is:

* what does this project require?
* what does this machine actually have?
* what environment will the app really receive?

---

## A typical workflow

```bash
# add a new shared requirement
envctl add API_KEY sk-example
git add .envctl.yaml
git commit -m "require API_KEY"

# another developer pulls
envctl check
envctl fill
envctl run -- python app.py
```

The contract changes in Git.
Real values stay local.
The runtime environment stays explicit.

---

## When `envctl` is a good fit

* your `.env.local` keeps drifting
* onboarding is fragile
* local and CI behavior diverge too easily
* one machine needs multiple local contexts
* you want a local-first workflow without turning generated files into the source of truth

## When it is probably overkill

* you have one tiny project with a static env file
* onboarding is trivial and unlikely to change
* the team already solves environment consistency elsewhere and does not need another layer

---

## Security

* no secrets in the contract
* local values stay on the machine
* sensitive output is masked
* encryption at rest is optional
* managed Git hooks can run `guard secrets` automatically before commit and push

`envctl` assumes the local machine is trusted. It is designed to keep environment handling explicit and safer, not to replace a full remote secrets platform.

---

## Documentation

* [Docs home](docs/index.md)
* [Getting started](docs/getting-started/index.md)
* [Quickstart](docs/getting-started/quickstart.md)
* [Concepts](docs/concepts/index.md)
* [Commands reference](docs/reference/commands/index.md)
* [Configuration reference](docs/reference/configuration.md)
* [Observability reference](docs/reference/observability.md)
* [Distribution reference](docs/reference/distribution.md)
* [Troubleshooting](docs/troubleshooting/index.md)
* [Compatibility](docs/internals/compatibility.md)

---

## Development

The supported contributor baseline is:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e ".[dev]"
make validate
```

That is the canonical local workflow for this repository today.

`uv.lock` is tracked to document one tested dependency resolution state and to support optional local workflows, but it is not yet the canonical CI input. Until that policy changes explicitly, local validation and CI should be expected to work from the editable `pip install -e ".[dev]"` path first.

If you are editing documentation locally, install docs extras as well:

```bash
pip install -e ".[dev,docs]"
make docs-check
```

The normal contributor validation path should include architecture checks, not only lint and tests:

```bash
make validate
```

That flow runs linting, formatting checks, type-checking, Bandit, tests with coverage, and `lint-imports`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the detailed contributor workflow.

---

If you have ever said:

> "it works on my machine"

then `envctl` is probably solving a problem you already have.
