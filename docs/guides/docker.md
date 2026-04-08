# Docker

## Problem

Your app runs in a container, but `envctl` resolves the environment on the host side first.

That creates a common mistake:

> assuming that `envctl run -- docker run ...` automatically gives the container the full resolved environment

It does not.

!!! warning "`envctl run -- docker run ...` is not automatic container injection"
    `envctl` can inject variables into the Docker client process, but the container still needs an explicit interface such as `--env-file` or explicit `-e` forwarding.

## Goal

Run a container with an `envctl`-resolved environment without depending on hidden host inheritance.

## Steps

Validate the selected environment first:

```bash
envctl check
```

Then hand the resolved environment to Docker explicitly:

```bash
docker run --env-file <(envctl export --format dotenv) my-image
```

If you need a committed-looking local artifact for another tool, generate a dotenv file explicitly instead:

```bash
envctl sync --output-path /tmp/app.env
docker run --env-file /tmp/app.env my-image
```

Use `run` for non-container commands where direct subprocess injection is enough:

```bash
envctl run -- pytest
```

## Result

You get a container that receives the resolved environment through an explicit interface that Docker actually understands.

That means:

* the container runtime is predictable
* the handoff is visible
* you avoid assuming that host-side injection automatically becomes container-side state

## Why this works

`envctl` resolves and validates the environment first, but Docker still needs an explicit handoff mechanism.

This is a projection problem, not a resolution problem.

* [Projection](../concepts/projection.md)
* [run](../reference/commands/run.md)
* [export](../reference/commands/export.md)
* [sync](../reference/commands/sync.md)
