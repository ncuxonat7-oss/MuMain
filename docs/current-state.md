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
