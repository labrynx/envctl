# CI Workflow

CI should be read-only.

That is the main idea behind using `envctl` in automation: CI should validate the environment, not quietly change it.

## Validate the environment

```bash
envctl check
```

This confirms whether the resolved environment satisfies the contract.

If required values are missing or invalid, CI should fail clearly and early.

## Important rules

In CI:

* no mutation
* no secret generation
* failures should stay explicit

The goal is to surface problems, not to patch them invisibly during a pipeline run.

## Optional: use a CI profile

If your workflow uses a dedicated profile, you can select it explicitly:

```bash
ENVCTL_PROFILE=ci envctl check
```

Remember that `profile = "ci"` and `runtime_mode = "ci"` are different ideas. One selects a local value set. The other controls command policy.
