# Debugging Workflow

When something fails:

## Step 1: overview

```bash
envctl status
```

## Step 2: validation

```bash
envctl check
```

## Step 3: inspect

```bash
envctl inspect
```

## Step 4: explain

```bash
envctl explain KEY
```

## Step 5: raw vault

```bash
envctl vault show
```

## Rule of thumb

* `inspect` → resolved state
* `vault show` → stored values
