# Commands Reference

This section describes exact command behavior.

For usage examples, see workflows.
For concepts, see concepts section.

---

## Global options

- `--version`, `-V`
- `--profile`, `-p`
- `--json`

---

## Core model

Commands are grouped by responsibility:

### Contract mutation

- `add`
- `remove`

### Value mutation

- `set`
- `unset`
- `fill`

### Resolution

- `check`
- `inspect`
- `explain`

### Projection

- `run`
- `sync`
- `export`

### Identity

- `project bind`
- `project unbind`
- `project rebind`
- `project repair`

### Profiles

- `profile ...`

### Vault

- `vault ...`

---

## add

```bash
envctl add KEY VALUE
```

* updates contract
* stores value in active profile
* infers metadata

---

## set

```bash
envctl set KEY VALUE
```

* updates value only
* does not modify contract

---

## unset

```bash
envctl unset KEY
```

* removes value from active profile
* keeps contract

---

## remove

```bash
envctl remove KEY
```

* removes contract definition
* removes value from all profiles

---

## fill

```bash
envctl fill
```

* prompts for missing required values
* uses contract metadata

---

## check

```bash
envctl check
```

* validates resolved environment
* exits non-zero on failure

---

## inspect

```bash
envctl inspect
```

* shows resolved state
* masks sensitive values

---

## explain

```bash
envctl explain KEY
```

* explains resolution path

---

## run

```bash
envctl run -- command
```

* injects environment in memory

---

## sync

```bash
envctl sync
```

* writes `.env.local`

---

## export

```bash
envctl export
```

* prints shell exports

---

## status

```bash
envctl status
```

* shows readiness summary

---

## doctor

```bash
envctl doctor
```

* runs diagnostics

---

## profile commands

```bash
envctl profile list
envctl profile create NAME
envctl profile copy SRC DST
envctl profile remove NAME
envctl profile path [NAME]
```

---

## vault commands

```bash
envctl vault check
envctl vault show
envctl vault path
envctl vault edit
envctl vault prune
```

---

## project commands

```bash
envctl project bind ID
envctl project unbind
envctl project rebind
envctl project repair
```
