# Current confirmed state — 2026-10-10

## LAST CONFIRMED STATE

New continuation: focused legacy quest decoder/crosswalk completed; all16Group0definitions MATCH explicitly compared NPC/item/monster-count/Zen fields. Exact200×744byte native file layout verified;14targetedbinary/semantic testsPASS. Full requirements/rewards/recipe semantics remain unresolved. See s6-legacy-quest-codex-handoff.md for scope/result;65.5unchanged.

Latest bounded audit: docs/s6-baseline-diff.md;7735partialsemanticMATCH,1380UNKNOWN;clientbinaryIDcrosswalk;noimport/fix/runtime;readiness65.5unchanged. See exact next action below.

Latest completed bulk/data checkpoint38005996341 SUCCESS54s: all22 shop grids/13 semantic checks PASS; all81 S6 update identities/versions current; all690 client item IDs/dimensions PASS with reviewed overlay. See bulk-baseline-validation.md. No runtime/build/import/trade work this milestone.

**Baseline Readiness:61% →61.5%(+0.5 owner scope only) →65.5%(+4 confirmed local fixes), model1.1; Evidence Confidence:MEDIUM. Current critical RED blockers:0; Crywolf deferred / Illusion Temple out of scope. NOT YET READY FOR MAJOR CUSTOMIZATION.**

Working MuMain→OpenMU→PostgreSQL→authentication→Dark Knight→Lorencia remains preserved. Previously confirmed warp/shop/kill/EXP/drop/level-up/STR/Small Shield/relog, party membership and ordinary item+100Zen trade are not to be repeated.

Latest successful gameplay milestone: run37996918917, headb0e1a816dc6c1e13f8be8a7edb3310df4176188b, SUCCESS7m17s. Reused verified MuMain/Data/OpenMU d067b3c + current Money patch and previous working DB; no rebuild. Native item+100Zen offer→donor process termination→recipient auto cancellation→both native relogs. Screenshots27–30 personally inspected;14 scoped persisted assertionsPASS. Donor9999900→9999900; recipient9996100 unchanged; potion UUID511da101-0000-7bac-41a0-aad9f93fe7fd/qty3/original owner/slot37 exactly restored; core test0Dk and scoped inventories preserved. Existing normal-cancel37959672391 and ordinary transfer remain verified. One disconnect criterion0→.5 adds only .5; audit adds no score.

The real Money defect was an ItemStorageAdapter that forwarded Items but not nonvirtual Money. Current patch unwraps to actual persisted storage for backup/refund; DataModel/schema/client/resources unchanged. The earlier virtual-Money patch failed generated clone compilation and is discarded; see lessons-learned.md. One donor-process disconnect is now proven; concurrency/hard server crash remain UNKNOWN. Owner explicitly considers trade sufficient for current baseline; no further trade edge cases unless a later specific defect.

## CURRENT UNFINISHED TASK / EXACT NEXT ACTION

Owner routing decision persisted in work-codex-routing.md and AGENTS.md. Current recipe/legacy-quest cross-system semantics investigation is WORK; localized decoder/validator implementation becomes CODEX PREFERRED after formats/mappings and acceptance are clear. Do not duplicate work or assume shared session context. Client optimization remains DEFERRED. This routing decision adds no readiness credit and changes no S6 priority.

S6 baseline diff and safe automation audit completed: docs/s6-baseline-diff.md + machine-readable diff/client-crosswalk; reusable scripts and pinned projections saved. 7,735 projected records all MATCH;1,380 current records UNKNOWN;84.86% selected-record adapter coverage is NOT overall S6 completeness. No confirmed missing mapped records, no new defect, no safe import candidate, no baseline mutation. Readiness65.5 unchanged; model1.1/MEDIUM/current critical RED0.

Exact next unfinished analysis (WORK): map all38scoped recipe variants, category/NPC dispatch, item ranges/levels/options/counts, costs/formulas and outcomes; include16legacyquests' remaining inherited levels, class-generation eligibility, prerequisites, item levels and rewards. Recipe preflight:35simple settings,16custom handlers,3handler-only,15MixIDs with multiple client variants. The binary-format gap for16legacydefinitions is CLOSED; do not decode it again. Localized mapper implementation becomes CODEX PREFERRED once each semantic rule and acceptance are clear. Compare preserved export only, dry-run findings; no external writes without owner approval. Full IDs-and-requirements criterion could earn+2.5 only after proof; current evidence earns0. No runtime/import/build dispatched.

