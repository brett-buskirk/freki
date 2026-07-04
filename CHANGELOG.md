# Changelog

All notable changes to freki are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2026-07-04

### Added
- **`releases`** — stale draft releases and old pre-releases per repo, age ≥ `$FREKI_STALE_DAYS`
  (default 90 days). `--apply` deletes the release entry via the GitHub API; the underlying git tag,
  if any, is left alone. Never touches a published (non-draft, non-prerelease) release or its tag.
- **`reap`** — a dry-run-only combined summary across `branches`/`prs`/`artifacts`/`releases`, with
  an estate-wide headline (reapable counts per category). Never deletes anything itself — points you
  at the per-command `--apply`. Reuses each command's own scan (via small additive counters exposed
  after each command's existing dry-run pass) rather than duplicating the scan logic.
- All five commands now implemented, matching the original v0.1.0–v0.4.0 phased plan.

## [0.3.0] - 2026-07-04

### Added
- **`prs`** — every open PR across the estate via a single `gh search prs --owner` query, flagging
  ones with no activity in `$FREKI_PR_STALE_DAYS` (default 180 days). `--apply` closes the abandoned
  ones with a courteous comment (`gh pr close --comment`), confirming once for the batch.
- **`artifacts`** — non-expired GitHub Actions workflow artifacts per repo, by age/size.
  `--apply` deletes those at or past `$FREKI_STALE_DAYS` (default 90 days). Already-expired artifacts
  are skipped — GitHub reclaims those on its own regardless of what freki does.
- Both route through the same batch-confirm/`do_it`/`log_action` safety spine as `branches`.

## [0.2.0] - 2026-07-04

### Added
- **`branches`** — merged and long-stale local + remote branches across the estate, extending
  huginn's `branches --prune` to remote refs and the whole estate. Merged branches are always
  eligible for `--apply`; stale-but-unmerged branches also need `--force`. Never touches the default
  branch or the currently checked-out branch. A destructive `--apply` run confirms once for the
  whole batch (skip with `--yes`), and every deletion routes through the safety spine's
  `do_it`/`log_action` for an auditable record.

## [0.1.0] - 2026-07-04

First cut — the scaffold and safety spine, before any reaping command exists.

### Added
- **Dispatcher + two-level help** — `freki help` (top-level menu) and `freki <command> help`
  (per-command detail), mirroring huginn's structure and voice.
- **Config-driven** — settings resolve env → config file → smart defaults: `FREKI_ROOT`,
  `FREKI_OWNER`, `FREKI_STALE_DAYS`, `FREKI_PR_STALE_DAYS`, `FREKI_CONVENTIONS`. Config lives at
  `~/.config/freki/config`. Falls back to `~/.config/huginn/config`'s `HUGINN_ROOT`/`HUGINN_OWNER`/
  `HUGINN_CONVENTIONS` when unset, so a huginn user gets a working freki with zero setup (same
  pattern as muninn).
- **Estate model** — repos are any top-level directory under `$FREKI_ROOT` with a `.git` folder,
  identical to huginn's `repos()`.
- **Exemptions** — reuses huginn's `is_exempt`: repos listed in `repo-conventions/exemptions.json`
  or the `$HUGINN_FAMILY` env var are skipped by every command. Ships a bundled, empty
  `templates/exemptions.json` fallback so the tool degrades safely with no conventions repo present.
- **The shared dry-run/`--apply`/confirm safety spine** — `would()`, `confirm()`, `do_it()`, and
  `log_action()`. Dry-run is the default for every command; `--apply` is required to mutate, and a
  destructive `--apply` run still confirms (reading from `/dev/tty`, so piped stdin can't skip it)
  unless `--yes` is also passed. Every deletion made with `--apply` is logged to
  `~/.local/state/freki/reaped.log` (repo, kind, detail, UTC timestamp) for after-the-fact audit.
- **Dependency check** — `need_deps` verifies `git`/`gh`/`jq` are on `PATH` before a command runs;
  a missing `jq` at startup degrades exemptions to `$HUGINN_FAMILY`-only with a loud warning, rather
  than silently narrowing what's protected.
- Command stubs for `branches`, `prs`, `artifacts`, `releases`, and `reap` — each documents its
  planned contract via `help_<name>` and reports "not built yet" until its milestone lands.
