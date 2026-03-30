# First Project

This guide explains the normal first-run flow in a repository.

It is slightly more detailed than the quickstart and is meant for real onboarding.

## Goal

Prepare one repository so you can validate, inspect, and run it with `envctl`.

## Step 1: create local config

```bash
envctl config init
```

This creates your personal config file.

The config controls local tool behavior.
It does not define the project contract and it does not store secrets.

## Step 2: initialize the repository

```bash
envctl init
```

`init` is the main bootstrap command.

It may:

* prepare local vault structure
* establish binding and persisted state
* create or normalize contract metadata
* infer a starter contract from `.env.example` when supported

Important:

* `init` does **not** invent secrets
* `init` does **not** automatically write `.env.local`
* `init` is safe to run repeatedly

## Step 3: inspect the current state

```bash
envctl status
```

This gives you a workflow-oriented summary of what is ready and what is missing.

## Step 4: provide missing required values

```bash
envctl fill
```

This prompts only for values required by the contract and missing from the active profile.

## Step 5: validate

```bash
envctl check
```

This confirms that the resolved environment satisfies the contract.

## Step 6: run the project

```bash
envctl run -- <command>
```

Examples:

```bash
envctl run -- python app.py
envctl run -- npm start
envctl run -- make dev
```

## Working with profiles from day one

If you already know you want a second local setup, create an explicit profile:

```bash
envctl profile create dev
envctl --profile dev fill
envctl --profile dev check
envctl --profile dev run -- python app.py
```

## Common follow-up tasks

### Add a new variable

```bash
envctl add REDIS_URL redis://localhost:6379
```

### Change only your local value

```bash
envctl set PORT 4000
```

### Debug one key

```bash
envctl explain DATABASE_URL
```

### Inspect physical stored values

```bash
envctl vault show
```

## What to read next

* [Mental model](mental-model.md)
* [Contract](../concepts/contract.md)
* [Profiles](../concepts/profiles.md)
* [Daily workflow](../workflows/daily.md)
