# Team Workflow

This describes collaboration scenarios.

## Add a variable

```bash
envctl add API_KEY
git add .envctl.schema.yaml
git commit
```

## Other developers

```bash
envctl fill
```

## After pulling changes

```bash
envctl check
envctl fill
```

## Key idea

* contract is shared
* values are local
