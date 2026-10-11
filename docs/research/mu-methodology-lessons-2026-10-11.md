# MU methodology research — verified takeaways (2026-10-11)

Owner-requested bounded methodology review. No project code, access, environment, executable downloads or development tasks changed. 17 source families reviewed: 10 OpenMU/MuMain issue/PR/commit chains and 7 public RaGEZONE discussions. Forum reports are experience, not independently verified fixes or production reliability.

## Authority and scope
Priority remains stable local Windows 11 S6 Alpha on the pinned client/server/Data/PostgreSQL stack. Readiness remains 65.5 (model 1.1, MEDIUM evidence confidence), not percent software completion. Recommendations below are proposals, not approval to implement an architectural change.

## Confirmed upstream facts useful to future agents
1. MuMain #393 is OPEN design discussion (2026-05-16; comments through June 6). The maintainer favors SQLite and versioned/per-realm configuration; inspected timeline does not establish an implementing PR. Do not treat this as an available synchronization tool or an Alpha prerequisite.
   https://github.com/sven-n/MuMain/issues/393
2. MuMain energy-requirement issues #273/#333 were closed by 7f734ce (2026-05-18). Its actual two-file change uses SkillAttribute[].Energy directly, unlike the proposed Level+1 workaround. Twisting Slash is named. Presence in our pinned client and actual cast success remain unverified.
   https://github.com/sven-n/MuMain/commit/7f734ce5542aabde022a6bd492e5018a4a697560
3. OpenMU test actors #964 merged 2026-09-19. Documentation/review explicitly limits skill commands to targeted casting, excluding AreaSkillAttackAction. Connection-less actors do not prove native client input, rendering or authentication. Reported tests are upstream evidence, not rerun here.
   https://github.com/MUnique/OpenMU/pull/964
4. Real PostgreSQL integration proposal #905 remains OPEN (2026-08-26). Merged startup fix #910 distinguishes missing/unknown/initialized configuration; its author explicitly did not verify real-PostgreSQL end-to-end startup. Unit success alone cannot establish restore/login/persistence.
   https://github.com/MUnique/OpenMU/issues/905
   https://github.com/MUnique/OpenMU/pull/910
5. Merged concurrency repair #940 (2026-09-21) centralizes synchronized effects collection access and includes bounded concurrent-reader/writer regression tests. It is not exhaustive concurrency or production-uptime evidence.
   https://github.com/MUnique/OpenMU/pull/940
6. Merged config-versioning #1027 (2026-10-04) preserves plugin GUID identity and adds repair/version semantics, with in-memory tests and explicitly skipped PostgreSQL cases. Do not infer real migration safety or presence in our pin.
   https://github.com/MUnique/OpenMU/pull/1027
7. Apparent jewel duplication #465 (2024-08-20) was traced to editor-created durability retained from a previous item definition; the fix resets durability when changing definition. Item provenance and fixture invariants matter before rewriting transaction logic.
   https://github.com/MUnique/OpenMU/issues/465
   https://github.com/MUnique/OpenMU/commit/5fad28acd06adbc01d98925f4660dcb2c62086e0
8. PostgreSQL container-layout issue #665 and merged #666 (2025-11-21) document deployment assumptions broken by a major-version change. This is Docker-specific, not a Windows-native defect. Pin versions; migration/restore remain distinct checks.
   https://github.com/MUnique/OpenMU/pull/666
9. S6 receiver-layout PR #1007 is OPEN/unmerged as inspected. Author reports packet/native checks; not independently rerun. Serializer tests and injected visual output do not establish an entire event works.
   https://github.com/MUnique/OpenMU/pull/1007

## Proposed engineering application, not new implementation
- Keep one authoritative version/evidence ledger. Preserve old completed checks without allowing stale EXACT NEXT sections to override newer owner decisions.
- Reuse the existing seven-card player QA kit and component manifest. Add only a missing critical scenario/fixture when it answers a specific question. No new dashboard or comprehensive test framework prerequisite.
- Preserve separate states for skill learned/relogged, client cast, server hit/damage and persistence. Twisting Slash casting remains unproven.
- Before local Alpha: reproducible matched package, local exposure controls, login/basic play, critical state save/reconnect and a recoverable baseline. Existing valid evidence can be reused; recheck changed boundaries only.
- Before public use, separately require multi-user transaction/disconnect, abuse/security, load/soak and recovery evidence. A solo local Alpha does not establish these.
- Deep auditing of every mechanic, new configuration-sync architecture, broad content/economy tuning, website/VPS/donation and FPS work stay outside the immediate Alpha gate.
- Each future change should have a finite scenario, observable expected outcome, expense bound and rollback; stop repeated attempts that generate no new evidence.

## Evidence limitations
No inspected forum history establishes measured long-running S6 uptime, concurrency capacity, anti-cheat efficacy or universal best server strategy. Vendor pages inaccessible in this pass were excluded as evidence. No source licenses or unfamiliar executable provenance were assumed. Do not import another stack or upgrade upstream merely because an issue is closed. Second research phase requires owner decision.

## Current independent engineering blocker
Manual Actions run 38099569774 at source 211dd945 failed a Listener byte-comparison check after pinned source verification and patch application, before SDK setup. Helper tests: 0/12, NOT RUN. Windows line endings are a hypothesis, not established cause. Engineering corrections were paused when this research began; this report does not resolve the blocker.
