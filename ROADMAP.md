# Roadmap

_What's planned for freki — check items off as they ship. Each phase is a version milestone._

## Phases

- [x] **v0.1.0 — Scaffold + the safety spine.** Dispatcher, config, estate model + `is_exempt`, and
      the shared dry-run/`--apply`/confirm framework. Shipped before any reaping command.
- [x] **v0.2.0 — `branches`.** Merged/stale branches, estate-wide, remote + local.
- [ ] **v0.3.0 — `prs` + `artifacts`.** Abandoned PRs; old CI artifacts.
- [ ] **v0.4.0 — `releases` + `reap`.** Stale drafts/pre-releases; the combined summary.
- [ ] **v0.5.0 — CI & docs.** `shellcheck` gate; consolidated README with the safety contract up front.
- [ ] **v1.0.0 — Release.** Symlink install to `~/.local/bin/freki`, tagged `v1.0.0`, Definition of
      Done met.

## Deferred (do NOT build before v1.0)

- **Cloud-resource reaping** — orphaned DigitalOcean / AWS / GCP resources (untagged droplets, stray
  buckets, dangling volumes/snapshots). Real cost savings, but multi-provider auth and real
  spend/data risk mean it gets its own phase and its own safety model.
- **`--json` output.**
- **Scheduled reaping** — a periodic dry-run digest of accumulating cruft.
- **Going public** — like huginn/muninn, once solid.

## Polish

- [ ] `shellcheck` in CI.
- [ ] Bats tests for the pure-logic helpers (`is_exempt`, `repos`, the safety spine).
