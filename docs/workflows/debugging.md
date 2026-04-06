# Debugging Workflow

When something fails, the easiest way to recover is to move from the broad picture to the specific detail.

`envctl` gives you commands for both.

## Step 1: get the overview

```bash
envctl status
```

Start here when you want to know whether the project is generally ready or whether something obvious is missing.

## Step 2: validate

```bash
envctl check
```

This tells you whether the resolved environment satisfies the contract.

If `check` fails, you know the problem is real at the contract level, not just a vague runtime symptom.

If `run`, `sync`, or `export` fail first, those commands now show the blocked projection keys directly, but `check` is still the best full pass/fail overview.

If `check`, `status`, or even the global CLI callback fail before resolution, `envctl` now also surfaces structured diagnostics for common setup problems such as:

* invalid contracts
* invalid config files or runtime mode settings
* corrupted vault state
* ambiguous or broken project binding

## Step 3: inspect the resolved state

```bash
envctl inspect
```

Now look at the resolved runtime view.

This helps answer questions like:

* which values are actually being used?
* is a default being applied?
* is a value missing from the active profile?
* did one placeholder reference make the value invalid?

## Step 4: inspect one key

```bash
envctl inspect KEY
```

Once the problem narrows down to one variable, `inspect KEY` is usually the fastest way to understand it.

That is especially useful after a projection failure points at one invalid or expanded key.

`envctl explain KEY` still works for now, but it is deprecated in favor of `envctl inspect KEY` and is scheduled for removal in v2.6.0.`

## Step 5: inspect stored vault values

```bash
envctl vault show
```

Use this when you need to see the physical stored values in the current profile file.

This is lower-level than `inspect`, so it helps when the question is not “what is the runtime result?” but “what is actually stored on disk?”

## Common expansion pitfall

`envctl` expands `${VAR}` references only for variables declared in the contract.

That means a value like:

```text
CACHE_DIR=${HOME}/.cache/demo
```

is invalid unless `HOME` is also a declared contract key.

This is intentional. It prevents placeholder expansion from silently depending on whatever host variables happen to exist in the current machine or shell session.

If you want to use a variable in `${VAR}` form, declare it in the contract first.

## Structured error hints

When `envctl` can classify a failure, the CLI now prints a short summary, concrete facts such as `path`, `field`, `key`, or `project_id`, and compact next steps.

That means you can usually tell apart:

* contract authoring problems
* config file problems
* persisted state corruption
* repository discovery or binding problems
* projection validation failures

## Rule of thumb

A good mental shortcut is:

* `check` → short validation and next actions
* `inspect` → full resolved state and context
* `inspect KEY` → one variable in detail
* `vault show` → stored values

If you keep that distinction in mind, debugging gets much easier.
