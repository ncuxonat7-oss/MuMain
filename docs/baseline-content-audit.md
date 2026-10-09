<!-- Latest evidence overrides historical milestone paragraphs below. -->

> Current owner scope and evidence2026-10-10 supersede historical readiness/RED conclusions below. Illusion Temple OUT OF SCOPE; Crywolf DEFERRED late stage: neither is a current blocker or penalty. Read baseline-scope.md and bulk-baseline-validation.md. Current readiness65.5%, criticalRED0; Hanzo and14 client socket metadata defects resolved; GM duplicate absent in newest proven snapshot. Historical rows retained for traceability.

# Standard MU baseline content audit

Updated2026-10-09. Exact stack: OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8; validated MuMain8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5/upstream21728b1e5b03e0763b38ef9e23f79645e0df7ad2; Data tree77f7830f542d106fc519c8821832d49a3dd8ae3a. Target: ordinary playable S6E3-oriented standard baseline, not every proprietary retail feature. Static audit used no new CI; later bounded runtime checks reused existing binaries. No stack modifications/imports/rebuilds.

GREEN means sufficiently confirmed for the stated scope, not universal proof. YELLOW means incomplete/uncertain. RED means specific missing/incompatible behavior/content. VERIFIED, AUTOMATICALLY VALIDATED, STATICALLY CONFIRMED, INFERRED and UNKNOWN remain separate.

## Evidence identifiers

- R1: Lorencia native run37830707804; R2: warp/shop37846640006; R3: combat/two connections37851961862; R4: finite STR/equipment/relog37860870710, seven persisted assertions.
- A1: baseline-config export37863153228,47,417 rows/89 nonempty tables;272 structural constraints PASS,0FAIL,3NOT_CHECKED empty ItemOption. Seven local scalar checks0violations. See bulk-config-validation.md and scripts/check-config-references.py. Referential integrity does not prove gameplay rules.
- A2: scripts/check-client-resources.py;690 server item definitions vs949 client JSON entries/889 model entries; complete nontruncated13,188-file pinned manifest;73 map records/68 numbers. Results client-resource-check.json. Actual ItemJsonFormat defaults and ItemDataHandler/ItemModelLoader shared-model resolver were checked.
- S1: preserved original pinned source/reference audit baseline-content-audit-legacy-2026-10-08.md. Its runtime/scoring observations are historical, superseded here. No repeated repository analysis.
- R5: party37879360808/artifact11593403578; R6: completed trade/relog37947724161/artifact11624674487, nine persisted assertionsPASS.
- Recovery/source provenance in resource-registry.md; chronological limits in test-history.md.

## Feature matrix

