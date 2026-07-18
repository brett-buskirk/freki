# freki cheat sheet

Quick reference for every command, option, and behavior. `freki` is the estate's **reaper** — it finds
and clears the cruft (merged/stale branches, abandoned PRs, old CI artifacts, stale draft/pre-releases)
across **every repo under `$FREKI_ROOT`** (default `~/github-repos`), derived live from `git`/`gh`, no
stored state.

**It is the one tool in the pack that deletes things — so it is dry-run by default.** Every acting
command lists exactly what it *would* remove and stops; **nothing is deleted until you pass `--apply`**,
and an `--apply` run still confirms once before it bites (skip that with `--yes`).

For the narrative version see the [README](README.md); for per-command detail in the terminal, run
`freki <command> help`.

---

## At a glance

| Command | Aliases | What it does | Options |
|---------|---------|--------------|---------|
| [`branches`](#branches) | `br` | Merged/stale branches across the estate (local + remote) | `--apply`, `--force`, `-y`/`--yes` |
| [`prs`](#prs) | | Open PRs, flagging the abandoned ones | `--apply`, `-y`/`--yes` |
| [`artifacts`](#artifacts) | `art` | Old CI workflow artifacts eating the storage quota | `--apply`, `-y`/`--yes` |
| [`releases`](#releases) | `rel` | Stale draft releases and old pre-releases | `--apply`, `-y`/`--yes` |
| [`reap`](#reap) | | The combined cruft summary across all four (**dry-run only**) | |
| [`help`](#help) | `-h`, `--help` | The command menu | |

- **Dry-run is the default, always.** `branches` `prs` `artifacts` `releases` each print what they
  *would* delete and exit without touching anything. **`--apply` is required to actually delete.**
- **`--apply` confirms once for the whole batch** before it does anything — pass `-y`/`--yes` to skip
  that prompt. The prompt reads `/dev/tty`, so a piped/scripted stdin can't silently auto-confirm.
- **`reap` never deletes** — it's a summary/dry-run headline only. You apply per-command.
- Running `freki` with no command is the same as `freki help`.

---

## Requirements & global behavior

- **Requires `bash` + `git` + `gh` (authenticated) + `jq`** — all four. Missing any is a hard error
  (`exit 1`); freki is `gh`-backed end to end, so there's no degraded local-only mode.
- **Estate-scoped.** freki operates on every top-level directory under `$FREKI_ROOT` that contains a
  `.git` — the same estate huginn manages. There is **no `[repo]` argument**; commands sweep the whole
  estate. (This is why exempting repos matters — see below.)
- **Config model** — resolves **env var → config file → smart default**, same precedence as huginn.
  Config file `${XDG_CONFIG_HOME:-~/.config}/freki/config` (override with `$FREKI_CONFIG`); if a key
  isn't set there, freki falls back to `~/.config/huginn/config` before the built-in default, so a
  huginn user gets a working freki with zero setup.

  | Key / env var | Falls back to | Default | Purpose |
  |---|---|---|---|
  | `FREKI_ROOT` | `HUGINN_ROOT` | `~/github-repos` | directory of repos to sweep |
  | `FREKI_OWNER` | `HUGINN_OWNER` | your `gh` login | GitHub owner of the estate repos |
  | `FREKI_STALE_DAYS` | _(none)_ | `90` | branch/artifact/release staleness threshold (days) |
  | `FREKI_PR_STALE_DAYS` | _(none)_ | `180` | days with no activity before a PR is "abandoned" |
  | `FREKI_CONVENTIONS` | `HUGINN_CONVENTIONS` | `repo-conventions` | dir under the root holding `exemptions.json` |
  | — | `HUGINN_FAMILY` | _(none)_ | space-separated repos to exclude, merged with `exemptions.json` |

- **Exemptions — they matter more here than anywhere, because this tool deletes.** Repos listed in
  `repo-conventions/exemptions.json` (shared with huginn) or in `$HUGINN_FAMILY` are **skipped
  entirely, by every command**. The profile repo, personal/creative repos, and another agent's repos
  live there — keep them there. (If `jq` were somehow absent, `exemptions.json` would be ignored and
  only `$HUGINN_FAMILY` honored — but `jq` is a hard requirement, so this shouldn't arise.)
- **The dry-run / `--apply` contract** (enforced in code, not just docs):
  - No `--apply` → freki prints `[dry-run] would …` lines and mutates **nothing**.
  - `--apply` → freki confirms **once for the whole batch** ("delete N thing(s)? [y/N]"), then deletes
    only what it listed. Answer anything other than `y`/`yes` and it aborts, having changed nothing.
  - `--yes` / `-y` → skips that single confirmation (for scripted/non-interactive runs).
  - **No tty + no `--yes`** → freki refuses (`no tty for confirmation — pass --yes to proceed
    non-interactively`) rather than guess. A piped `--apply` cannot silently delete.
- **Every actual deletion is logged** to `${XDG_STATE_HOME:-~/.local/state}/freki/reaped.log` — a
  tab-separated line per removal (UTC timestamp · repo · kind · detail), so an `--apply` run is
  auditable after the fact. Dry-runs log nothing.
- **`NO_COLOR`** — set it (`NO_COLOR=1 freki …`) to disable color; output is also automatically plain
  when not a TTY (piped or redirected).
- **Two-level help** — `freki help` for the menu, `freki <command> help` (or `-h`/`--help`) for one
  command.
- **Unknown options are ignored with a warning**, not fatal; an unknown *command* errors (`exit 1`)
  and prints the menu.
- **Exit codes** — `0` on success; `1` on error (a missing required tool, no resolvable owner, an
  unknown command, or a no-tty confirmation refusal).

---

## branches

Merged and long-stale branches across the estate — **local and remote** — extending huginn's
`branches --prune` estate-wide. It fetches each repo's remote (`--prune`) first, then classifies every
branch against `origin/<default>`:

- **Merged** branches (local or `origin/*`) are always eligible for `--apply`.
- **Stale-but-unmerged** branches — last commit ≥ `$FREKI_STALE_DAYS` (default **90 days**) — are
  listed but need **`--force`** as well to become eligible; without it they're shown as
  `(unmerged, stale Nd — needs --force)`.

It **never** touches the **default branch** or the **currently checked-out branch**. On `--apply`,
deleting a merged **remote** branch pushes a delete to `origin` — so this is a networked, real
deletion, not a local-only cleanup.

```sh
freki branches                  # dry-run: list merged + stale branches estate-wide, delete nothing
freki br                        # alias
freki branches --apply          # delete the merged ones (confirms once for the batch)
freki branches --apply --force  # also delete stale, unmerged branches
freki branches --apply --yes    # delete without the confirmation prompt
```

| Option | Effect |
|--------|--------|
| `--apply` | Delete the merged branches (local via `git branch -d`, remote via a push-delete to `origin`) |
| `--force` | Also make stale, **unmerged** branches eligible for deletion (still confirms) |
| `-y`, `--yes` | Skip the one batch-confirmation prompt (with `--apply`) |

---

## prs

Every **open** pull request across the estate, with the **abandoned** ones flagged — abandoned meaning
**no activity in ≥ `$FREKI_PR_STALE_DAYS` (default 180 days)**. It lists all open PRs so you see the
whole picture; `--apply` **closes only the abandoned ones**, each with a courteous comment. PRs with
recent activity are never touched.

```sh
freki prs               # dry-run: list all open PRs, mark the abandoned ones, close nothing
freki prs --apply       # close the abandoned PRs (confirms once for the batch)
freki prs --apply --yes # close them without the confirmation prompt
```

| Option | Effect |
|--------|--------|
| `--apply` | Close the abandoned PRs (with a courteous comment) |
| `-y`, `--yes` | Skip the one batch-confirmation prompt (with `--apply`) |

---

## artifacts

Old **GitHub Actions workflow artifacts** — the ones that silently eat a repo's storage quota. Lists
non-expired artifacts by age and size; `--apply` deletes those with **age ≥ `$FREKI_STALE_DAYS`
(default 90 days)**. **Already-expired artifacts are left alone** — GitHub reclaims those on its own,
so freki doesn't bother.

```sh
freki artifacts               # dry-run: list artifacts by age/size, mark those past the threshold
freki art                     # alias
freki artifacts --apply       # delete the ones past the threshold (confirms once for the batch)
freki artifacts --apply --yes # delete them without the confirmation prompt
```

| Option | Effect |
|--------|--------|
| `--apply` | Delete the artifacts at or past the staleness threshold |
| `-y`, `--yes` | Skip the one batch-confirmation prompt (with `--apply`) |

---

## releases

Stale **draft** releases and old **pre-releases**, age ≥ `$FREKI_STALE_DAYS` (default **90 days**).
Lists them; `--apply` deletes the **release entry only** — the underlying git tag, if any, is left
alone. It **never** touches a **published** release (non-draft, non-prerelease) or its tag.

```sh
freki releases               # dry-run: list stale drafts / old pre-releases, delete nothing
freki rel                    # alias
freki releases --apply       # delete those past the threshold (confirms once for the batch)
freki releases --apply --yes # delete them without the confirmation prompt
```

| Option | Effect |
|--------|--------|
| `--apply` | Delete the stale draft / pre-release entries past the threshold |
| `-y`, `--yes` | Skip the one batch-confirmation prompt (with `--apply`) |

---

## reap

The combined **"here's all the cruft"** summary across `branches` / `prs` / `artifacts` / `releases`,
with an estate-wide headline. **Dry-run only — `reap` never deletes anything itself**; it takes no
`--apply`. It runs the full scan for all four commands (so it's the slowest one); when you know what
you want gone, apply it per-command.

```sh
freki reap    # estate-wide cruft headline across all four surfaces — deletes nothing
```

*(No options. To actually clear anything, run the individual command with `--apply`.)*

---

## help

```sh
freki                  # no command → the menu
freki help             # the command menu
freki -h               # same
freki <command> help   # detail for one command (e.g. freki branches help)
```

---

## Recipes

```sh
# What cruft has piled up across the whole estate? (the flagship overview, deletes nothing)
freki reap

# See which branches I could reap — merged and stale — before touching anything
freki branches

# Delete the merged branches estate-wide (confirms once for the batch)
freki branches --apply

# …and also sweep the stale, unmerged ones
freki branches --apply --force

# Which open PRs are abandoned (no activity ≥ 180d)?
freki prs

# Close the abandoned PRs, unattended (no prompt)
freki prs --apply --yes

# What old CI artifacts are eating the quota?
freki artifacts

# Reclaim artifact storage past the 90-day threshold
freki artifacts --apply

# Clear stale draft / pre-releases (tags are left alone)
freki releases --apply

# Reap merged branches with a longer staleness window, just this run
FREKI_STALE_DAYS=180 freki branches

# Audit what a previous --apply run actually deleted
cat ~/.local/state/freki/reaped.log

# Plain output for a log/pipe (no color)
NO_COLOR=1 freki reap
```
