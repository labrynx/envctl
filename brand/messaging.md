# envctl messaging

## Canonical sentence

`envctl` keeps environments consistent by separating what the project requires from what each machine stores, and by making runtime resolution explicit.

## Enemy

The main enemy is invisible `.env` drift:

* different machines
* fragile onboarding
* CI behaving differently
* nobody knowing what is actually required

## Positioning guardrails

### Primary framing

`envctl` stops `.env` drift.

It makes environments consistent.

### Secondary contrasts

* cloud secret tools solve secret distribution, not environment coherence
* dotenv loaders and shell tricks inject values, but do not model shared requirements cleanly

### Messages to prefer

* keeps environments consistent
* stops `.env` drift
* shared requirements, local values
* explicit runtime behavior
* local-first

### Messages to avoid

* tool to manage environment variables
* dotenv but better
* secret manager
* missing layer between repo and runtime

## 30 seconds

`envctl` stops `.env` drift.

It keeps environments consistent by separating shared project requirements from machine-local values, then making the final runtime environment explicit and checkable.

It is not a secret manager or a shell trick. It is a local-first system for keeping local dev, teammates, and CI aligned.

## 2 minutes

The problem `envctl` solves is not “how do I load env vars?”.

The problem is that `.env`-style setups drift.

One machine has values another one is missing. Onboarding is fragile. CI fails differently from local. Generated files become the accidental source of truth. And teams often do not even have a shared definition of what the app really requires.

`envctl` fixes that by separating three things that usually get blurred together:

* what the project requires
* what each machine stores locally
* what the app actually receives at runtime

That gives you:

* shared requirements in the repo
* local values outside Git
* deterministic runtime behavior
* explicit projection when a tool actually needs the environment

So `envctl` is not mainly competing with secret managers or dotenv loaders.

It is solving the consistency problem around environments.

## 1 page

`envctl` is a local-first environment system for teams whose `.env` workflows keep drifting.

The core problem is familiar:

* one developer has a working `.env.local`, another does not
* CI fails because a variable is missing or shaped differently
* onboarding depends on tribal knowledge
* generated env files become the real source of truth by accident
* nobody can clearly answer which variables are actually required

That is not just a secret-storage problem.

It is an environment-consistency problem.

`envctl` addresses it by splitting the environment into clear responsibilities.

First, the project defines shared requirements in the repository. That is the contract: which variables exist, what shape they should have, and what defaults or validation rules are shared.

Second, each machine stores its real values locally, outside Git.

Third, the final runtime environment is resolved explicitly instead of being guessed from a pile of files and shell state.

Finally, that resolved environment is projected in the shape a workflow actually needs: into a subprocess, into stdout, or into a generated file when a file is truly required.

This matters because it makes environments explainable.

Instead of asking “why does it work here but not there?”, teams can ask:

* what is required?
* what is missing locally?
* what value won?
* what did the app actually receive?

That is why `envctl` is different.

It is not a secret manager.
It does not try to be a cloud control plane.
It is not just a dotenv loader or shell trick.

It keeps environments consistent across local development, team workflows, and CI.
