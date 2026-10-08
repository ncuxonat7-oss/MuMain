# Current state — confirmed gameplay core and economical bulk validation

Updated 2026-10-08 23:49 UTC. Confirmed native Windows MuMain → pinned OpenMU → PostgreSQL → character → Lorencia.

## Last successful milestone

Manual finite workflow `Finish Gameplay Smoke Test`, run **37860870710**, job **113596011554**, success. Workflow commit **52971f34461304a76587cfe3b6c694be239fc54d**. Reused validated client and server cache; no builds, no repeat of 423 tests, warp/shop/combat tests.

Actual client allocated three earned points: STR 28 → 31, equipped the purchased Small Shield, restarted and logged in again. Screenshots `05-relogin-level-experience-strength.png` and `06-relogin-equipped-shield.png` show Lorencia and saved state. Database independently confirms level 2, EXP 115, STR 31, remaining points 2, purchased shield UUID `801da101-0000-760d-a605-a410efe9185d` in offhand slot 1. All 44 original item UUIDs retained.

Latest recoverable database: run **37860870710**, artifact **11585339277**, `gameplay-final`, 11,495,834 bytes, SHA256 `bebf351e6a295dc15f9e47e9abe83aeb8653fbccbef401c2fcb8aa03bd137615`. Restore THIS latest artifact for further runtime work. Do not allocate STR again or restore older pre-equipment state.

## Bulk check and current unresolved finding

Read-only reusable Python checker `scripts/check-baseline-snapshot.py` checked captured 4,602 items, 118 stores, 1,117 stat attributes, 326 attribute definitions, and five selected characters. 13 of 14 checks passed. Two duplicate occupied anchor-slot groups require triage: store `00001000-00fb-0000-0000-000000000000`, slot 73; store `511da101-0000-7ce5-cdf0-9a7bbb02e86e`, slot 9. Neither is test0Dk inventory. Do not automatically delete or relocate items: ownership/context and slot semantics need verification. Report contains exact item UUIDs in JSON.

This checks snapshot integrity, NOT all standard MU mechanics or a completion percentage. Maps/gates/spawns/shops/item definitions/drops/skills/quests and all client assets are not exported here. Previous `docs/baseline-content-audit.md` remains authoritative for static content evidence. Party/trade/guild/events/crafting remain runtime unverified.

## Exact next action

Economical next step: resolve the two duplicate-slot findings using existing definitions/snapshot, then add a read-only configuration/resource reference exporter and bulk validator for maps/gates/spawns/shops/items/skills. Avoid per-item GUI testing. Minimum two-client party/trade smoke can follow as one bounded runtime session; two native client instances are previously confirmed, their interaction is not.

Do not rebuild/retest verified core. Existing stack/resources stay frozen. Do not broaden research or import resources. Before any costly CI/build/repeated session, explain necessity. Available Work credit balance is not visible; no automatic budget warning can be guaranteed. Save every milestone and exact next step here.

## Preserved prior checkpoint and evidence

# Confirmed final gameplay checkpoint — 2026-10-09 Israel

Runtime session 4 ended successfully and all processes were cleaned up. Core gameplay smoke test is PARTIAL.

- Proven in the actual client: monster kills, real EXP and drop pickup (Small Axe, Vine Gloves), natural level 2, EXP 115/440, five earned stat points. Two real connected MuMain processes were also proven. No GM EXP/stat grants.
- Final persisted SQL: test0Dk Experience=115, LevelUpPoints=5, Level attribute=2, Strength=28, position Lorencia (117,140), inventory contains 44 items after normal healing-potion consumption and two drops. Purchased Small Shield ID 801da101-0000-760d-a605-a410efe9185d remains in inventory slot 47, durability 22.
- STR allocation, shield equipment and saved-progress client relog NOT executed. Party/trade NOT tested; guild deferred.
- Completed runtime: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37851961862 . Job 113566794117 success. Server build skipped from cache; validated client reused; no 423-test repeat.
- **Restore THIS latest backup:** artifact 11583409579, gameplay-final, 32,934,539 bytes; SHA256 d18505ba1e96558de56db7dbbbd9acc6ad9084f998ecdb98834d51c080f7db51. Local archive gameplay-session-4-final.zip; database dump 1,367,019 bytes. Existing workflow still restores run 3: change only the restore run-id to 37851961862 before the next runtime.
- Blocker: authorized GitHub browser write channel disconnected (exec-server transport disconnected); one recovery reset timed out. GitHub connector reads remain functional; earlier connector writes returned 403. No repeated retries/new builds. Latest level-2 docs edit and equip control were NOT committed. Remote docs/current-state.md still records 73 EXP. Preserve it and apply this newer checkpoint when write access resumes.
- **Exact next step:** existing test0Dk, natural Level 2 / 115 EXP / five points / STR 28 → click the normal STR plus exactly three times (character UI x989,y202) → STR31/two points → move purchased Small Shield from bag (x853,y465) to offhand (x967,y180) → verify actual item slot → restart client/login test0 → verify EXP, level, STR, points, equipped item and two real drops against saved database. Stop core smoke test only after this proof. Optional minimal party/trade afterwards; no new warp/shop tests.
- No laptop is needed. A functioning GitHub write/browser channel in Work is required. Current runtime is closed; use the saved backup and binaries instead of rebuilding. Available Work credits cannot be seen.

