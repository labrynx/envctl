# Configuration Reference

## Location

```text
~/.config/envctl/config.json
```

## Example

```json
{
  "vault_dir": "~/.envctl/vault",
  "env_filename": ".env.local",
  "schema_filename": ".envctl.schema.yaml",
  "runtime_mode": "local",
  "default_profile": "local"
}
```

## Keys

### vault_dir

Local storage location.

### env_filename

Generated env file.

### schema_filename

Contract filename.

### runtime_mode

Execution policy.

Examples:

* `local`
* `ci`

### default_profile

Default active profile.

---

## Rules

Config does NOT:

* store secrets
* define contract
* define values
