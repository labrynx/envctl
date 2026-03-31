# Quickstart

This is the fastest way to get productive with `envctl`.

It skips most of the deeper theory on purpose. The goal here is simple: get one repository working with the minimum number of steps.

If you want the bigger picture afterwards, read [Mental model](mental-model.md).

## 1. Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## 2. Initialize your local config

```bash
envctl config init
```

This creates your user-level config file.

A typical location is:

```text
~/.config/envctl/config.json
```

That config tells `envctl` how to behave on your machine. It does not store project secrets and it does not replace the project contract.

## 3. Initialize the repository

```bash
envctl init
```

This prepares the repository for contract-based workflows and establishes local state when needed.

If the repository has never been used with `envctl` before, this is the step that gets the local structure into a sensible starting state.

## 4. Fill missing values

```bash
envctl fill
```

This asks only for required variables that are missing from the active profile.

By default, the active profile is `local` unless you select another one.

## 5. Validate everything

```bash
envctl check
```

This validates the resolved environment against the contract.

If the contract is satisfied, you are ready to run the project with confidence. If not, `check` shows what still needs attention.

## 6. Run your application

```bash
envctl run -- python app.py
```

This injects the resolved values into the subprocess environment without needing `.env.local`.

For many workflows, that is the cleanest way to use `envctl`.

## Optional: work with a different profile

```bash
envctl --profile dev fill
envctl --profile dev check
envctl --profile dev run -- python app.py
```

This is useful when one machine needs more than one local setup.

## Optional: create `.env.local`

```bash
envctl sync
```

Use this only when another tool really needs an env file on disk.

The file is generated output. It is not the main source of truth.

## What to read next

* [First project](first-project.md)
* [Mental model](mental-model.md)
* [Commands reference](../reference/commands.md)
