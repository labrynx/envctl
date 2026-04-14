# Release playbook

This document defines how releases should be structured across commits, changelog entries, and GitHub release notes.

The goal is to ensure that every release tells one coherent story at three levels of detail:

- commits: what changed in concrete terms
- changelog: what changed in technical terms
- release notes: why it matters

---

## 1. Start with one release theme

Before writing commits, changelog entries, or release notes, define the release theme in one sentence.

Examples:
- Deterministic environments and CLI boundary cleanup
- Contract composition and scope-aware inspection
- Vault encryption and safer projection behavior

A release should ideally have one main theme and at most two supporting themes.

---

## 2. Group commits by narrative block

Commits should reflect the release story, not just the file list.

Preferred pattern:
- build(...): dependency, tooling, workflow, packaging
- ci(...): workflow and automation changes
- refactor(...): architectural cleanup without public behavior change
- perf(...): startup, execution, or import-surface improvements
- docs(...): documentation alignment
- test(...): test-only updates

Example:
- build(env): adopt uv as canonical workflow
- ci: align workflows with locked uv environments
- refactor(cli): enforce service-layer boundaries
- perf(cli): reduce startup import surface
- docs: align contributor workflow with uv

---

## 3. Changelog structure

Changelog entries should be concise, factual, and grouped by impact.

Preferred sections:
- Added
- Changed
- Improved
- Fixed
- Deprecated
- Removed
- Docs
- Security

Rules:
- do not narrate everything twice
- avoid listing every file-level detail
- group related items under one meaningful heading
- make the release legible in under one minute

---

## 4. Semver decision rule

Use this rule before tagging:

- patch: internal cleanup, tooling, fixes, no public behavior change
- minor: new capability, meaningful workflow expansion, non-breaking behavior change
- major: breaking change in public behavior, compatibility, or contract

If the main effect is on contributors, CI, architecture, or reproducibility — but not on end-user behavior — prefer patch unless the contributor contract changes in a breaking way.

---

## 5. Final consistency check

Before publishing a release, verify:

- commit groups match the release theme
- changelog reflects the same structure as the commits
- release notes explain the same story in higher-level language
- semver matches the actual impact
- contributor-facing workflow changes are documented clearly

If these layers do not tell the same story, the release is not ready.

---

## 6. Automated release notes

GitHub release notes are generated automatically from the changelog.

Process:

1. Extract version section from `CHANGELOG.md`
2. Derive highlights from:
   - Added
   - Changed
   - Improved
3. Prepend highlights
4. Append full changelog section

Rules:

- CHANGELOG is the single source of truth
- Do not edit GitHub releases manually
- If highlights are poor, fix the changelog instead
