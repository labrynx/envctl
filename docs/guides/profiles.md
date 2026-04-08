# Profiles

## Problem

One machine often needs more than one local setup for the same project.

Without profiles, people tend to copy dotenv files around or manually overwrite values until they lose track of what changed.

## Goal

Keep multiple local contexts cleanly without changing the shared project contract.

## Steps

Create an explicit profile:

```bash
envctl profile create dev
```

Fill the missing values for that profile:

```bash
envctl --profile dev fill
```

Validate it:

```bash
envctl --profile dev check
```

Run the app with it:

```bash
envctl --profile dev run -- python app.py
```

## Result

You get a second local environment context without:

* changing the contract
* duplicating fragile project files
* mixing one setup into another accidentally

## Why this works

Profiles change local stored values, not shared project requirements.

They are the right tool when the contract stays the same but your local execution context changes.

* [Profiles](../concepts/profiles.md)
* [Resolution](../concepts/resolution.md)
* [profile](../reference/commands/profile.md)
