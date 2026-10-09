# Bulk configuration validation — confirmed run

2026-10-09. Existing latest gameplay database restored in a database-only Windows job. Working OpenMU/MuMain stack and saved source backup unchanged.

Run **37863153228**, job **113603471810**, workflow commit **926eef40d5431bbb104fd6594d7ced93ea5335e1**. Artifact **11587091295** (`baseline-config-evidence`), SHA256 `b952abed311e6f77cc9aa3ae1f5fbb43ca302b75e5f58b602200bf70e029accd`. ZIP 1,059,611 bytes. Source gameplay run37860870710; no builds, server/client launch or asset downloads. Seven-minute maximum; export/check/upload steps successful.

## Results

**47,417 rows across 89 nonempty exported tables. 272 declared primary-key/foreign-key checks PASS, zero FAIL. Three NOT_CHECKED constraints refer to config.ItemOption with no exported rows.** Export covers every config table plus data.Item. References checked against configuration targets only; account credentials not exported. This mostly confirms PostgreSQL structural integrity; it does not prove gameplay mechanics or complete MU content.

| Content present | Records |
|---|---:|
| GameMapDefinition | 73 |
| MonsterSpawnArea | 6330 |
| MonsterDefinition | 483 |
| EnterGate | 116 |
| ExitGate | 224 |
| WarpInfo | 39 |
| ItemDefinition | 690 |
| CharacterClass | 18 |
| Skill | 288 |
| QuestDefinition | 499 |
| ItemCrafting | 39 |
| DropItemGroup | 119 |

## Additional read-only scalar checks

| Check | Records | Violations |
|---|---:|---:|
| Spawn coordinate bounds | 6330 | 0 |
| Positive spawn quantity | 6330 | 0 |
| Enter gate coordinates | 116 | 0 |
| Exit gate coordinates | 224 | 0 |
| Nonnegative warp cost/level | 39 | 0 |
| Drop chance range | 119 | 0 |
| Positive item dimensions | 690 | 0 |

These seven checks were calculated locally from the same complete export, without another CI run. Coordinate checks use the standard 0..255 MU tile range, not collision/pathfinding or rectangle orientation. Positive dimensions do not validate item footprints against shop layout or client rendering.

## Known findings retained

- Hanzo Gladius/Falchion share slot73 in pinned upstream merchant seed.
- Test GM Ice/Fire pendants share slot9 in pinned upstream GM seed.
- Neither affects test0Dk inventory. No records deleted, relocated, or patched.

## Still unverified / next economical step

- Client-resource matching for all configured maps, items, monsters and skills; no all-assets compatibility claim.
- Runtime party/trade/guild, events, quests and crafting. The previously proven core loop remains valid; do not repeat it.
- Prepare a filename manifest from the exact approved resource archive and check it against these exported definitions locally. Reuse this export; no new database/CI run is needed for data inspection.
- Minimum two-client party/trade smoke can follow as a separate bounded session when practical; no new client builds.

Use scripts/check-config-references.py with extracted evidence to reproduce the 275 structural checks. Raw configuration export and complete report are kept in the preserved artifact; summarize findings in the repository. Existing baseline-content-audit.md is unchanged.
