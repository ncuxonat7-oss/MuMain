# Deferred external findings — OpenMU S6 / agent maintenance

Recorded 2026-10-12 for later *targeted* use. These are **external issue reports / review triggers**, not verified defects in our pinned client/server, accepted fixes, or implementation requests. Current local Windows Season 6 Alpha, its newest durable checkpoint, launch/setup approval gates and existing owner priorities remain authoritative.

## 1. OpenMU game-configuration update behavior — DEFERRED WATCH

- Primary source: [MUnique/OpenMU issue #984](https://github.com/MUnique/OpenMU/issues/984), opened 2026-09-26. The issue describes required configuration-data update plugins and optional changed-default-value plugins being listed together, with insufficient before/after visibility. This is a **proposal**, not evidence that its suggested preview/separation has shipped. EF schema migrations are explicitly distinct.
- Relevance: before **future version upgrades, custom balance/shop changes, or production configuration import**, preserve actual operator-customized values and compare intended changes with the live configuration on an isolated copy. Avoid silently overwriting PvP rules, item/shop values or other intentional settings.
- Trigger to revisit: a concrete requested OpenMU upgrade, applied update plugin, game-config import, or a reproducible config drift/overwrite symptom.
- Cheapest response then: identify pinned and target versions, effective data source and update-plugin behavior; review a bounded diff/backup/rollback plan on a non-production copy. Do **not** build a new administration UI or migration framework now.

## 2. Season 6 packet layouts — DEFERRED / OUT OF SCOPE where applicable

- Primary source: [MUnique/OpenMU issue #1006](https://github.com/MUnique/OpenMU/issues/1006), opened 2026-09-29. A contributor reports struct packing / offset incompatibilities affecting several Castle Siege and Illusion Temple packets plus the letter list. The contributor reports runtime testing; this has **not been confirmed for our pinned MuMain+OpenMU binaries**. An open issue does not mean a fix has been accepted or included.
- Relevance: if a *future in-scope* Castle Siege NPC or in-game mail/letter failure appears, use the cited packet IDs, native receiver layout and actual bytes as a bounded diagnostic starting point rather than beginning a full protocol audit.
- Scope: Illusion Temple remains **OUT OF SCOPE** under the owner's standing decision. Castle Siege and mail are not new local-Alpha obligations merely because this issue exists.
- Trigger to revisit: owner reopens relevant feature scope or a reproducible failure within approved scope. First compare versions/packets and existing evidence; do not change wire formats, client, server or readiness based only on this report.

## 3. Knowledge map upkeep — EXISTING RULE, not a new subsystem

The current checkpoint's `AGENTS.md` already requires refreshing the affected existing ALPHA-NAV/STACK entry, or marking evidence stale, after substantial code/configuration changes. Reuse that rule; do not create a second index, automatic crawler, vector database or broad discovery phase for these two external issues.

## Operational constraints

- **DEFERRED / reference-only**. No changes to code, runtime configuration, database, credentials, launch flags, dependencies, migrations, networking or user-facing deployment are authorized by this note.
- No retesting confirmed Alpha scenarios, downloading source trees or performing speculative investigations simply to clear these notes.
- When revisited, establish which issue claims still apply to the **exact pinned version**, distinguish STATIC from actual runtime proof, and close only the scoped task with evidence.
- Do not elevate GitHub issue claims to `VERIFIED` for this project; do not increment readiness.
- Keep the existing current-state checkpoint as the sole authority for the next task.