|Feature / subsystem|Server present|Client resources present|Runtime verified|Status|Known gap / incompatible|Required action|Evidence / provenance|
|---|---|---|---|---|---|---|---|
|Core connectivity/database|Exact pinned server and PG17.11|Existing native binary/shaders/bridge|Auth, seeded DK, real Lorencia|GREEN VERIFIED|New-character UI and production hosting not tested|Reuse artifacts|R1–R4; resource registry|
|Maps|73 definitions; bounds/references checked|Alias-aware core triplets found except Exile object|Lorencia/Noria|YELLOW AUTO + limited VERIFIED|World6/EncTerrain6.obj absent; Exile special-case intent UNKNOWN; texture/collision/all-map rendering UNKNOWN|Target only manifest exception first if relevant; do not walk all maps|A1/A2; pinned MapManager aliases|
|Gates/warps|Definitions/references/cost/level/coordinates checked|Core terrain alias presence; UI source STATIC|Lorencia↔Noria and Zen debit saved|YELLOW|All routes, terrain reachability and event gate rules UNKNOWN|Bulk logical route validator before runtime sampling|A1,R2|
|Monsters|483 definitions|Generic asset manifest exists; full ID→model/effect mapping UNKNOWN|Normal weak-monster kill|YELLOW|Other models/AI/skills/respawn UNKNOWN|Generate class/model mapping; sample only exceptions|A1,R3,S1|
|Spawns|6,330 definitions, references/coordinates pass|Maps mostly resolved; models not fully cross-mapped|Local combat spawns visible|YELLOW|Terrain walkability, density and timed respawns UNKNOWN|Bulk spawn→map/model audit|A1/A2,R3|
|NPCs|Definitions/spawn links present|Hanzo visible; all NPC animations/models UNKNOWN|Hanzo interaction|YELLOW|Complete NPC→shop/quest mapping unvalidated|Use generated lookup, check exceptional links|R2; query-baseline.py|
|Shops|118 stores; structural links valid|Hanzo purchase UI works|Normal230 Zen purchase persisted|RED scoped / otherwise YELLOW|Hanzo Gladius/Falchion anchor73 overlap; GM pendant anchor9 overlap|Correct initializer slot placement and validate seeded/current stores; no blind deletion|Snapshot validator13/14; Version075/MerchantStores.CreateHanzo and SeasonSix/TestAccounts/GameMaster|
|Items|690 server definitions, sizes/reference bounds pass|949 entries; most explicit/shared BMDs found|Normal drops/purchase/item retained|RED scoped / otherwise YELLOW|Sphere4/5 group12#73/#74 client entries absent; five model mappings UNKNOWN|Patch scoped metadata, diagnose five mapping exceptions without downloading packs|A1/A2; item resolver/defaults|
|Equipment/sets|Definitions/options/class requirements exist|Resolved configured BMD paths present; all animations/set effects UNKNOWN|STR requirement allocation and Small Shield offhand/relog|RED scoped / otherwise YELLOW|12 Seed Sphere4/5 group12#118–129 omitted sizes default0×0 vs server1×1; set/socket/excellent semantics untested|Fix metadata dimensions; targeted socket inventory check; avoid rechecking shield|A2,R4|
|Drops|Definitions/links and probability bounds validated|Small Axe/Vine Gloves render/pickup|Normal kills→drop→inventory/relog|YELLOW VERIFIED + AUTO|Rates by group/level/Zen distribution and rare/options/socket branches UNKNOWN|Analyze distribution invariants, bounded statistical test only if needed|A1,R3/R4|
|Classes|Seven base classes,18 progression definition rows|Source/UI/resources partly present|Dark Knight only|YELLOW|Other classes/evolutions not exercised|Class→skill/item/resource coverage first|S1,A1,R1–R4|
|Skills|288 definitions and structural references|Resource presence not fully linked to skill IDs/effects|Basic attack only; no complete casting proof|YELLOW STATIC/AUTO|Casting/buffs/master/tree/client effects UNKNOWN|Map supported packet/effect references and small representative test|S1,A1|
|Leveling/stats|Progression formulas/attributes present|UI works for exercised DK|Natural level2/5 points;STR31/2 remaining points saved|GREEN for basic DK / YELLOW across classes|Other classes/high-level/formulas/master progression UNKNOWN|Validate formula boundary cases, not repeated low-level grind|R3/R4,A1|
|Quests|499 definitions and references|Quest dialogs/source exist; resource/runtime coverage incomplete|None|YELLOW|Promotion/reward/requirements not end-to-end proven|Bulk prerequisites/rewards sanity; one representative cycle|A1/S1|
|Party|Handlers/config source present|Real native party lists on both clients|Invite/accept/two-member lists VERIFIED|YELLOW partially VERIFIED|Shared EXP/leave/relog behavior UNKNOWN|Shared EXP/leave remain optional next scope; do not repeat membership|run37879360808/artifact11593403578;07/08 screenshots|
|Trade|Pinned handlers + actual-storage Money patch|Native offer/cancel/confirmation|Ordinary transfer/relog; normal cancel and BOTH relogs|GREEN scoped / YELLOW safety|Disconnect/concurrency/crash UNKNOWN|One finite disconnect check with existing binaries|R6;37959672391/fixed23–26;14PASS;1 regressionPASS|
|Guild|Handlers and persistence source present|UI/resources source present|None|YELLOW|Creation/roles/member persistence UNKNOWN|Defer guild internals until actual block; later small transaction test|S1|
|Chaos Machine/crafting|39 recipes, links and numeric bounds partly checked|NPC/UI source present; all effects UNKNOWN|None|YELLOW|Success/failure/consumption/options/reset semantics UNKNOWN|Recipe ingredient/output bulk audit then one ordinary mix|A1/S1|
|Standard events|Blood Castle/Devil Square/Chaos Castle source/map definitions; other event definitions|Aliased core map triplets found, effects not runtime proof|None|RED Crywolf/Illusion Temple; YELLOW others|Pinned audit: complete specialized Crywolf/Illusion Temple lifecycle missing/incomplete; access maps alone cannot implement event|Explicitly define mandatory S6 event scope; targeted server implementation/verification only, not resource replacement|S1,A2|
|Persistence|PG config/player/inventory links valid|Native relog actual|Core progression/shield; conserved trade/itemUUID after recipient relog|GREEN exercised flows / YELLOW wider scope|Disconnect/guild/events/crash/load UNKNOWN|Preserve37959672391; targeted interruption only|R4,R6,A1|
|Stability/regression|423 client tests; server scoped evidence|Known working shaders/client binary|Finite sessions only|YELLOW|Long duration/load/crash replay not verified; earlier resource warnings scoped|Target regressions after specific changes; no full rebuild now|R1–R4,S1|

