# Configuration

`envctl` uses XDG-style defaults.

## Default config path

```text
~/.config/envctl/config.json
````

## Default data path

```text
~/.envctl/vault
```

## Supported config file format

v1 supports JSON only.

Planned for v1.1:

* YAML support
* config format detection by extension

Example:

```json
{
  "vault_dir": "/home/user/.local/share/envctl/vault",
  "env_filename": ".env.local"
}
```

## Supported keys

* `vault_dir`: absolute path to the vault root
* `env_filename`: repository env filename, default `.env.local`
