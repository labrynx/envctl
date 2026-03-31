# Debugging Workflow

When something fails, the easiest way to recover is to move from the broad picture to the specific detail.

`envctl` gives you commands for both.

## Step 1: get the overview

```bash
envctl status
```

Start here when you want to know whether the project is generally ready or whether something obvious is missing.

## Step 2: validate

```bash
envctl check
```

This tells you whether the resolved environment satisfies the contract.

If `check` fails, you know the problem is real at the contract level, not just a vague runtime symptom.

## Step 3: inspect the resolved state

```bash
envctl inspect
```

Now look at the resolved runtime view.

This helps answer questions like:

* which values are actually being used?
* is a default being applied?
* is a value missing from the active profile?

## Step 4: explain one key

```bash
envctl explain KEY
```

Once the problem narrows down to one variable, `explain` is usually the fastest way to understand it.

## Step 5: inspect stored vault values

```bash
envctl vault show
```

Use this when you need to see the physical stored values in the current profile file.

This is lower-level than `inspect`, so it helps when the question is not “what is the runtime result?” but “what is actually stored on disk?”

## Rule of thumb

A good mental shortcut is:

* `inspect` → resolved state
* `vault show` → stored values

If you keep that distinction in mind, debugging gets much easier.
