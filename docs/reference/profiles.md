# Profiles Reference

Profiles are local value namespaces.

## Commands

### list

```bash
envctl profile list
```

### create

```bash
envctl profile create dev
```

### copy

```bash
envctl profile copy dev staging
```

### remove

```bash
envctl profile remove staging
```

### path

```bash
envctl profile path dev
```

---

## Rules

* profiles do not change contract
* profiles do not inherit
* profiles are local only