## Earlier evidence and checkpoints

# Current confirmed state

Updated 2026-10-08. Current task is **in progress**: normal gameplay loop, then two-client party/trade/guild. Confirmed Lorencia baseline remains valid. No application rebuild or repeat of the 423 client tests in this stage.

## Last successful step

On real MuMain → pinned OpenMU → PostgreSQL:

- Normal `test300Dk` warp **Lorencia → Noria (171,114) → Lorencia (142,132)**. Actual screenshots and welcome messages; no GM command for these transitions. Persisted Zen **10,000,000 → 9,996,000**, matching two 2,000-Zen warps.
- Normal `test0Dk`, **level 1, XP 0/100, STR 28**, walked to Hanzo and opened the real standard NPC shop at Lorencia (117,140).
- Purchased **Small Shield** for **230 Zen**: inventory **10,000,000 → 9,999,770**. Screenshot and final PostgreSQL snapshot confirm the new item and saved money/position. Item `801da101-0000-760d-a605-a410efe9185d`, definition `00000080-0006-0000-0000-000000000000`, inventory slot **47**, durability **22**.
- The shield requires **STR 31**; test0 has 28. It is bought but **not equipped**. Natural level-up and three stat points are required; do not grant XP/stats or claim equipment success yet.

## Frozen stack and existing artifacts

- OpenMU https://github.com/MUnique/OpenMU commit `d067b3c11c23c3145de6e2c76201ab9a93b267c8`, MIT; cached Windows Release runtime, .NET 10.
- MuMain fork https://github.com/ncuxonat7-oss/MuMain . Existing Windows x64 Release/editor-off build run **37813650810**, artifact **11567737809**; previously passed **423 tests**.
- Exact Main.exe SHA256 `9d895c638eb256b98d728dfc511f4c57d4a9e88cdba703e639426712b0b57cd5`; MUnique.Client.Library.dll SHA256 `9292041494d9226f105fc07a94c2451f6303b906123b2932ea05a3469c378cb7`.
- PostgreSQL **17.11**, ephemeral trusted localhost test instance. Connect port 44406, game endpoint 127.127.127.127:55902. No persistent/public hosting deployed.
- Same approved prototype Data/fonts release `sven-n/MuMain`, `data-4b0ab29c58b27fc4`, archive SHA256 `8c62a98aaabf13d80c24c0c688dbfafd4b23813966dd3a2f13c445c3a35e8d1d`. Commercial redistribution remains unresolved; exact provenance is in [resource-registry.md](resource-registry.md).
- Original confirmed Lorencia login: run **37830707804**, artifact **11573356702**, actual `06-world-attempt.png`. Preserve it; do not rebuild or retest merely to reconfirm it.

## Latest preserved database and evidence

Completed gameplay session **37846640006**: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37846640006 . It reached its planned 25-minute interactive limit and saved the database.

**Resume from this database**, not from new seed data:

- Artifact **11581801498**, `gameplay-final`, ZIP **28,263,120 bytes**.
- ZIP SHA256 `bbd677d82a858bf72a3fbf259a163fd482c54a34f53988c750d75e72745130f9`.
- Includes `gameplay-test-db.dump`, `final-database.jsonl`, real map/shop/purchase screenshots, logs and exact binary hashes.
- Purchase screenshot `25-after-small-shield-purchase.png`; shop `24-hanzo-shop-attempt.png`; normal warp `11-normal-warp-noria.png`, `12-normal-warp-return.png`; initial low-level stats `19-test0-level1-xp0.png`.
- Additional map artifact **11579958340**, purchase batch **11581871100**. Full final ZIP and purchase/Noria screenshots saved additionally as durable user deliverables. GitHub artifacts expire after 90 days.

## Current blocker and prepared correction

Combat/XP/drop/level/equip and changed-gameplay re-login are not verified yet. Party/trade/guild are not verified.

The second process failed because the test harness copied only root files plus Data/fonts and omitted **shaders**. Actual log: `client-two\shaders\basic_textured.vert.dxil` not found. This is a packaging defect in the harness, not an established GPU/driver limitation. The GM positioning attempt reported `Character test0Dk not found`; it did not move test0 because the second client had not logged in. Normal shop approach was completed with the first full client instead.

Prepared harness correction adds the existing `shaders` directory to the second client, checks the shader file before launch, throws on readiness timeout, tracks restarted client PIDs for cleanup, and restores the latest run-3 database. No application source, resources, game rules or XP/stat values changed. Next session uploads only new screenshots/snapshots per batch to reduce transfers. Current official upload-artifact v4 documentation supports 500 artifacts/job using the same @actions/artifact 2 SDK; harness is bounded to 25 command batches and 35 interactive minutes, stopping earlier with `finish`.

