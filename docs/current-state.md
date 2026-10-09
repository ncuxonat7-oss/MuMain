# Current project checkpoint

This file is authoritative for active work; earlier run details belong in test-history.md. No credentials belong in this file.

## Work in progress

Owner requested durable project memory, standard-content audit refresh, and one permanent weighted customization-readiness model. Remaining minimum single-character chain is already VERIFIED; do not repeat it. Party/trade remain unverified and optional until a bounded test is practical. Current work is static client-resource cross-check and documentation/indexing; no new CI/runtime/build authorized as necessary by this stage.

Exact next unfinished action: retrieve the pinned Data tree filename inventory and compare actual exported item/map definitions, then publish the weighted score, concise handoff, and navigation index. Do not restart solved PostgreSQL17/export work. Existing gameplay and bulk artifacts below are authoritative.

Scoring: old audit 63.3% uses an older presence-based rubric. It is not the owner-requested weighted metric. Establish v1 transparently, preserve the old score as legacy, and do not present the model change as gameplay progress.

## Last completed bulk configuration run

User-authorized database-only run **37863153228**, job **113603471810**, workflow commit **926eef40d5431bbb104fd6594d7ced93ea5335e1**, completed successfully 2026-10-09 00:08 UTC. No duplicate run, builds, server/client start, repeated tests or asset download. Latest source backup restored read-only for export; original backup unchanged. PostgreSQL stopped cleanly.

Artifact **11587091295**, `baseline-config-evidence`, ZIP1,059,611 bytes, SHA256 `b952abed311e6f77cc9aa3ae1f5fbb43ca302b75e5f58b602200bf70e029accd`. Exported **47,417 rows / 89 nonempty tables**. **272 structural constraints PASS / zero FAIL / three NOT_CHECKED** for empty config.ItemOption. Full report in `docs/bulk-config-validation.md`. Seven supplementary scalar checks on the same export passed locally: spawn/gate coordinate bounds, positive spawn quantities, nonnegative warp costs/levels, drop chances0..1, positive item dimensions. No second CI was needed.

Presence counts: 73 maps, 6,330 spawn areas, 483 monster definitions, 690 item definitions, 288 skills, 499 quests, 39 crafting definitions. These counts and valid references are NOT evidence that every feature works in the client.

## Last successful milestone

Manual finite workflow `Finish Gameplay Smoke Test`, run **37860870710**, job **113596011554**, success. Workflow commit **52971f34461304a76587cfe3b6c694be239fc54d**. Reused validated client and server cache; no builds, no repeat of 423 tests, warp/shop/combat tests.

Actual client allocated three earned points: STR 28 → 31, equipped the purchased Small Shield, restarted and logged in again. Screenshots `05-relogin-level-experience-strength.png` and `06-relogin-equipped-shield.png` show Lorencia and saved state. Database independently confirms level 2, EXP 115, STR 31, remaining points 2, purchased shield UUID `801da101-0000-760d-a605-a410efe9185d` in offhand slot 1. All 44 original item UUIDs retained.

Latest recoverable database: run **37860870710**, artifact **11585339277**, `gameplay-final`, 11,495,834 bytes, SHA256 `bebf351e6a295dc15f9e47e9abe83aeb8653fbccbef401c2fcb8aa03bd137615`. Restore THIS latest artifact for further runtime work. Do not allocate STR again or restore older pre-equipment state.

## Bulk check and confirmed seed-data findings

Read-only snapshot validator captured 4,602 items, 118 stores, 1,117 attributes, 326 definitions, five selected characters. 13/14 checks passed; two duplicate anchor slots were traced to pinned OpenMU seed source, not our test0Dk gameplay:

- Hanzo storage `00001000-00fb-0000-0000-000000000000`, slot 73: Gladius and Falchion. Exact initializer: `src/Persistence/Initialization/Version075/MerchantStores.cs`, `CreateHanzoTheBlacksmith`, both `CreateWeapon(73, ...)` calls. This confirms a seeded shop-content collision. Do not delete records or patch stack yet; inspect item footprints and move to an available shop cell in an isolated future correction.
- Storage `511da101-0000-7ce5-cdf0-9a7bbb02e86e`, slot 9: Broy Pendant of Ice (group13 number25) plus Excellent Pendant of Fire (group13 number13). Exact initializer: `src/Persistence/Initialization/VersionSeasonSix/TestAccounts/GameMaster.cs`, two consecutive `InventoryConstants.PendantSlot` additions. This is a seeded GM-fixture collision; neither affects test0Dk inventory. Avoid using this GM fixture as equipment-validation evidence.

Pinned OpenMU commit d067b3c11c23c3145de6e2c76201ab9a93b267c8 source unchanged. No DB writes, client rebuilds, CI runs or resource imports during this follow-up.

## Prepared bulk configuration validator

`scripts/check-config-references.py` generates read-only repeatable-read SQL and validates exported primary keys and database-declared foreign keys pointing to configuration tables. Exports all config tables and data.Item only, not account credentials. Keep raw exports in private runtime evidence; publish summarized findings only.

```sh
python3 scripts/check-config-references.py --export-sql export-baseline-config.sql
# On already-restored PostgreSQL 17, from a private output directory:
psql -X -A -t -q -v ON_ERROR_STOP=1 -d openmu -f export-baseline-config.sql
python3 scripts/check-config-references.py --evidence PRIVATE_EXPORT_DIR --out PRIVATE_REPORT_DIR
```

Prepared checker verified on valid reference, missing target, and nullable-reference cases; SQL generated and checked against the embedded template. **Actual export and complete reference run are now confirmed by run37863153228.** Local existing pg_restore16 cannot read this pg_dump17 archive (format1.16). No repeated retry or fresh environment installation. The PostgreSQL17 workflow resolved this blocker; reuse its complete export for further local inspection.

Scope: structural references across exported configuration tables (maps/gates/spawns/shop definitions/items/skills where declared in schema), not full gameplay semantics or client model/texture availability. Client resource manifest matching remains unfinished. Previous baseline content audit retained; no inflated completion percentage. Party/trade still unverified.

## Exact next action

Economical next step: obtain only a filename manifest of the exact approved resource archive and match maps/items/monsters/skills against this preserved export. No more database or CI runs needed for static data inspection. Duplicate-slot seed origins confirmed; working stack/data left unchanged pending isolated layout/fixture corrections. Avoid per-item GUI testing. Minimum two-client party/trade smoke can follow as one bounded runtime session; two native client instances are previously confirmed, their interaction is not.

Do not rebuild/retest verified core. Existing stack/resources stay frozen. Do not broaden research or import resources. Before any costly CI/build/repeated session, explain necessity. Available Work credit balance is not visible; no automatic budget warning can be guaranteed. Save every milestone and exact next step here.

