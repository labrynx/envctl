# Vault Reference

The vault stores local values.

## Structure

```text
vault/
  projects/<slug>--<id>/
    values.env
    profiles/
```

## Commands

### check

```bash
envctl vault check
```

* exists
* parseable
* permissions

### show

```bash
envctl vault show
```

* masked values

### show raw

```bash
envctl vault show --raw
```

* requires confirmation

### edit

```bash
envctl vault edit
```

* opens editor

### path

```bash
envctl vault path
```

### prune

```bash
envctl vault prune
```

* removes unknown keys
