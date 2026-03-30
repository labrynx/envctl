# CI Workflow

CI should be read-only.

## Validate environment

```bash
envctl check
```

## Important rules

* no mutation
* no secrets generated
* explicit failures

## Optional

Use profile:

```bash
ENVCTL_PROFILE=ci envctl check
```