Sphere4/5 definitions have DropsFromMonsters=false and no live item instance in the saved snapshot; defects do not invalidate the proven ordinary-item loop. Five unresolved explicit model mappings:13:19 Weapon of Archangel,13:20 Wizard's Ring,14:162 Magic Backpack,14:163 Vault Expansion Certificate,14:169 Rage Fighter Character Card. UNKNOWN mapping is not a proven missing runtime render. SharedModels.json references were resolved before reporting absent files.

## STANDARD BASELINE READINESS FOR CUSTOMIZATION

Model1.0 is fixed by the owner's weighting. Machine-readable criteria/evidence/limits/history: baseline-readiness.json. Run `python scripts/score-baseline.py docs/baseline-readiness.json`. Each subsystem has five fixed acceptance criteria,20% each. Credit:1=adequately runtime/automatically verified;0.5=explicitly partial verified coverage;0=static/inferred/unknown/broken. Definition/resource presence alone earns zero. New evidence changes criteria credit only when uncertainty is actually reduced. Do not silently adjust weights/criteria to raise score; document old/new/impact and retain historical comparability.

|Subsystem|Weight|Evidence-based subsystem score|Weighted contribution|
|---|---:|---:|---:|
|Core client/server/database/connectivity|15%|100%|15|
|Maps/gates/warps|10%|70%|7|
|Monsters/spawns|10%|40%|4|
|Items/equipment/sets|10%|50%|5|
|Drops/basic economy|10%|80%|8|
|NPCs/shops|10%|40%|4|
|Classes/skills/stats/leveling|10%|60%|6|
|Quests/events/Chaos Machine/crafting|10%|20%|2|
|Party/trade/guild|5%|50%|2.5|
|Persistence/stability/regression|10%|70%|7|
|TOTAL|100%||60.5%|

Engineering estimate:60.5%, Evidence Confidence MEDIUM. Weighted acceptance-checklist coverage:37.5% runtime verified,23% automatically validated,17% static only,16.5% unknown,6% broken/missing. These percentages describe this fixed checklist's evidence scope, not a measured percentage of all MU mechanics. Structural checks score only structural acceptance criteria, not complete mechanic functionality. Two clients merely connecting earns prerequisite coverage, not party/trade PASS.

Native continuation37947724161: ordinary trade and actual recipient relog VERIFIED,9PASS; no builds. Party membership already VERIFIED. Shared EXP/leave, guild and disconnect/crash remain unverified. Normal cancel/refund and both-client relog now verified in37959672391.

### Readiness history

|Milestone|Previous → current|Reason / comparability|
|---|---|---|
|Legacy2026-10-08 audit|63.3% legacy|35.45/56;14 equally weighted S/C/A/R presence-oriented groups; excluded core. Preserved as historical record only|
|2026-10-09 owner model1.0 introduction|N/A →58%; delta N/A|Owner's10 subsystem weights;50 explicit criteria; reuses existing runtime/config evidence plus new pinned client cross-check. Not a gameplay regression from63.3%|
|2026-10-09 native party membership|58% →58.5% (+0.5)|Same model; partial invite/shared EXP/leave criterion earns0.5 for membership only|
|2026-10-09 completed trade/relog|58.5% →60% (+1.5)|Scoped trade and transaction persistence partial0.5 each; same model; no cancel/crash credit|

Critical RED areas:2 — Crywolf and Illusion Temple complete lifecycle. Normal cancellation Money defect was fixed and verified in37959672391. Other localized RED metadata/seed issues are listed in matrix and ledger. Core progression and completed trade are verified; interrupted-trade100Zen discrepancy remains unresolved, so general transaction safety is not cleared.

