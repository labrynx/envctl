# Resolution

Resolution is how `envctl` answers the question:

> “What values does the application actually receive?”

That is the point where the contract, the active profile, and any process environment overrides come together.

If the contract describes what should exist, and the vault stores what is available locally, resolution is the step that decides what finally counts at runtime.

## Resolution pipeline

Resolution happens in a small pipeline:

```text
selection
-> expansion
-> validation
```

That high-level model breaks down like this:

```text
selection
-> placeholder parsing/tokenization
-> placeholder resolution
-> rendering
-> validation
```

## Selection order

The effective order is:

```text
process environment
-> active profile values
-> contract defaults
```

In other words, the environment already present in the current process takes priority. If a value is not provided there, `envctl` looks at the active profile. If it is still missing, it can fall back to a non-sensitive default from the contract.

## Expansion

After selection, `envctl` expands supported placeholders inside the selected raw values.

In v1, the only supported placeholder form is:

```text
${VAR}
```

That means:

* `${VAR}` is expanded
* `$VAR` stays literal
* malformed placeholders make resolution invalid

When `envctl` resolves `${VAR}`:

* if `VAR` is a declared envctl key, that key is resolved first
* otherwise `envctl` falls back to the current process environment
* if neither source provides a value, resolution becomes invalid

Optional contract `group` labels do not change this behavior. A targeted command such as
`envctl --group Application export --format dotenv` may still resolve `${VAR}` references to
variables declared in other groups. Group selection affects which variables are targeted for the
command output, not how references are resolved.

`${HOME}` is not a special built-in rule. It works because `HOME` usually exists in the current
process environment.

## Inputs

Resolution uses:

* contract
* active profile
* local values
* optional process environment

These are the pieces that decide the final runtime view.

## Output

The result of resolution is a resolved environment:

* variables have been evaluated
* supported placeholders have been expanded
* missing values have been identified
* validation has been applied

This is the state that commands like `run`, `sync`, and `inspect` work from.

## Validation

Resolution also validates what it finds.

That includes checks such as:

* required variables
* placeholder syntax and reference validity
* type correctness
* declared string formats (`json`, `url`, `csv`)
* allowed values
* patterns

So resolution is not only about combining sources. It is also about confirming that the result makes sense under the contract.

## Commands that use resolution

These commands rely on the resolution step:

* `check`
* `inspect`
* `explain`
* `run`
* `sync`
* `export`

Each of them uses the resolved state in a different way, but they all depend on the same underlying model.

## Missing values

If required values are missing:

* `check` fails
* `run` fails
* `fill` can help resolve the problem interactively

That behavior is deliberate. `envctl` does not silently invent values just to make a command pass.

## Why explicit resolution matters

When resolution rules are clear, debugging gets easier.

You do not have to wonder whether a profile inherited something invisibly, or whether a generated file quietly changed what the app sees. You can trace the result back through a small, visible set of inputs.

That makes the system easier to trust and easier to explain.

## See also

* [Projection](projection.md)
