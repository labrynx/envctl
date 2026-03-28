# Commands

## envctl config init

Creates the default envctl config file in the user's XDG config directory.

- creates `~/.config/envctl/config.json`
- refuses to overwrite an existing config file
- writes readable default values
- keeps configuration creation explicit

## envctl init [PROJECT]

Registers the current Git repository in the vault, creates a unique project directory for it, creates the managed environment file, and creates the repository symlink when safe.

- `[PROJECT]` is optional
- if omitted, the repository directory name is used as the readable slug
- the vault directory is unique even when multiple repositories share the same visible name

## envctl repair

Validates and repairs the repository `.env.local` symlink using existing local envctl metadata.

- does not create a new vault project
- does not modify repository metadata
- will prompt before replacing a regular file
- supports `--yes` / `-y` to skip confirmation prompts

## envctl unlink

Removes the repository-managed symlink if present.

- if no managed symlink exists, no action is taken
- existing regular files are left untouched
- does not modify the vault or repository metadata

## envctl status

Shows the current repository envctl state in a human-friendly format.

- reports whether the repository is healthy, broken, not initialized, or missing its managed vault file
- explains the current repository and vault env state
- suggests the next command when action is needed

## envctl set KEY VALUE

Creates or updates a key/value pair in the managed vault env file for the current initialized repository.

- requires valid local envctl metadata
- requires the managed vault env file to already exist
- does not create missing repository or vault structure automatically
- does not print the stored value

## envctl doctor

Runs read-only diagnostics for the local envctl environment.

- checks configuration loading
- checks the resolved vault path
- checks vault path permissions when the vault exists
- checks Git repository detection from the current working directory
- checks whether symlink creation works on the current system

The command uses a checklist-style output with `OK`, `WARN`, and `FAIL` states.

## envctl help [COMMAND]

Shows help for envctl or for a specific command.

- `envctl help` shows the root help
- `envctl help init` shows help for `init`
- this is a convenience alias for Typer's built-in help output

## envctl remove

Removes envctl management for the current repository.

- prompts before destructive changes
- supports `--yes` / `-y` to skip confirmation prompts
- restores a real repository `.env.local` file from the managed vault file when the current symlink is valid
- removes repository metadata
- removes the managed vault env file
- removes the managed vault project directory when it becomes empty
- never deletes or overwrites a regular repository `.env.local` file