Read-only CI38008949221 SUCCESS12s/artifact11652516455 extracted4exactclienttables fromnative8d18a2b;650skillslots,99recipeentries,915queststeps decoded. All38scopedrecipeIDs and Number/StartingNumber/RefuseNumber steps of483nonlegacyquests present.282skills named;6blank names UNKNOWNhandling, not missing implementation.16legacyquests remain separateformat. No repeat of previous bulk/update/item/shop/native/trade checks.

Owner scope: IT OUT OF SCOPE, Crywolf DEFERRED; no fixes/runtime now. Trade sufficient; no deeper tests. Future client performance/AFK/multi-window/FPS tasks are DEFERRED in docs/deferred-client-optimization.md. Future Client Modifiability / Extensibility Audit must assess clean feasibility/difficulty and prove gameplay timing/network invariance; these tasks affect no current priority or score.

## KNOWN BLOCKERS / UNKNOWN

Historical/deferred findings: Crywolf incomplete (late stage), Illusion Temple incomplete (OUT OF SCOPE). Current critical blocker list is empty by owner scope decision, not event fixes. Previous scoped RED resolved: Hanzo stock slot73→76 in newest persisted checkpoint; 14 socket item metadata corrections; GM duplicate absent in newest proven snapshot. Known current scoped RED:0; broader unknowns remain. Unknown: concurrency/hard server crash, party shared EXP/leave, guild, representative skills/quests/crafting/events, wider rendering/AI and long-session stability. No permanent hosted service exists; CI processes stopped after saving DB.

## FILES / ARTIFACTS TO REUSE

- NEWEST WORKING DB: baseline-data-final artifact11651520969/run38005996341, Hanzo fixed; archiveSHA256 b40fbdbdb5c3bd9630331e0b9cb3bc7c1860db041a928bb976555635e03f79ea; dumpSHA2560a4b0744cb9be77c8f53a6f4a73e729402d17382069ba93261d394cbadf19478. Private backup ID recorded in resource-registry.md. Only1 of4602 item rows changed(slot);42,815 config rows and all other item properties unchanged. Characters/stats/Money/guild hashes identical.
- EXACT CLIENT DATA: original pinned archive plus patches/client-socket-metadata.json applied with scripts/apply-client-overlay.py. Corrected Group12 SHA2561441360f93d80291659f63912022e0816125863acd0212ab4ec02fca33ebbb73. Future standard-gameplay.yml consumes newest DB and this overlay; do not dispatch idle gameplay. OpenMU initialization patch is prepared/tested against pinned075/S6 source; no runtime rebuild this milestone.

- Server: OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8 + current patch; successful patched-openmu-runtime artifact11630698202/run37959672391. Private durable runtime libfile_e442fc7253b88191aee21b3a19a679ab. No rebuild required.
- PREVIOUS proven runtime DB/evidence: gameplay-final artifact11647981651/run37996918917; private durable archive libfile_6e1c5002e01881919a8e9284aac71584; SHA25642c1372b158b1bbec16a1f571c3129f5976ef7e995e30a92d1ae1a907837e9ab. Previous proven11630634143/libfile_384c0829e2548191a69976943a31e85f remains fallback. Retains core/ordinary-trade progress. Do not restore failed37954653808 or interrupted37881728154/37882579366 snapshots as working baseline.
- MuMain validated8d18a2b/run37813650810/artifact11567737809/423PASS unchanged. Data/fonts hashes and full backups in resource-registry.md.
- Reuse existing bulk272PASS/scalar7PASS and client-resource check; no export/rebuild needed. scripts/check-trade-snapshot.py supports scoped cancel assertions; score-baseline.py freezes owner weights. Audit/navigation/test-history route further work.

GitHub source/docs are canonical; private backup IDs/checksums preserve large runtime/DB evidence beyond CI retention. Never commit DB dumps, passwords, tokens or account hashes. GitHub connector writes previously403; owner-authorized browser upload fallback is documented. Credits/reset time are not visible to the agent; do not promise automatic balance warnings. Fresh-agent handoff: YES with this GitHub repository and the same owner's backup access.