NOT YET READY FOR MAJOR CUSTOMIZATION. Required gate:readiness>=85%, confidence>=MEDIUM and no unresolved fundamental core/persistence/item/progression RED. Numerical threshold alone is insufficient.

## Existing reference gap analysis — no imports

|Reference / exact provenance|License/version|Gap reference value|Compatibility / effort|
|---|---|---|---|
|https://github.com/Yomalex/MuEmu at6b1e8af3e90155ca6fd1d003b9dae5c978f24186|Root MIT; S6 Korean plus mixed later content; asset rights separate|Compare standard XML/TXT definitions and event behavior; Crywolf fragment not proof of complete implementation|Different schemas/MySQL; moderate/high manual definition mapping, no drop-in use|
|https://github.com/sven-n/MuMain at21728b1e5b03e0763b38ef9e23f79645e0df7ad2 and exact maintainer Data release|S5.2-derived/S6E3 target; game content/source permission unresolved|Closest client ID/resource reference already used; not independent runtime validation|Exact frozen fit; cannot fill missing server event logic; no new import|
|https://github.com/Ignies/OpenMu-Client-Babylon|Partial S6E3 web client; license UNVERIFIED (root lookup404 is not proof of no license)|Inspect concept/resource mapping only|Converted assets/proxy, different client; high replacement effort, no advantage justifying migration|

No verified rights-cleared compatible package that fills the major server-content gaps was found in the previous narrow audit. Production candidate prices/provenance and rejected packs remain in resource-registry.md. Do not broaden research simply because some content is unverified.

## Shortest path

Core runtime chain already complete. Next bounded stage:one scoped open-trade client-disconnect/refund/relog validation with verified runtime; do not repeat verified party or completed trade. Then scoped seed/item metadata fixes with targeted checks, generate monster/skill/recipe cross-reference exceptions, and only sample runtime cases validators cannot resolve. Decide required event scope explicitly before implementing incomplete events. Preserve standard MU first; do not introduce custom systems now.

Continuation run37879360808 completed normally; trade request/accept/UI proven, transfer/persistence still UNKNOWN.15-minute harness window ended before offer packet; no score increase beyond party membership58.5%. Final DB comparator showed0Zen deltas, original potion ownership, unchanged baseline DK. Saved recovery pointers in resource-registry.md. Next finite trade-only plan avoids per-click GitHub handshakes; final transaction assertions are required for PASS.

### Failed finite trade checkpoint (2026-10-09)
Run37881728154/artifact11595121043 did not complete trade: actual windows remained open; expected transfer assertions failed, donor-100Zen/recipient0. Item placement was not achieved; wrong-cell input and timing were hypotheses, not established causes; interrupted-trade refund/persistence behavior remains UNKNOWN. Core DK unchanged. Readiness stays58.5%, MEDIUM; no new success credit. One specifically corrected finite attempt follows from clean pre-trade DB; no stack modification.

### Corrected finite attempt / recovery checkpoint (2026-10-09)
Run37882579366/artifact11594978877 consumed the corrected33 steps and focused20-second waits; no item transfer, no recipient Zen credit, trade UI remained open, final donor-100Zen. Nine-check overallFAIL, core DK unchanged. VERIFIED: offered100Zen appeared in recipient UI. UNKNOWN: item placement/held-item binding, normal completed trade, interrupted-trade refund/teardown persistence. This is a blocking YELLOW multiplayer uncertainty, not evidence of a diagnosed normal-trade server defect. Existing critical standard-contentRED count remains2 (Crywolf/Illusion Temple); multiplayer safety is not cleared. Next: pinned caller→direct auto-move→actual trade-grid screenshot→one transfer/relog, no further drag-loop attempts. Readiness58.5→58.5(+0), MEDIUM; unchanged weights/criteria/coverage.

### Completed ordinary trade / readiness milestone (2026-10-09)
VERIFIED run37947724161/artifact11624674487: item visible in both trade grids17/18; ordinary item+100Zen confirmation20; actual recipient client restart/relog21. AUTOMATICALLY VALIDATED: nine observed persisted assertionsPASS, same transferred itemUUID/quantity/options, Zen conserved, two-inventory ID union unchanged, baseline DK unchanged. No build/core/party retest.

