# CLAUDE.md — Freki Build Handoff
### The estate's reaper — the second of Odin's two wolves

> `huginn new` scaffolded this repo (guardrails, ruleset, labels, the full docs suite, a signed genesis
> commit). This file is the build brief for the agent that builds Freki. Read it top to bottom first.
> **huginn is your reference implementation** — read `~/github-repos/huginn/huginn` and match it.
> **Freki deletes things — read the "Safety rails" section before writing a single destructive call.**

---

## The concept

Odin keeps two ravens *and* two wolves. [`huginn`](https://github.com/brett-buskirk/huginn) (present
state) and [`muninn`](https://github.com/brett-buskirk/muninn) (memory) are the read-only ravens — they
observe and remember. The wolves are the pack with teeth. Its sibling
[`geri`](https://github.com/brett-buskirk/geri) is the hunter (finds what's dangerous or stale).

**Freki is the reaper.** It roams the whole `~/github-repos` estate, finds the accumulated **cruft**,
and — on your say-so — clears it: merged and stale branches, abandoned PRs, old CI artifacts eating
storage, dead draft releases. It reclaims the ground the ravens can only point at. huginn's
`branches --prune` is a Freki cub; Freki is that instinct, estate-wide and across more surfaces.

**Freki is the one tool in the pack with real teeth — so it is the most dangerous. Default to safe.**

## Scope — v0.1 (GitHub-only cruft · dry-run by default)

GitHub surface only in v0.1 — branches, PRs, artifacts, releases. **No cloud resources yet** (deferred).
Everything is derived live via `gh`; no stored state. Every command is **dry-run by default**: it lists
exactly what it *would* remove and stops. `--apply` is required to actually delete.

### `freki branches`
Merged and long-stale local + remote branches across the estate (extends huginn's `branches --prune` to
remote and estate-wide). Lists candidates; `--apply` deletes. **Never** the default/protected branch;
**never** an unmerged branch unless `--force` (and even then, confirm).

### `freki prs`
**Abandoned** open PRs — no activity in N months (configurable, default e.g. 6). Lists them; `--apply`
closes them with a courteous comment. Never touches PRs with recent activity.

### `freki artifacts`
Old **GitHub Actions workflow artifacts** (they silently consume the storage quota). Lists by age/size;
`--apply` deletes those past a threshold.

### `freki releases`
Stale **draft** releases and old **pre-releases**. Lists them; `--apply` deletes. **Never** a published
release or its tag.

### `freki reap`
The combined **"here's all the cruft"** summary across the above, with an estate headline. Dry-run only
(a summary view; you apply per-command).

## Safety rails (read this twice — it is the most important section)

Freki removes things, often irreversibly. These are non-negotiable:

- **Dry-run is the default.** Every command prints what it *would* do and exits without mutating.
  `--apply` is required to delete. On `--apply`, prompt for confirmation before irreversible ops unless
  `--yes` is passed.
- **Never touch:** the default or protected branch · unmerged branches (without explicit `--force`) ·
  published releases and their tags · anything with recent activity · a repo's only remaining branch.
- **Respect exemptions.** Reuse huginn's `is_exempt` (`repo-conventions/exemptions.json` + the
  `HUGINN_FAMILY` env var). Never reap an exempt repo (the profile repo, personal/creative repos, or
  another agent's repos).
- **Scope every destructive `gh` call narrowly**, and **log exactly what was removed** (repo, item,
  when) so an apply run is auditable. Prefer reversible ops; warn loudly before irreversible ones.
- **No cloud resources in v0.1.** Deleting cloud infra is a separate phase with its own auth and safety
  model (see Deferred) — do not reach past GitHub.

## Tech & architecture — mirror huginn

**huginn is the reference implementation — read it and match it.** huginn, muninn, geri, and freki
should feel like one four-tool pack.

- **Single Bash script** named `freki`, `set -uo pipefail`. Deps: `bash`, `git`, `gh`, `jq`.
- **Dispatcher + two-level help** (`freki help`, `freki <cmd> help`) — copy huginn's structure.
- **A shared dry-run/`--apply` spine.** Build the safe-by-default mechanism once (parse `--apply`/`--yes`,
  a `would()` vs `do_it()` helper, the confirmation prompt) and route every command through it, so no
  command can delete by accident.
- **Config-driven**, same precedence (env → `~/.config/freki/config` → smart defaults): `FREKI_ROOT`,
  `FREKI_OWNER`, plus thresholds (`FREKI_STALE_DAYS`, `FREKI_PR_STALE_DAYS`). **Fall back to huginn's
  config** for `HUGINN_ROOT`/`HUGINN_OWNER` when unset (mirror muninn).
- **Reuse huginn's estate model and `is_exempt`** (see Safety rails). Estate = dirs under `$ROOT` with `.git`.
- **Network where it must be** (`gh`) — mark those in help. Respect `NO_COLOR` and non-TTY.

## Working conventions (non-negotiable)

- **No direct commits to `main`.** Branch → PR → green checks → **stop at the PR and let Brett merge**
  (don't self-merge unless told). One command per PR.
- **Signed commits** (Verified); end messages with `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
- **AgentGate on every PR** (scaffolded). **`brett-buskirk` must be the active gh account.**
- **Match huginn's voice** — terse, lowercase, a little wry.

## Docs suite

`huginn new` scaffolded README / LICENSE / CHANGELOG / ROADMAP / CONTRIBUTING. Flesh out the **README**
(lead with the ravens/wolves framing) and make the **safe-by-default / `--apply`** contract loud and
early — a user must understand Freki won't bite by accident. Grow the **CHANGELOG** and **ROADMAP**.

## Phased plan (each phase → a version milestone; create them when you start)

- **v0.1.0 — Scaffold + the safety spine.** Dispatcher, config, estate model + `is_exempt`, and the
  shared dry-run/`--apply`/confirm framework. Ship this before any reaping command.
- **v0.2.0 — `branches`.** Merged/stale branches, estate-wide, remote + local.
- **v0.3.0 — `prs` + `artifacts`.** Abandoned PRs; old CI artifacts.
- **v0.4.0 — `releases` + `reap`.** Stale drafts/pre-releases; the combined summary.
- **v0.5.0 — CI & docs.** `shellcheck` gate; consolidated README with the safety contract up front.
- **v1.0.0 — Release.** Symlink install to `~/.local/bin/freki`, tagged `v1.0.0`, DoD met.

## Definition of Done

`freki branches`, `prs`, `artifacts`, `releases`, and `reap` all work against the live estate, **dry-run
by default**, respecting exemptions and every safety rail; `--apply` deletes only what was listed;
config-driven with two-level help; docs suite complete; passes `huginn doctor freki` clean; shipped as
**v0.1.0**. Feels unmistakably like huginn's packmate — and never bites by accident.

## Deferred — Roadmap (do NOT build in v0.1)

- **Cloud-resource reaping** — orphaned DigitalOcean / AWS / GCP resources (untagged droplets, stray
  buckets, dangling volumes/snapshots). The big one: real cost savings, but multi-provider auth and real
  spend/data risk — it gets its own phase and its own safety model. Not in v0.1.
- **`--json`** output; **scheduled reaping** (a periodic dry-run digest of accumulating cruft).
- **Going public** — like huginn/muninn, once solid.

## Reference repos

- **`~/github-repos/huginn`** — the reference implementation; match its structure, config, `is_exempt`,
  and voice. `branches --prune` is the seed of `freki branches`. Inspect the standard with `huginn conventions`.
- **`~/github-repos/muninn`** — the sibling with the huginn-config fallback pattern you'll reuse.
- **`~/github-repos/repo-conventions`** — the estate standard, including `exemptions.json`.
