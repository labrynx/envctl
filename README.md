# envctl

`envctl` is a local environment control plane.

Instead of committing `.env.local` files, duplicating secrets across machines, or relying on symlink-based workflows, `envctl` follows a **contract-first model**:

- the repository declares **what it needs**
- each developer stores **values locally**
- `envctl` **resolves, validates, and projects** the environment safely

No secrets in the repository. No hidden coupling. No guessing.

---

## Quickstart

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

## Mental model

Think of `envctl` as five explicit parts:

* a **contract** → `.envctl.schema.yaml`
* a **local vault** → your private machine-local values
* a **profile** → one local value namespace such as `local`, `dev`, or `staging`
* a **resolver** → combines values deterministically
* a **projection layer** → injects or materializes the environment when needed

That separation matters:

* the **contract** defines what exists
* the **vault** stores what is currently set
* the **profile** selects one local value set
* the **resolved environment** is what the application actually sees
* generated files such as `.env.local` are **artifacts**, not the source of truth

---

## Profiles

`envctl` supports profile-aware local workflows.

Examples:

* `local`
* `dev`
* `staging`
* `ci`

The implicit `local` profile keeps using the legacy vault file:

```text
<vault-project-dir>/values.env
```

Explicit profiles use:

```text
<vault-project-dir>/profiles/<profile>.env
```

Profile selection precedence:

1. `--profile`
2. `ENVCTL_PROFILE`
3. `default_profile` from config
4. `local`

Profiles change only local stored values.
They do not change contract schema.

There is no hidden inheritance between profiles.

---

## Runtime mode

`envctl` also supports a separate runtime mode concept.

Examples:

* `runtime_mode = "local"` → normal local workflow
* `runtime_mode = "ci"` → stricter command policy, usually read-only

This is intentionally separate from profile selection.

* a runtime mode is policy
* a profile is a value namespace

---

## Common commands

### Validate the contract

```bash
envctl check
envctl --profile staging check
```

### Fill missing values

```bash
envctl fill
envctl --profile dev fill
```

### Inspect resolved environment

```bash
envctl inspect
envctl --profile staging inspect
```

### Run a command with injected environment

```bash
envctl run -- python app.py
envctl --profile staging run -- python app.py
```

### Add a variable

```bash
envctl add DATABASE_URL postgres://user:pass@localhost:5432/app
envctl --profile staging add APP_NAME demo-staging
```

### Set a value

```bash
envctl set PORT 4000
envctl --profile dev set PORT 4000
```

### Remove a variable entirely

```bash
envctl remove PORT
```

### Manage profiles

```bash
envctl profile list
envctl profile create dev
envctl profile copy dev staging
envctl profile remove staging --yes
```

### Inspect the vault

```bash
envctl vault check
envctl vault show
envctl vault edit --profile staging
```

---

## Documentation

Start here:

* [Documentation index](docs/index.md)
* [Quickstart](docs/getting-started/quickstart.md)
* [Mental model](docs/getting-started/mental-model.md)
* [Commands reference](docs/reference/commands.md)
* [Internal architecture](docs/internals/architecture.md)

---

## Design principles

* Contract-first
* Deterministic resolution
* Explicit over implicit
* No hidden state
* Local-first, no required cloud dependency
* Generated files are artifacts, not sources of truth
* Profiles are value namespaces, not contract variants

---

## Security model

* Secrets never leave your machine unless you explicitly project them
* `.env.local` is optional and disposable
* The contract contains **no secrets**
* Sensitive values are masked in normal output
* Read-only commands do not silently mutate state
* Local storage is kept outside repositories
* Profiles are explicit namespaces, not security boundaries

Important limitation:

`envctl` assumes a trusted local machine. If the machine or account is compromised, your secrets are compromised.