|Feature/subsystem|Server present|Client present|Runtime verified|Status|Known gap/action|Evidence|
|---|---|---|---|---|---|---|
|Ordinary trade and relog|Yes, pinned|Yes; existing native auto-move|YES one item+100Zen|GREEN scoped normal flow|Cancel/refund/disconnect UNKNOWN; investigate earlier interrupted100Zen delta separately|37947724161,17–22,9PASS|
|Multiplayer persistence|Yes|Yes|YES scoped trade+recipient relog|YELLOW broader safety|No crash/load/cancel proof; not cleared by normal trade|Same itemUUID and conserved balances in final DB|

Readiness58.5%→60%(+1.5), model1.0 unchanged: trade transfer/cancel/relog=.5 because transfer/relog verified but cancellation untested; transaction persistence/duplication-loss=.5 for this one completed exchange, not generalized crash safety. ConfidenceMEDIUM. Scores:Core100,Maps70,Monsters40,Items50,Drops80,NPC40,Classes60,Quests/events/crafting20,Party/trade/guild40,Persistence70. Weighted evidenceRUNTIME37/AUTOMATIC23/STATIC17/UNKNOWN17/BROKEN6. Critical standard-contentRED2 unchanged. NOT YET READY FOR MAJOR CUSTOMIZATION. Next shortest stage: targeted trade cancellation/refund/relog investigation, using successful snapshot; do not repeat normal trade or drag emulation.


### Normal cancellation diagnostic (2026-10-09)
Run37954653808/artifact11627378814 FAIL. VERIFIED: native item+100Zen offer23, normal cancel24, both relogs25/26. AUTOMATIC: original offered item exactly restored, ownership IDs/core DK preserved. BROKEN: donor9999900→9999800, recipient9996100 unchanged;100Zen lost. Other strict differences (equipped durability, Current Ability) are outside offered-item rollback, not established persistence defects. Static root: ItemStorageAdapter forwards Items but lacks Money forwarding; base ItemStorage.Money is non-virtual. At this historical checkpoint no fix had been validated; resolved in the latest milestone below. New criticalRED for cancellation/persistence. Numerical score60%→60%(+0); previous normal-flow credit retained, no credit for diagnosis. ConfidenceMEDIUM; coverage runtime37/automatic23/static17/unknown15.5/broken7.5. Preserved working37947724161; failed37954653808 must not become restore baseline. Next minimum action: targeted Money forwarding patch + regression + one server rebuild/cancel-only runtime; no client rebuild or broad audit.


## Latest confirmed cancellation fix / readiness milestone — 2026-10-09

VERIFIED run37959672391/head5a3cd675df6095995b2355bdd4368b1ac2260bd5: existing MuMain and Data, patched pinned OpenMU, genuine native item+100Zen offer→normal cancel→both client restarts/relogs. Donor9999900 and recipient9996100 restored/unchanged; offered medium potion UUID511da101-0000-7bac-41a0-aad9f93fe7fd quantity3 originalslot37 restored exactly. AUTOMATICALLY VALIDATED:14 scoped assertionsPASS, all owned IDs/core DK preserved;1 targeted real-player Money cancellation regressionPASS. Equipment durability and mutable Current Ability on test trade actors are explicitly excluded from rollback comparison; offered item/full core state are not excluded. Source/compile identity and all evidence saved privately; no client build or423-test rerun.

Resolved critical Money RED: adapter Money did not forward to actual persisted inventory. Unwrap-based backup/refund patch, no schema/DataModel/client/resource change. First virtual-property candidate failed generated clone CS0266 and was replaced; failure recorded, no score credit for diagnosis/build alone.

Readiness **60%→60.5%(+0.5)**, model1.0 unchanged. Trade transfer/cancel/relog .5→1; Persistence multiplayer safety remains .5. Subsystems:Core100,Maps70,Monsters40,Items50,Drops80,NPC40,Classes60,Quests/events/crafting20,Party/trade/guild50,Persistence70. ConfidenceMEDIUM; weighted checklist evidence runtime37.5/automatic23/static17/unknown16.5/broken6. Critical RED **2**, localized RED4 unchanged. NOT YET READY FOR MAJOR CUSTOMIZATION. UNKNOWN interruption/concurrency/crash cannot be inferred from normal cancellation. Shortest next milestone:single finite client-disconnect/refund/relog on the verified server, then scoped metadata fixes. No further runtime launched for this checkpoint.

