# Test and evidence history

Dates UTC; this is evidence, not a conversation transcript. Latest state always overrides earlier fixture values. No tests were rerun for the durable-memory checkpoint.

| Evidence | VERIFIED result | Limit |
|---|---|---|
| Client build run37813650810, artifact11567737809 | Windows native x64 Release/editor OFF;423 tests passed | Client tests, not complete gameplay |
| Lorencia run37830707804, artifact11573356702 | Real MuMain→OpenMU→PG17.11, auth/character selection/DK/Lorencia;06-world-attempt.png | Seeded account/character; no new-character-creation UI proof |
| Gameplay run37846640006, artifact11581801498 | Normal test300Dk Lorencia↔Noria, saved4,000 Zen cost; normal test0Dk Hanzo purchase230 Zen | No all-map/shop coverage |
| Gameplay run37851961862, final artifact11583409579 | Two native connections; normal weak-monster combat;22 then51 then27/15 EXP, Small Axe/Vine Gloves pickup; natural level2,115 EXP,5 points | GM positioning fixture only; no XP/stat grants. Respawn, all skills and multiplayer interactions not proven |
| Finite smoke run37860870710, artifact11585339277 | Real UI STR28→31, purchased shield slot47→offhand1, restart/relog in Lorencia; level2/EXP115/points2/44 same item UUIDs persist | Seven persisted-state assertions; one DK scenario |
| Snapshot validator on same final evidence |4,602 item IDs/refs,118 stores,1,117 attributes,326 definitions,5 captured characters;13/14 checks pass | Two duplicate anchor-slot groups are true seed-data findings, not ignored |
| Bulk config run37863153228, artifact11587091295 |47,417 rows/89 nonempty tables;272 key/reference checks PASS;0 FAIL;3 NOT_CHECKED empty ItemOption;PG stopped | Declared structural constraints only; mostly PostgreSQL integrity, not mechanics |
| Same export, local scalar bounds | Seven checks pass: spawn/gate coordinates, quantities, warp cost/level, drop chance, item dimensions | No rectangle/pathfinding/probability distribution proof |
|2026-10-09 pinned client cross-check |690 server definitions vs949 client entries/889 model entries; full13,188-file manifest; shared models resolved;73 maps/68 numbers with aliases |2 missing item entries,12 zero dimension entries,5 unknown mappings; Exile object absent. No rendering/effect/binary proof |
|2026-10-09 navigation tool | Lorencia(116,141) resolves Hanzo251, exact spawn, definition and merchant storage | Read-only locator, not additional gameplay test |
|2026-10-09 runtime37879360808/artifact11593403578|Party invite/accept, two native member lists (07/08); trade request received (10)|No shared EXP/leave proof; trade transfer/relog still pending|
|Runtime37879360808 final artifact11594420323|Successful cache-only Windows session; final DB saved; baseline DK stats/items unchanged|15-minute live window ended before offer-06; no completed trade,0Zen deltas; trade validator correctly FAILS expected-transfer checks|

|Finite trade run37881728154/artifact11595121043|Native trade offer100Zen appeared; two clients restarted/captured; core DK unchanged; final9-assertion check FAIL|Empty item cell clicked; native trade UI still open; donor-100, recipient0, no item transfer. Interrupted-trade refund/teardown discrepancy UNKNOWN. Corrected33-step attempt next; not gameplay success.|

Screenshots05/06 of finite smoke are authentic native captures, not generated images. Restore newest run37860870710, not the pre-equipment run37851961862.

## NOT VERIFIED

Party shared EXP/leave; trade completion/guild interactions and transaction persistence; all seven classes/casting/buffs/master skills; quest/promotion cycle; Chaos mix outcomes; event entry/lifecycle/reward; all monster ID/render/AI/respawn mappings; sustained server stability; client resource textures/animations/audio; production hosting/security/licensing.

Earlier failures and workarounds are in lessons-learned.md. Current readiness scoring is in baseline-content-audit.md and baseline-readiness.json. Do not infer a PASS from an implementation/test name or a server/client resource count.