Earlier restore failure (run **37845483038**) was exactly 127 missing-role errors for standard PostgreSQL roles account/config/guild/friend. Fixed in commit `6a4a287055abfd6d5e2491a6c3998b5a94d616b9`: recreate those exact standard roles before restoring original grants, stop failed bootstrap processes, redirect child output to a file. Original first-session backup also remains preserved (run 37843108952, artifact 11580160294).

## Next action and checkpoint policy

Launch the corrected bounded continuation with the latest preserved database. Use existing seeded `testgm` and normal `test0` as two actual MuMain processes. Verify saved purchase, then use standard GM movement **only as a named positioning fixture** near normal Lorencia monster spawns; no XP/stat grants or fabricated drops. Fight, collect real XP/drop, naturally level, add three STR points, equip the purchased shield, and reconnect to verify saved progress. Then, only if practical, perform the minimum two-client party/trade test. Guild is deferred by the latest user scope.

Save significant success to this repository and update this file plus [gameplay-runtime-checks.md](gameplay-runtime-checks.md). Prior detailed baseline/reference audit is [baseline-content-audit.md](baseline-content-audit.md). Do not repeat builds/tests/research without a technical need. Notify before substantial new build/research/retry series. Available Work credit balance is not visible; automatic balance warnings cannot be promised.

## Active continuation checkpoint
Runtime session 4 dispatched: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37851961862 . Workflow correction commit ddb64812330bbdde66d4591af85c37fc90233857; control commit bd92e0ceaac0d1a4a6d98159cba50591a379a8fa. Latest confirmed gameplay is still the purchased shield; combat, XP/drop, natural level, STR allocation, equipment and saved-progress relog remain unverified. No client rebuild/retest. Stop cleanly with database dump and update this checkpoint if continuation cannot finish.

### Session 4 milestone: saved purchase and two connected clients
Artifact 11581969326 (`gameplay-combat-setup-01`) confirms test0Dk re-entered with the purchased Small Shield and Zen 9,999,770; unchanged XP/level were captured before combat. Both real MuMain processes are running and the character has been placed by the GM at Lorencia (200,130), with live monsters visible. This is an explicit positioning fixture, not a normal warp claim. Latest confirmed step: persistence of the shop purchase and two-client connection. Next unfinished step: actual monster kill and EXP/drop.

### Session 4 milestone: real kill, EXP and item drop
Artifact 11582392895 (`gameplay-combat-kill-02`), screenshots 29-first-combat and 30-combat-xp-level: Budge Dragon combat, “Obtained 22 Exp”, “Small Axe Obtained”, character level 1 EXP 22/100. Real dropped item was picked up with Space. No XP/stat grants. Latest success: kill + EXP + drop pickup. Next unfinished step: naturally reach level 2 (100 EXP), then allocate 3 STR, equip purchased Small Shield and relog. Character needs normal healing potions during continued combat.

### Latest combat checkpoint before the next result
Artifact 11582453969 (`gameplay-combat-safe-04`) proves another normal kill awarded 51 EXP and Vine Gloves was picked up. test0Dk now shows level 1, EXP 73/100, STR 28, HP 88/112, back safely at Lorencia (117,140). Healing potions were consumed normally. Next unfinished step: earn at least 27 additional EXP naturally, then add 3 STR, equip the already purchased shield and verify a relog. No new level or equipped-shield success is claimed yet.

### Session 4 milestone: natural level 2 confirmed
Artifact 11583028877 (`gameplay-combat-cluster-08`), 42-level-check-after-cluster.png: test0Dk level 2, EXP 115/440, 5 freely earned level-up points, STR 28, HP 107/114. Actual chat shows 27 EXP, “Congratulations, you are Level 2 now”, then 15 EXP. No XP/stat grants. GM was moved out of the combat area to stop attracting monsters; test0 fought the observed real group. Latest successful step: natural level-up. Next unfinished step: allocate exactly 3 earned STR points, equip purchased Small Shield, restart client and verify persisted EXP/level/stats/items; party/trade only if practical afterwards.

## Handoff: GitHub browser transport unavailable
At 2026-10-08 22:39 UTC, cua_repl disconnected while filling the pending gameplay control and current-state editors. A single recovery reset timed out after 300 seconds. No further browser retries. The STR/equip/relog command is prepared in gameplay-control.json but NOT verified committed or executed. Last verified remote control is combat-cluster-08 at fc674e095a218ecabc0a2e0e453dc41bdf34762a. Remote docs still confirm 73 EXP; this newer level-2 checkpoint could not be pushed. The active bounded runtime should finish automatically and preserve gameplay-final with a database dump; collect that from run 37851961862 before any new run.

Exact next unfinished action: restore the latest session-4 final dump using existing binaries/resources; verify current level 2 / EXP 115 / earned points 5 / STR 28, allocate 3 STR via normal character UI, equip purchased Small Shield from inventory slot 47 to offhand, restart client and verify persistent XP/level/STR/items. No warp/shop/build/test repeats. Party/trade is optional afterwards, guild deferred. No laptop action is needed; continuation requires a working authorized GitHub write/browser channel.
