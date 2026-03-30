# Quickstart

This guide is the fastest way to become productive with `envctl`.

It intentionally skips deeper theory.

If you want the underlying model, read [Mental model](mental-model.md).

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

This creates your user-level config file under the XDG config directory.

Typical location:

```text
~/.config/envctl/config.json
```

## 3. Initialize the repository

```bash
envctl init
```

This prepares the repository for contract-driven workflows and establishes local state when needed.

## 4. Fill missing values

```bash
envctl fill
```

This prompts only for missing required variables for the active profile.

By default, the active profile is `local` unless you select another one.

## 5. Validate everything

```bash
envctl check
```

This validates the resolved environment against the contract.

## 6. Run your application

```bash
envctl run -- python app.py
```

This injects resolved values into the subprocess environment without requiring `.env.local`.

## Optional: work with a different profile

```bash
envctl --profile dev fill
envctl --profile dev check
envctl --profile dev run -- python app.py
```

## Optional: materialize `.env.local`

```bash
envctl sync
```

Use this only when another tool really needs an env file on disk.

## What to read next

* [First project](first-project.md)
* [Mental model](mental-model.md)
* [Commands reference](../reference/commands.md)
