# freki

The reaper of your GitHub estate — finds and clears the cruft (stale branches, dead PRs, old CI
artifacts, stale draft releases). Named for Odin's wolf: the pack's hunter, and its most dangerous
member.

In Norse myth Odin keeps two ravens, **Huginn** (*thought*) and **Muninn** (*memory*), and two wolves,
**Geri** and **Freki** (both meaning roughly "the ravenous one"). The ravens
([`huginn`](https://github.com/brett-buskirk/huginn), [`muninn`](https://github.com/brett-buskirk/muninn))
observe and remember — they're read-only. The wolves have teeth: [`geri`](https://github.com/brett-buskirk/geri)
hunts down what's dangerous or stale (outdated deps, advisories, drift); **freki reaps it** — merged
and abandoned branches, dead PRs, old artifacts, stale releases — across the whole estate.

> **Freki is the one tool in the pack that deletes things — so it's the most dangerous, and it
> defaults to safe.** Every command is **dry-run by default**: it lists exactly what it *would*
> remove and stops. Nothing is deleted until you pass `--apply`, and destructive `--apply` runs still
> confirm before touching anything, unless you also pass `--yes`. See [Safety](#safety) below.

## Status

**v0.1.0 — scaffold only.** The dispatcher, config, estate model, exemptions, and the shared
dry-run/`--apply`/confirm safety spine are in place, but none of the reaping commands are wired up
yet — `branches`, `prs`, `artifacts`, `releases`, and `reap` all currently print a "not built yet"
notice pointing here. See [ROADMAP.md](ROADMAP.md) for the phased build-out.

## Install

Requirements: `bash`, `git`, [`gh`](https://cli.github.com) (authenticated), `jq`.

```bash
git clone git@github.com:brett-buskirk/freki.git ~/github-repos/freki
ln -s ~/github-repos/freki/freki ~/.local/bin/freki   # ~/.local/bin must be on your PATH
```

freki manages the repos in **`$FREKI_ROOT`** (default `~/github-repos`) — the same estate huginn
manages. If you already run `huginn`, freki picks up its config automatically (see
[Configuration](#configuration)); there's nothing extra to set up.

## Commands

```
reap
  branches [--apply]    merged/stale branches, estate-wide           (v0.2.0)
  prs [--apply]         abandoned open PRs                           (v0.3.0)
  artifacts [--apply]   old CI workflow artifacts                    (v0.3.0)
  releases [--apply]    stale draft / pre-releases                   (v0.4.0)
  reap                  the combined cruft summary                   (v0.4.0)
reference
  help                  this menu
```

Run **`freki <command> help`** for details and options on any command (works today, even before a
command is built — it documents the planned contract).

## Safety

These rules are non-negotiable, and they're enforced in code, not just documentation:

- **Dry-run is the default.** Every command prints what it *would* do and exits without mutating.
  `--apply` is required to delete anything.
- **Confirms before deleting**, even with `--apply` — unless you also pass `--yes`. The confirmation
  prompt reads from `/dev/tty`, so a piped or scripted stdin can't accidentally skip it.
- **Never touches:** the default/protected branch · unmerged branches (without explicit `--force`,
  and even then it confirms) · published releases and their tags · anything with recent activity.
- **Respects exemptions** — repos in `repo-conventions/exemptions.json` (shared with huginn) or
  listed in `$HUGINN_FAMILY` are skipped entirely, everywhere.
- **Logs every deletion** it actually makes to `~/.local/state/freki/reaped.log` (repo, kind, detail,
  UTC timestamp) so an `--apply` run is auditable after the fact.
- **GitHub-only in v0.1.** No cloud-resource deletion (droplets, buckets, volumes) yet — that's a
  deferred phase with its own auth and safety model. See [ROADMAP.md](ROADMAP.md).

## How it works

- **Estate model** — identical to huginn's: any top-level directory under `$FREKI_ROOT` containing a
  `.git` folder is a managed repo. No stored state; everything is derived live via `git`/`gh` — no
  caching, no daemon, no telemetry.
- **Exemptions, shared with huginn** — freki reads `repo-conventions/exemptions.json` and merges it
  with the `$HUGINN_FAMILY` env var, the same convention huginn/muninn use. A repo listed there is
  never touched by any freki command.
- **Respects `NO_COLOR`** and non-TTY output.

## Configuration

Settings resolve **environment variable → config file → smart default**, same precedence as huginn.
Config file: `${XDG_CONFIG_HOME:-~/.config}/freki/config` (override with `FREKI_CONFIG`). If a key
isn't set there, freki falls back to `~/.config/huginn/config` before using the built-in default — a
huginn user gets a working freki with zero setup.

| Key / env var | Falls back to | Default | Purpose |
|---|---|---|---|
| `FREKI_ROOT` | `HUGINN_ROOT` | `~/github-repos` | directory of repos to manage |
| `FREKI_OWNER` | `HUGINN_OWNER` | your `gh` login | GitHub owner of the estate repos |
| `FREKI_STALE_DAYS` | _(none)_ | `90` | days since the last commit for a branch to count as stale |
| `FREKI_PR_STALE_DAYS` | _(none)_ | `180` | days with no activity for a PR to count as abandoned |
| `FREKI_CONVENTIONS` | `HUGINN_CONVENTIONS` | `repo-conventions` | dir under the root with `exemptions.json` |
| — | `HUGINN_FAMILY` | _(none)_ | space-separated repos to exclude, merged with `exemptions.json` |

## Backstory

freki is the fourth tool in the [huginn](https://github.com/brett-buskirk/huginn) /
[muninn](https://github.com/brett-buskirk/muninn) / [geri](https://github.com/brett-buskirk/geri) /
freki estate-management pack — see huginn's README for the fuller story of why this exists.

## License

[MIT](LICENSE) © 2026 Brett Buskirk
