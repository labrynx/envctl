# envctl

`envctl` is a local-first CLI tool that centralizes `.env.local` files in a user-owned vault and links them back into repositories using symlinks.

It enforces a simple and explicit model:

- the repository declares what it needs
- the vault stores the secret values
- the link between both is explicit and local

No hidden behavior. No implicit state. No duplication.

---

## Why envctl

Managing `.env` files across multiple repositories is error-prone:

- secrets end up duplicated
- values drift between projects
- onboarding is inconsistent
- local setups become hard to trust

`envctl` solves this by separating structure, storage, and validation.

---

## Goals

- Keep secrets outside repositories
- Avoid duplicated `.env.local` files
- Use explicit, deterministic local-only workflows
- Fail safely when the filesystem is not in the expected state
- Make environment setup understandable and verifiable

## Non-goals

- No automatic syncing
- No hidden behavior
- No implicit environment creation
- No secret management beyond the local filesystem
- No default-value provisioning from project schemas

Everything is explicit and local.
