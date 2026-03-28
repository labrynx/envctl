# Configuration

`envctl` uses an XDG config path and a home-based vault path.

## Default config path

```text
~/.config/envctl/config.json
````

## Default vault path

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
  "vault_dir": "~/.envctl/vault",
  "env_filename": ".env.local"
}
```

## Supported keys

* `vault_dir`: absolute path or `~`-based path to the vault root
* `env_filename`: repository env filename, default `.env.local`
