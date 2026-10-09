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

|Finite trade run37881728154/artifact11595121043|Native trade offer100Zen appeared; two clients restarted/captured; core DK unchanged; final9-assertion check FAIL|No item appeared in trade grid; empty-cell diagnosis was not established; native trade UI still open; donor-100, recipient0, no item transfer. Interrupted-trade refund/teardown discrepancy UNKNOWN. Corrected33-step attempt next; not gameplay success.|

|Corrected trade37882579366/artifact11594978877|33-step plan consumed (item cell792:428,20-second focused pauses); both clients captured/restarted; core DK unchanged|Trade UI/grid still incomplete; nine-assertion overallFAIL; donor-100Zen/recipient0; original UUID stayed donor. No successful transfer. Stop repeated drag plans; direct auto-move is next targeted candidate.|

|Trade37947724161/artifact11624674487|Direct native item offer visible in both clients17/18; item+100Zen confirmed;20 shows100Zen Obtained;21 recipient relog; final9 assertionsPASS|One ordinary item/Zen exchange between GM400 and normal300 fixtures. Same potionUUID/quantity3 transferred, all two-inventory IDs conserved, core DK unchanged. Cancel/disconnect safety and guild/shared EXP not tested.|

Screenshots05/06 of finite smoke are authentic native captures, not generated images. Restore newest successful run37959672391 (which retains core run37860870710), not interrupted37881728154/37882579366 or pre-equipment37851961862.

## NOT VERIFIED

Party shared EXP/leave; guild interactions, trade cancel/disconnect/crash safety and general multiplayer transaction stability; all seven classes/casting/buffs/master skills; quest/promotion cycle; Chaos mix outcomes; event entry/lifecycle/reward; all monster ID/render/AI/respawn mappings; sustained server stability; client resource textures/animations/audio; production hosting/security/licensing.

Earlier failures and workarounds are in lessons-learned.md. Current readiness scoring is in baseline-content-audit.md and baseline-readiness.json. Do not infer a PASS from an implementation/test name or a server/client resource count.


### Normal cancellation diagnostic37954653808 — FAILED
One cached native run, restored successful37947724161, no build/repeated successful gameplay tests. Artifact11627378814;23 item+100Zen offered,24 native cancelled,25/26 both clients restarted/relogged. Donor9999900→9999800; recipient9996100 unchanged. Offered medium potion UUID511da101-0000-7bac-41a0-aad9f93fe7fd exactly restored, all ownership IDs conserved, baseline DK unchanged.13 strict checks9PASS/4FAIL: money loss is confirmed; the other differences are two equipped durabilities and recipient Current Ability, not diagnosed as rollback defects. Run overallFAIL; native harness completed normally. Root diagnosis static: adapter forwards Items but not Money. No fix validated. Never promote failed DB over37947724161. Readiness60→60, MEDIUM, criticalRED3.


## Latest confirmed cancellation fix / readiness milestone — 2026-10-09

VERIFIED run37959672391/head5a3cd675df6095995b2355bdd4368b1ac2260bd5: existing MuMain and Data, patched pinned OpenMU, genuine native item+100Zen offer→normal cancel→both client restarts/relogs. Donor9999900 and recipient9996100 restored/unchanged; offered medium potion UUID511da101-0000-7bac-41a0-aad9f93fe7fd quantity3 originalslot37 restored exactly. AUTOMATICALLY VALIDATED:14 scoped assertionsPASS, all owned IDs/core DK preserved;1 targeted real-player Money cancellation regressionPASS. Equipment durability and mutable Current Ability on test trade actors are explicitly excluded from rollback comparison; offered item/full core state are not excluded. Source/compile identity and all evidence saved privately; no client build or423-test rerun.

Resolved critical Money RED: adapter Money did not forward to actual persisted inventory. Unwrap-based backup/refund patch, no schema/DataModel/client/resource change. First virtual-property candidate failed generated clone CS0266 and was replaced; failure recorded, no score credit for diagnosis/build alone.

Readiness **60%→60.5%(+0.5)**, model1.0 unchanged. Trade transfer/cancel/relog .5→1; Persistence multiplayer safety remains .5. Subsystems:Core100,Maps70,Monsters40,Items50,Drops80,NPC40,Classes60,Quests/events/crafting20,Party/trade/guild50,Persistence70. ConfidenceMEDIUM; weighted checklist evidence runtime37.5/automatic23/static17/unknown16.5/broken6. Critical RED **2**, localized RED4 unchanged. NOT YET READY FOR MAJOR CUSTOMIZATION. UNKNOWN interruption/concurrency/crash cannot be inferred from normal cancellation. Shortest next milestone:single finite client-disconnect/refund/relog on the verified server, then scoped metadata fixes. No further runtime launched for this checkpoint.


## 2026-10-09 — prepared disconnect completed; broad-baseline audit stop

Run37996918917, headb0e1a816dc6c1e13f8be8a7edb3310df4176188b, SUCCESS7m17s. Reused verified MuMain/Data/patchedOpenMU and previous workingDB; no rebuild. Actual donor item+100Zen offer (27), donor process termination/restart (no UI cancel), recipient automatic cancellation (28), both native relogs (29/30). Personally inspected screenshots;14 scoped saved-state assertionsPASS. Offered potion UUID511da101-0000-7bac-41a0-aad9f93fe7fd/qty3/slot37 restored exactly; donor9999900 andrecipient9996100 unchanged; coretest0Dk preserved. CurrentAbility regeneration/other equipped wear excluded as in existing validator; offered item and core remain strict. Artifact11647981651 is NEWEST WORKING DB/evidence. Hard server crash/concurrency remain unknown.

Readiness60.5→61(+.5) for partial disconnect criterion only; weights unchanged,MEDIUM,2criticalRED. Owner: trade sufficient for current baseline; no more trade edge cases unless a specific later defect. New strategy breadth via data-driven seven-category audit. season6-reference-feasibility.md contains exact pin mapping, measured overlap, risks and fastest path. No import/adapter implementation/content runtime tests performed. Stop after this audit; no next job dispatched.


## 2026-10-10 broad bulk/data checkpoint

- Owner scope model1.1: IT out of scope, Crywolf deferred, no current blocker/penalty. 61→61.5 scope only; archived1.0 unchanged.
- run38005996341/head7723123f81daaf655fbf99f9faa94cdf7f71518c SUCCESS54s, data-only PostgreSQL17; no server/client/build/trade. Restored newest37996918917 dump, guarded Hanzo Falchion73→76, repeated SQL idempotently,13 checks +all22 stock grids PASS.
- Latest snapshot comparison:4602 item records, exactly1 ItemSlot changed;42,815 config rows identical; character/stat/storage-money/guild hashes unchanged. Old GM duplicate absent in newest snapshot.
- All81 installed S6 updates match147 pinned source files/current versions; no updates rerun/imported.
-14 client socket metadata corrections guarded by exact hashes;690/690 IDs/dimensions PASS; repeat idempotence and wrong-hash rejection PASS. Five special model mappings and Exile world object remainUNKNOWN, no render/runtime claim.
- Readiness61.5→65.5 from two criteria0→1(+2 each); no score from source presence, update installation or replayed evidence. Coverage buckets reconciled from actual criteria without score gain.
