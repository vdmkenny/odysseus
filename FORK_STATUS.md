# Fork status — vdmkenny/odysseus

Tracks the features carried in this fork, their upstream PRs, and how they
depend on each other. Upstream = `pewdiepie-archdaemon/odysseus`.

This `main` branch is the fork's running build: latest upstream `main` + all the
open-PR branches + fork-only items, combined.

_Last updated: 2026-06-04 (src/search dedup PR #2506 finishes #2504)._

## Legend
- **Open PR** — proposed upstream, awaiting review/merge.
- **Merged** — landed upstream.
- **Closed** — not accepted (superseded or rejected).
- **Fork-only** — runs in the fork, not yet proposed upstream.

---

## Open PRs (proposed upstream)

| Feature | Branch | PR | State | Depends on | Notes |
|---|---|---|---|---|---|
| GitHub Copilot provider (device-flow auth) | `feat/github-copilot` | [#1480](https://github.com/pewdiepie-archdaemon/odysseus/pull/1480) | Open, mergeable | issue [#2021](https://github.com/pewdiepie-archdaemon/odysseus/issues/2021) | Modeled on opencode. OpenAI-compatible endpoint at `api.githubcopilot.com`; device-flow OAuth, token used directly as Bearer. |
| edit_file tool + file-change diffs | `file-write-diff` | [#1239](https://github.com/pewdiepie-archdaemon/odysseus/pull/1239) | Open, mergeable | issue [#2022](https://github.com/pewdiepie-archdaemon/odysseus/issues/2022) | Exact-string disk edit + unified diff; `write_file` shows diff too. |
| Workspace: confine agent tools to a folder | `workspace-confine` | [#1103](https://github.com/pewdiepie-archdaemon/odysseus/pull/1103) | Open, mergeable | issue [#2023](https://github.com/pewdiepie-archdaemon/odysseus/issues/2023) | Hard path confinement for file tools; bash/python `cwd`. Pairs with plan mode. |
| Plan mode for the chat agent | `plan-mode` | [#638](https://github.com/pewdiepie-archdaemon/odysseus/pull/638) | Open, mergeable | issue [#2024](https://github.com/pewdiepie-archdaemon/odysseus/issues/2024) | Read-only investigate → checklist → approve → execute. Now also: approved plan re-sent + pinned as `## ACTIVE PLAN` (survives context truncation), plan-button "Show plan" menu re-opens the dockable window, and `update_plan` tool for agent write-back (tick/revise, live). |
| CI workflow (syntax + tests) | `ci-checks` | [#1966](https://github.com/pewdiepie-archdaemon/odysseus/pull/1966) | Open (re-filed) | issue [#1965](https://github.com/pewdiepie-archdaemon/odysseus/issues/1965) | Re-opened after #1015 was closed for being tooling-without-an-issue; #1965 is the issue-first discussion. `.github/workflows/ci.yml`. |
| Code-navigation tools (grep, glob, ls) + read_file line ranges | `code-nav-tools` | [#1670](https://github.com/pewdiepie-archdaemon/odysseus/pull/1670) | Open, mergeable | issue [#2025](https://github.com/pewdiepie-archdaemon/odysseus/issues/2025) | Standalone version (confined to the `_resolve_tool_path` allowlist, no workspace dep). ripgrep-backed grep with Python fallback. |
| Round-limit handling — Continue at cap + configurable cap | `feat/continue-on-round-limit` | [#1999](https://github.com/pewdiepie-archdaemon/odysseus/pull/1999) | Open | issue [#1997](https://github.com/pewdiepie-archdaemon/odysseus/issues/1997) | `rounds_exhausted` event → Continue pill (bottom, repeatable); admin "Max steps per message" setting (validated 1..200). |
| `ask_user` — agent-posed multiple-choice questions | `feat/ask-user` | [#2111](https://github.com/pewdiepie-archdaemon/odysseus/pull/2111) | Open | issue [#2110](https://github.com/pewdiepie-archdaemon/odysseus/issues/2110) | `ask_user` tool → `ask_user` SSE event, ends the turn; card with option buttons + free-text Other + dismiss ×, removed once answered. Question streamed as assistant text so it persists/replays (prevents re-ask loop). Independent (clean off upstream `main`). **Screenshots still to be dragged into the PR.** |
| Provider line in the model-info card | `feat/provider-label` | [#2185](https://github.com/pewdiepie-archdaemon/odysseus/pull/2185) | Open | issue [#2184](https://github.com/pewdiepie-archdaemon/odysseus/issues/2184) | Model-info popup gains a **Provider** line from the session endpoint host (GitHub Copilot / OpenRouter / Anthropic / Local / …), distinguishing the same model name served by different routes. `providerLabel()` in `providers.js`. Independent (clean off upstream `main`). **Screenshot still to be dragged into the PR.** |
| Cleanup: drop unused `UPLOAD_DIR` imports | `chore/rm-unused-upload-dir-import` | [#2214](https://github.com/pewdiepie-archdaemon/odysseus/pull/2214) | Open | issue [#2213](https://github.com/pewdiepie-archdaemon/odysseus/issues/2213) | Pure upstream dead-code removal — 8 unused `from src.constants import UPLOAD_DIR` lines in `routes/document_routes.py`. One file, no behaviour change. Not a fork delta (not carried in the build). Small/focused — the rest of the unused-import findings deliberately left out. |
| Cleanup: drop unused `uuid` import | `chore/rm-unused-uuid-import` | [#2218](https://github.com/pewdiepie-archdaemon/odysseus/pull/2218) | Open | issue [#2217](https://github.com/pewdiepie-archdaemon/odysseus/issues/2217) | Pure dead-code removal — unused `import uuid` in `app.py`. One line, no behaviour change. Sibling of #2214. |
| Cleanup: dedupe `src/search` cache/content/query into shims | `chore/dedup-src-search` | [#2506](https://github.com/pewdiepie-archdaemon/odysseus/pull/2506) | Open | Fixes [#2504](https://github.com/pewdiepie-archdaemon/odysseus/issues/2504) | cache/content/query → `sys.modules` aliases of `services/search/*` (matches core/providers/ranking). ~600 dup LoC removed; src-coupled tests repointed to services; redundant parity-test params dropped. analytics is #2264. |
| Cleanup: dedupe `src/search/analytics.py` into a shim | `chore/dedup-search-analytics` | [#2269](https://github.com/pewdiepie-archdaemon/odysseus/pull/2269) | **Closed (dup)** | issue [#2262](https://github.com/pewdiepie-archdaemon/odysseus/issues/2262) | Closed in favour of #2264 (NubsCarson), opened ~4 min earlier for the same issue #2262 with a cleaner module-alias approach. Issue #2262 stays; #2264 fixes it. Fork build still carries the local shim until #2264 lands upstream. |

All rebased on fresh upstream `main` and use the upstream PR template.

> **Two code-nav variants.** The PR (`code-nav-tools`, #1670) is standalone —
> confined to the data/tmp allowlist, no workspace/plan dependency. The fork's
> running build instead carries the **workspace-aware** variant
> (`feat/code-nav-tools`): same tools, but confined to the active workspace and
> allowed in plan mode. Once #1670 lands upstream, the fork keeps the
> workspace-aware delta as a small follow-up.

## Fork-only (not yet upstreamed)

| Feature | Branch | In main build | Depends on (for clean upstream) | Notes |
|---|---|---|---|---|
| Code-navigation tools — workspace-aware variant | `feat/code-nav-tools` | yes | `workspace-confine` (#1103) path helper, `plan-mode` (#638) read-only set | Workspace-confined + plan-mode-readonly superset of #1670. Runs in the fork build; folds into #1670 once #1103 + #638 land. |
| Git branch indicator (workspace / data dir) | `feat/git-branch-indicator` | yes | `workspace-confine` (#1103) for the workspace readout | Shows the checked-out branch of the active workspace (else the data dir, only when the dir itself is a repo top level — doesn't climb to a parent repo); reloads on each LLM message. Silent no-op when git is unavailable. Ready to PR. |
| AGENTS.md / CLAUDE.md project instructions | `feat/agents-md` | yes | `workspace-confine` (#1103) workspace note block | Reads repo-authored instructions (AGENTS.md → CLAUDE.md, workspace root only, 32 KB cap) and prepends them to the system prompt. Mirrors opencode / Claude Code. Ready to PR (folds in with #1103). |
| Git + forge (gh/glab) agent tools | `feat/git-tools` | yes | `workspace-confine` (#1103) + `code-nav` (#1670); issue [#2053](https://github.com/pewdiepie-archdaemon/odysseus/issues/2053) | `git` (allowlisted subcommands incl. push, agent commit identity) + `forge` (auto-detects gh/glab, `pr`↔`mr` bridge) + `/git` slash + workspace git-context in the prompt. Admin-gated, workspace-required, excluded from plan mode, all binaries `shutil.which`-resolved (Windows-safe). **PR blocked**: its diff interleaves with #1103 (workspace param) and #1670 (tool registration) — open it once both land, then rebase clean onto upstream. |

## Project notes

- **No JS unit-test runner.** The repo has no `package.json` / jest / vitest /
  playwright. CI (`#1015`) runs `python -m py_compile`, `node --check`, and
  `pytest`. `tests/bombadil-spec.ts` is an external Antithesis harness, not unit
  tests. So JS-only changes are covered by `node --check` + manual/browser
  verification; Python logic gets `pytest` tests.

## Candidate next features (from the Claude Code / opencode gap analysis)

Ranked by leverage × effort. (Biggest gap — first-class code navigation — is
done: #1670.)

1. **`AGENTS.md` auto-load** — read a repo/workspace instructions file and
   prepend to the agent system prompt (what `CLAUDE.md` / `AGENTS.md` do
   upstream of us). Cheap, high value. Pairs with workspace (#1103).
2. **Edit checkpoint / undo** — snapshot files before `edit_file`/`write_file`
   per turn; expose "revert last agent change". Safety.
3. **Parallel tool execution** — independent tool calls run sequentially today;
   `asyncio.gather` the read-only ones. Latency.

Lower priority: per-action approval prompts, LSP/diagnostics loop.

## Merged upstream

| Feature | PR |
|---|---|
| Fix chat offset/overlap/animation when a docked modal closes | [#1158](https://github.com/pewdiepie-archdaemon/odysseus/pull/1158) |
| Accessibility: ARIA labels and toggle states | [#1010](https://github.com/pewdiepie-archdaemon/odysseus/pull/1010) |
| Cleanup: remove unused imports in calendar_routes | [#2221](https://github.com/pewdiepie-archdaemon/odysseus/pull/2221) |
| Expand `~` in read_file/write_file paths | [#781](https://github.com/pewdiepie-archdaemon/odysseus/pull/781) |

## Closed (not accepted)

| Feature | PR | Why |
|---|---|---|
| edit_file (first attempt) | [#1171](https://github.com/pewdiepie-archdaemon/odysseus/pull/1171) | Superseded by the focused #1239. |
| Favorite models in the picker | [#597](https://github.com/pewdiepie-archdaemon/odysseus/pull/597) | Another PR implemented something similar; excluded. |
| CI workflow — first attempt | [#1015](https://github.com/pewdiepie-archdaemon/odysseus/pull/1015) | Closed for being tooling-without-an-issue. Re-filed as #1966 with issue #1965. |
| Text-only emoji streaming fix | [#1692](https://github.com/pewdiepie-archdaemon/odysseus/pull/1692) | Maintainer read it as emoji-rendering (it's a strip-mode bugfix); needs reframe + visual clip. Dropped from build; branch `fix/text-emoji-streaming` parked. |

> **Maintainer is automated + strict on CONTRIBUTING.** Tooling/CI and visual/UI
> changes are gated: open an **issue first** for tooling, and attach a
> **screenshot/clip** for anything touching `static/` (DOM). Frame fixes precisely
> to avoid policy false-positives.

---

## Dependency graph (upstreaming order)

```
Open PRs — all independent, merge in any order:
  github-copilot (#1480)
  edit_file (#1239)
  workspace-confine (#1103)
  plan-mode (#638)
  code-nav-tools (#1670)   ← standalone (allowlist-confined)
  ci-checks (#1966)        ← re-filed; issue #1965

Fork-only deltas (need workspace #1103 [+ plan #638] for a clean upstream PR):
  feat/code-nav-tools (workspace-aware) ──needs──► workspace-confine (#1103) + plan-mode (#638)
  feat/git-branch-indicator             ──needs──► workspace-confine (#1103)
  feat/agents-md (AGENTS.md/CLAUDE.md)  ──needs──► workspace-confine (#1103)
```

- The open PRs are mutually independent and can merge in any order.
- The fork-only **workspace-aware code-nav**, **git-branch-indicator**, and
  **agents-md** deltas reuse the workspace plumbing (#1103); the workspace-aware
  code-nav also reuses the plan-mode read-only set (#638). Functional on the
  fork today regardless — the dependency only matters for a clean upstream
  cherry-pick.
