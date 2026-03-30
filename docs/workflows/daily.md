# Daily Workflow

This is the most common usage pattern.

## Run your app

```bash
envctl run -- <command>
```

## Change a value

```bash
envctl set KEY VALUE
```

## Inspect current state

```bash
envctl inspect
```

## Debug one variable

```bash
envctl explain KEY
```

## Switch environment

```bash
envctl --profile dev run -- app
```

## Summary

* use `run` for execution
* use `set` for local changes
* use `inspect` to understand
