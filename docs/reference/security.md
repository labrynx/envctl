# Security Reference

`envctl` is designed to make local environment handling clearer and safer. It is not a remote secrets platform and it does not try to hide its trust assumptions.

## Core assumption

`envctl` assumes a single-user trusted machine.

If the local account or host is compromised, local secrets should be treated as compromised too.

## Security rules of the model

The main safety properties come from the product model itself:

* contracts describe requirements, not secret values
* local values stay outside repositories
* profiles stay explicit
* projection is explicit
* generated files are artifacts, not the source of truth

That separation reduces accidental leaks and hidden state.

## Contract safety

The contract is versioned with the repository, so it must stay safe to share.

Allowed:

* variable declarations
* descriptions
* validation rules
* non-sensitive defaults
* sensitivity flags

Not allowed:

* real secret values
* machine-specific local state
* profile-specific secret payloads

## Local storage safety

The local provider stores values outside repositories and applies restrictive permissions on a best-effort basis.

Typical protections include:

* private local paths
* restrictive file and directory modes where supported
* explicit mutation through commands rather than hidden writes

Binding is also local and stored in local Git config for the current checkout.

## Encryption at rest

Vault encryption is optional.

When enabled:

* vault files are encrypted at rest
* the encryption layer is transparent to normal commands
* the master key lives in local storage

See [Encryption Reference](encryption.md) for the operational details and migration workflow.

## Projection safety

Projection is explicit on purpose:

* `run` keeps the handoff in memory
* `sync` creates a plaintext generated artifact
* `export` prints resolved values to stdout

Important: `sync` output is **not** encrypted automatically. Encryption protects vault files, not generated projection artifacts.

## Local Git protection

`envctl` can also protect against accidental commits and pushes of envctl-specific secret material through managed Git hooks.

That protection is intentionally narrow:

* it only manages envctl-owned `pre-commit` and `pre-push` wrappers
* both wrappers run `envctl guard secrets`
* it does not act as a general secret scanner or hook-merging framework

Important limits still apply:

* `git commit --no-verify` bypasses hooks
* CI enforcement must be configured separately
* external shared hooks paths are outside envctl's management perimeter

## Distribution safety

Published release artifacts are treated as build outputs that should be verifiable, not just downloadable.

Current release hardening includes:

* tagged releases build source and wheel artifacts in CI
* release artifacts are smoke-tested before publication
* a `SHA256SUMS` manifest is generated for published artifacts and release metadata
* a CycloneDX SBOM is generated for the built wheel
* GitHub provenance attestations are generated for release artifacts

That does not replace provenance or attestation, but it does give downstream users one concrete integrity check for released files.

See [Distribution Reference](distribution.md) for the operational release-artifact policy.

## What `envctl` does not try to do

`envctl` does not provide:

* remote access control
* OS keyring integration by default
* profile-based isolation guarantees
* protection against a compromised local machine

That is outside its intended scope.

## User responsibilities

Users still need to:

* keep secrets out of the contract
* protect their local machine
* avoid committing generated env artifacts
* back up the master key if encryption is enabled

## Related pages

* [Contract](../concepts/contract.md)
* [Vault reference](vault.md)
* [Encryption reference](encryption.md)
* [Hooks command reference](commands/hooks.md)
