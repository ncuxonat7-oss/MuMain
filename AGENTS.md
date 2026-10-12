# Project bootstrap / task router

Canonical repository:ncuxonat7-oss/MuMain. Start with the newest section of docs/current-state.md (the single current next step and its approval gate); older next-action queues are historical. Do not replay successful tests. Work is disposable; commit/push useful atomic checkpoints; never commit secrets or DB dumps. No broad research, stack replacement, paid services or production changes without owner authorization. Credit balance is not visible; explain costly work before starting. After two identical failures reassess. Standard baseline before major customization.

Owner routing: before substantial work classify WORK (uncertain root cause/cross-system/runtime/reference investigation), CODEX PREFERRED (localized repository implementation/refactoring/tests/review with clear scope and acceptance), or mixed WORK→CODEX after investigation. Read docs/work-codex-routing.md for responsibilities and concise handoff. Use Codex proactively, not only after Work gets stuck; do not duplicate the same task. After two similar implementation attempts without meaningful progress reconsider routing. Tiny edits need no ceremony. Useful discoveries from either agent return to GitHub memory; do not assume shared session context. Future client optimization remains DEFERRED in docs/deferred-client-optimization.md and must be assessed by the future Client Modifiability / Extensibility Audit, not executed during S6 baseline work.

Deferred external OpenMU configuration/packet issue pointers are stored in [docs/deferred-external-findings-2026-10-12.md](docs/deferred-external-findings-2026-10-12.md). Consult only when a matching future in-scope issue or upgrade arises; this is not a new task and does not change current Alpha priorities.\n\nRead only documents relevant to the task:

|Task|Read next|
|---|---|
|Resume/checkpoint|docs/current-state.md; docs/test-history.md for contradictory results|
|Maps/NPC/spawns/shop/items/drop/skill/quest bug|docs/navigation.md; relevant rows of docs/baseline-content-audit.md; query saved export with scripts/query-baseline.py|
|Client/build/resource issue|docs/architecture.md; docs/resource-registry.md; relevant client checker findings|
|Database/persistence|docs/architecture.md; newest snapshot in docs/resource-registry.md; relevant test-history row|
|Score/mass validation|docs/baseline-content-audit.md; docs/baseline-readiness.json; scripts/score-baseline.py; existing bulk-config-validation.md|
|Owner intent/scope/architecture decision|docs/product-vision.md; docs/decisions.md|
|Blocked operation/repeated failure|Relevant entries in docs/lessons-learned.md; no repeat CI/build just to inspect state|

Owner-defined model1.1 preserves model1.0 weights and original checklist; see docs/baseline-scope.md and archived ledger. Illusion Temple is OUT OF SCOPE; Crywolf is DEFERRED late stage. Neither is a current RED blocker or readiness penalty. Preserve findings; no fixes/runtime work on them now. Trade baseline is sufficiently validated; no deeper trade tests. Current priority is the bounded local Windows 11 Alpha path recorded in docs/current-state.md. Older bulk/recipe expansion queues are parked unless the owner explicitly reopens them; external import requires separately proven missing S6 records and approval. Source/config/assets present alone earns no readiness credit. Update evidence limits and score only after uncertainty materially reduces or defects are fixed; preserve comparison/history. Distinguish static/automatic/runtime/inferred/unknown. Two native connections do not prove party/trade.

No complex agent orchestration. Reuse validated artifacts/cache/DB; smallest targeted validation then owner alpha testing. See docs/navigation.md for bug report format. Read the original coding rules below before code changes; preserve existing source structure. This bootstrap adds project memory and does not override original repository rules.

Current packaging checkpoint (2026-10-12): read docs/current-state.md and checkpoints/local-alpha/2026-10-12-full-disabled-alpha/phase1124-full-disabled-alpha/report.txt. Full disabled-package integrity and 13 integrated PowerShell cases passed locally; Windows/HTTP/runtime acceptance has not run. Single next step is the existing package Verify command in an agreed Windows acceptance environment, awaiting separate owner authorization. Keep launch/setup/grants blocked; do not repeat completed local packaging tests.

---

# Agent Instructions

This file is the entry point for AI coding assistants (Claude Code, Cursor, Codex,
etc.) working in this repository. It also applies to human contributors.

## Coding rules — read first

**The coding rules in [`docs/CODING_RULES.md`](docs/CODING_RULES.md) apply to all
code changes in this repository, by humans and by AI agents alike.**

Before writing or modifying code:

1. Read [`docs/CODING_RULES.md`](docs/CODING_RULES.md).
2. Apply the rules to any new or changed code.
3. When reviewing a change (including via `/review` or `/ultrareview`), treat
   `docs/CODING_RULES.md` as the authoritative style and quality baseline.

The rules are not exhaustive — they capture the conventions that matter most for
this codebase. Follow the style of surrounding code where the rules don't speak.

## Build setup

The project uses CMake. Supported build environments and setup steps are
documented in [`docs/build/README.md`](docs/build/README.md).

Quick references:

- Requirements and IDE-specific instructions: [`README.md`](README.md).
- Cross-platform / WSL build details: [`docs/build/README.md`](docs/build/README.md).

## Checkpoint documentation

The latest integrated setup source/evidence is checkpoints/local-alpha/2026-10-12-alpha-setup-integrated/README.md: 82 unit checks PASS and prior actual Account load/save/rollback evidence retained. Parent candidate evidence backup remains pending its follow-up commit. Follow only the newest docs/current-state.md next step: separately authorized Windows deployment/credential handoff. Publication enables neither setup nor launch; do not rerun completed stages.

The 2026-10-12 admin-only diagnostic and the subsequent single GameConfiguration read are complete; reuse their saved evidence. See checkpoints/local-alpha/2026-10-12-binary-json-read/README.md: one actual read PASS, 35 driver guard cases PASS, PostgreSQL stopped, original hashes intact. Follow only the newest next step in docs/current-state.md; older preparation queues are historical. Full ACL closure, Typed reads and Windows readiness remain unproven; keep setup/launch guards blocked.

At ordinary checkpoints, keep one unambiguous next step in docs/current-state.md and mark older completed, cancelled, or parked instructions as superseded while preserving evidence and links. After substantial code/configuration changes, refresh only the matching existing ALPHA-NAV/STACK entry or mark its evidence stale. Use the existing document structure; do not expand this into a separate audit or catalog. Publication, main merges, deployments, and costly stages still require the owner's applicable approval.

## Branch and PR conventions

- Target branch for PRs is `main`.
- Keep changes focused — one concern per commit (see rule 10 in the coding
  rules). Smaller diffs review faster.
- Match the style of existing commit messages in `git log`.
- Reference the related issue in the PR description when applicable.

## Out of scope for AI changes

Don't perform large retroactive cleanups of existing code to fit the rules unless
the user explicitly asks for it. Apply the rules going forward; pre-existing
code can be refactored opportunistically when you're already touching it.




