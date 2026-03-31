# Team Workflow

`envctl` is built around a simple collaboration rule:

> the contract is shared, but values stay local

That split is what makes team workflows clearer.

## Add a variable

If the project itself now needs a new variable, add it to the contract:

```bash
envctl add API_KEY
git add .envctl.schema.yaml
git commit
```

This is a shared change. It affects the repository and may affect other developers, so it should be reviewed like any other project change.

## What other developers do

Other developers do not need your actual value. They only need to satisfy the updated contract on their own machines.

Typically that means:

```bash
envctl fill
```

That will ask only for the missing required value in their active profile.

## After pulling contract changes

A common update flow is:

```bash
envctl check
envctl fill
```

First validate, then provide any missing values.

## Key idea

The rule behind the whole workflow is:

* contract is shared
* values are local

That keeps the project requirements visible without pushing secrets into the repository.
