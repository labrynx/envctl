# First Project

This guide walks through the normal first-run flow in a repository.

It is a little more detailed than the quickstart and is meant for real onboarding. If you have just cloned a project and want to get from “nothing is set up” to “I can validate and run this”, this is the guide to follow.

## Goal

Prepare one repository so you can validate, inspect, and run it with `envctl`.

## Step 1: create your local config

```bash
envctl config init
```

This creates your personal config file.

That config controls local tool behavior, such as where the vault lives and which profile is used by default. It does **not** define the project contract, and it does **not** store secrets.

## Step 2: initialize the repository

```bash
envctl init
```

`init` is the main bootstrap command.

Depending on the repository and the current local state, it may:

* prepare local vault structure
* establish binding and persisted state
* create or normalize contract metadata
* infer a starter contract from `.env.example` when supported

A few things are worth calling out here:

* `init` does **not** invent secrets
* `init` does **not** automatically write `.env.local`
* `init` is safe to run repeatedly

So think of `init` as “prepare this repository for `envctl`”, not as “magically make everything ready with guessed values”.

## Step 3: inspect where you are

```bash
envctl status
```

At this point, it helps to ask: what is already ready, and what is still missing?

`status` gives you that overview. It is meant to answer the practical question, “What should I do next?”

## Step 4: provide missing required values

```bash
envctl fill
```

This prompts only for values that are required by the contract and missing from the active profile.

That means you are not asked for everything under the sun. You are only asked for what the project actually needs and what your current local setup does not yet provide.

## Step 5: validate

```bash
envctl check
```

This confirms that the resolved environment satisfies the contract.

If something is missing or invalid, `check` will tell you. If everything looks good, you know the project has the values it expects.

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

This runs the command with the resolved environment injected directly into the subprocess. In many cases, that means you do not need a `.env.local` file at all.

## Working with profiles from day one

If you already know you want a second local setup, create an explicit profile early.

For example:

```bash
envctl profile create dev
envctl --profile dev fill
envctl --profile dev check
envctl --profile dev run -- python app.py
```

This is useful when you want one setup for normal local work and another one for testing something closer to staging.

## Common follow-up tasks

### Add a new variable

```bash
envctl add REDIS_URL redis://localhost:6379
```

Use this when the project itself now requires a new variable.

### Change only your local value

```bash
envctl set PORT 4000
```

Use this when the contract stays the same, but you want a different value in your current profile.

### Debug one key

```bash
envctl explain DATABASE_URL
```

Use this when a single variable is confusing or behaving differently than expected.

### Inspect physical stored values

```bash
envctl vault show
```

Use this when you want to look at the current profile’s stored vault data rather than the resolved runtime view.

## What to read next

* [Mental model](mental-model.md)
* [Contract](../concepts/contract.md)
* [Profiles](../concepts/profiles.md)
* [Daily workflow](../workflows/daily.md)
