# Resolution

Resolution determines the effective environment state.

It answers:

> what values does the application actually receive?

## Resolution order

```text
process environment
-> active profile values
-> contract defaults
```

## Inputs

Resolution uses:

* contract
* active profile
* local values
* optional process environment

## Output

A resolved environment:

* all variables evaluated
* missing values identified
* validation applied

## Validation

Resolution validates:

* required variables
* type correctness
* allowed values
* patterns

## Commands using resolution

* `check`
* `inspect`
* `explain`
* `run`
* `sync`
* `export`

## Missing values

If required values are missing:

* `check` fails
* `run` fails
* `fill` can resolve interactively

## Why explicit resolution matters

* no hidden fallback logic
* deterministic behavior
* easier debugging

## See also

* [Projection](projection.md)
