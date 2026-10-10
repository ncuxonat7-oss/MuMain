# Work + Codex development model — owner decision, 2026-10-10

GitHub project memory is the shared source of truth. Classify every substantial technical task before starting it; do not duplicate the same task between Work and Codex. Tiny edits and obvious one-line changes need no extra process.

| Main uncertainty / remaining work | Owner / routing |
|---|---|
| WHAT is broken, WHERE it is, WHICH subsystem owns it, how systems interact | **WORK** investigates first. |
| Localized problem; known files/modules, clear goal and acceptance criteria; targeted tests can verify it; most work is coding | **CODEX PREFERRED**, proactively. |
| Mixed investigation and implementation | **WORK → CODEX** after affected scope and acceptance criteria are clear. |

## Responsibilities

**ChatGPT Work** remains broad technical lead, integration and investigation agent: broad baseline audits, root-cause investigation, client/server/Data compatibility analysis, runtime orchestration, external/reference research, evidence gathering, blocker identification, prioritization and deciding WHAT needs to change and WHY.

**Codex** is the preferred specialist for focused repository work once the problem is understood: implementing specified changes and well-defined server/client modules, localized bug fixes, reusable validators, importers/converters, refactoring known subsystems, writing/improving tests, focused code review and focused PR preparation.

Work retains a task when root cause is unknown, several subsystems must be correlated, runtime investigation is needed, browser/external-reference investigation is needed, or client/server/Data behavior is not yet understood. Do not follow the pattern “Work codes everything first; Codex is used only after Work gets stuck.” Use Codex proactively when the scope and verification are ready.

After **two substantially similar implementation attempts without meaningful progress**, stop repeating the approach and reconsider routing. Record both attempts and what was learned. Routing is not permission to duplicate work, spawn unnecessary agent teams, repeat successful checks, change the working stack or execute deferred tasks.

## Concise Codex handoff

Do not assume Codex has the current Work session context. Provide:

1. Goal.
2. Affected subsystem and known files/modules.
3. Confirmed current state, exact pins/checkpoint and relevant findings.
4. Acceptance criteria.
5. Targeted tests to run.
6. Constraints and relevant project-memory documents.
7. What was already tried and what must NOT be repeated.

State the task owner and whether a handoff was merely **prepared** or actually **delivered/accepted**. A written handoff is not evidence that another agent ran the task. Transfer a localized scope once; Work retains integration responsibility and unresolved cross-system questions. Return outcomes and useful discoveries to GitHub before closing the task.

## Durable memory requirement

Useful knowledge discovered by either Work or Codex that cost meaningful time or credits must return to persistent GitHub memory: findings and limits, mappings, working/failed approaches, reusable tools, tests/evidence and exact next unfinished step. Future agents must resume without rediscovering solved problems. Do not commit secrets or raw account/DB dumps.

## Current priority preserved

The current S6 baseline task remains the dry-run semantic crosswalk of scoped recipes and legacy quests from docs/current-state.md. Deferred client optimization stays in docs/deferred-client-optimization.md; future Client Modifiability / Extensibility Audit must evaluate clean feasibility/difficulty and gameplay timing/network invariance. FPS/AFK/multi-client/profile/effect work is **not executed now**, earns no readiness credit and creates no current blocker. MU Dream remains product/UX reference only, no proprietary code/resources.

Illusion Temple OUT OF SCOPE; Crywolf DEFERRED; trade sufficiently validated. No repeat bulk checks, verified fixes, native build or trade tests. No broad external import without owner approval. Readiness65.5%, model1.1, MEDIUM remains unchanged by this workflow decision.
