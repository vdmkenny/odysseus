# AGENTS.md — Odysseus Code (fork conventions)

This repo is **Odysseus Code**, a fork of
[`pewdiepie-archdaemon/odysseus`](https://github.com/pewdiepie-archdaemon/odysseus)
that adds Claude Code / opencode-style agent features. These instructions are
**fork-only** — they never go upstream.

## Golden rules

- **Follow upstream.** `main` = latest upstream `main` + our open-PR branches +
  fork-only items, combined. Rebase on fresh `origin/main` regularly.
- **Upstream everything.** Every feature is developed as a focused,
  upstream-targeted PR branch off `origin/main`, using the upstream PR template.
- **Keep [`FORK_STATUS.md`](FORK_STATUS.md) in sync.** Whenever a feature is
  added, a PR opens/merges/closes, a dependency changes, or a branch is
  created/dropped — update `FORK_STATUS.md` in the same change. It is the
  source of truth for what this fork carries and where each piece stands.

## Fork-only artifacts — never include in upstream PRs

- `FORK_STATUS.md` (status tracker)
- `AGENTS.md` (this file)
- The **rebrand** commit (README "Odysseus Code" title + fork note) — kept as a
  single isolated commit so it can be left out of any PR. Do not mix rebrand
  edits into feature commits.

Feature PR branches are built off `origin/main` and must contain **only** the
feature — none of the above.

## Working with the upstream maintainer (automated + strict)

**Status (2026-06-04): vdmkenny is now a Collaborator with write access.**

- **PRs target `dev`, NOT `main`.** `main` is curated by the maintainer
  (pewdiepie-archdaemon); `dev` is the integration branch (`dev` is ahead of
  `main`). Base every new PR on `dev`; rebase open branches onto `origin/dev`.
- Write access means branches can be pushed to the upstream repo directly, but
  keep using PRs into `dev` for review. Do not push to or merge `main`.
- Maintainer contact: Felix; email shared off-list.

Upstream enforces `CONTRIBUTING.md` mechanically:

- **ALWAYS re-read `CONTRIBUTING.md` fresh** (from `origin/dev`) before opening
  or updating any issue or PR, and verify the submission against it — it changes,
  and conformance is gated. Use the current issue/PR templates.
- **Tooling/CI changes** (workflows, dev tooling, packaging) → **open an issue
  first**; don't PR them cold (see closed #1015).
- **Any change under `static/` that draws to the DOM** is "visual" → **attach a
  screenshot or short clip** in the PR, and match the existing monochrome-SVG
  style. **No Unicode emoji in UI or code** — use inline SVG or plain text.
- Frame fixes precisely so a pattern-matching reviewer doesn't misread them
  (e.g. #1692 — a text-only-emoji *strip* bugfix was misread as emoji rendering).

## Tests / checks

No JS unit-test runner exists. Run the smallest relevant checks:

```
python -m py_compile <changed .py>
node --check static/js/<changed>.js
python -m pytest tests/<relevant>.py
```

Python logic gets `pytest` tests; JS changes get `node --check` + browser
verification.
