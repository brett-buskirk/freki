# Contributing

- **No direct commits to `main`** — branch → PR (`gh pr create`) → green checks → merge. **Stop at
  the PR and let Brett merge** — don't self-merge unless told. One command per PR.
- **AgentGate runs on every PR** — `secrets` + `dangerous_patterns` block; `scope` is advisory.
- Commits are signed & Verified; never commit secrets (`.env`, keys are gitignored).

## Working on the script

`freki` is a single Bash script. Keep it dependency-light: `bash`, `git`, `gh`, `jq` only.

- **Syntax-check before pushing:** `bash -n freki`.
- **Run `shellcheck`** if you have it: `shellcheck freki`.
- Colors go through the `$R/$G/$Y/…` vars (empty when non-TTY / `NO_COLOR`) — don't hardcode escapes.
- Each subcommand is a `cmd_<name>` function with a matching `help_<name>`; wire new ones into the
  `case` dispatcher and the `cmd_help` menu.
- Paths: `$HERE` = where the tool lives (and its bundled `templates/`); `$ROOT` = the estate it
  manages (`$FREKI_ROOT`); `$CONV` = the conventions source, shared with huginn. Resolve conventions
  files with `first_of "$CONV/<file>" "$HERE/templates/<file>"` so commands fall back to the bundled
  defaults.
- **Every mutating action routes through the safety spine** (`would`/`confirm`/`do_it`/
  `log_action`) — see `freki` itself and the Safety section of the README. No command may delete
  anything without going through `do_it`, and `do_it` must never run without a command's own
  `--apply` flag having been explicitly set.
