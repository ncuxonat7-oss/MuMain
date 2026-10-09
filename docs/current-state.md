# Current confirmed state — 2026-10-09

## LAST CONFIRMED STATE

**Baseline Readiness:60.5% →61%(+0.5), model1.0; Evidence Confidence:MEDIUM. Critical RED blockers:2. NOT YET READY FOR MAJOR CUSTOMIZATION.**

Working MuMain→OpenMU→PostgreSQL→authentication→Dark Knight→Lorencia remains preserved. Previously confirmed warp/shop/kill/EXP/drop/level-up/STR/Small Shield/relog, party membership and ordinary item+100Zen trade are not to be repeated.

Latest successful milestone: run37996918917, headb0e1a816dc6c1e13f8be8a7edb3310df4176188b, SUCCESS7m17s. Reused verified MuMain/Data/OpenMU d067b3c + current Money patch and previous working DB; no rebuild. Native item+100Zen offer→donor process termination→recipient auto cancellation→both native relogs. Screenshots27–30 personally inspected;14 scoped persisted assertionsPASS. Donor9999900→9999900; recipient9996100 unchanged; potion UUID511da101-0000-7bac-41a0-aad9f93fe7fd/qty3/original owner/slot37 exactly restored; core test0Dk and scoped inventories preserved. Existing normal-cancel37959672391 and ordinary transfer remain verified. One disconnect criterion0→.5 adds only .5; audit adds no score.

The real Money defect was an ItemStorageAdapter that forwarded Items but not nonvirtual Money. Current patch unwraps to actual persisted storage for backup/refund; DataModel/schema/client/resources unchanged. The earlier virtual-Money patch failed generated clone compilation and is discarded; see lessons-learned.md. One donor-process disconnect is now proven; concurrency/hard server crash remain UNKNOWN. Owner explicitly considers trade sufficient for current baseline; no further trade edge cases unless a later specific defect.

## CURRENT UNFINISHED TASK / EXACT NEXT ACTION

No runtime/build is active. Gameplay control is idle; CI processes stopped after saving newest proven DB. Owner requested STOP after feasibility/mapping audit; it is complete in season6-reference-feasibility.md. NO imports, importer implementation or additional gameplay run.

SHIFT STRATEGY: breadth first across maps/gates/warps; monsters/spawns; NPCs/shops; items/sets; drops; skills; quests/events/crafting. Prefer pinned native configuration/update comparison and exact client semantic bulk validation; selective external adapter only for admitted, proven missing S6 records. Runtime only critical chains, real mismatches or insufficient static evidence. No further trade edge-case work absent a later defect; do not replay verified core/trade tests.

If owner resumes, shortest evidence-based step is read-only seven-category semantic/client validator on saved export and exact resources, including 81 installed-update identity comparison; not wholesale external import. Reference sample overlaps all68 baseline map numbers and483monster numbers but contains later-season IDs/custom stores/duplicate wave rows. Scoped Hanzo/GM and Sphere/SeedSphere defects remain priority. Full Crywolf/IT lifecycle needs implementation proof; data cannot substitute it.

## KNOWN BLOCKERS / UNKNOWN

Critical standard-content RED: incomplete Crywolf and Illusion Temple lifecycles. Scoped RED: Hanzo/GM duplicate item anchors, absent Sphere4/5 entries,12 zero-sized Seed Sphere4/5 client entries. Unknown: concurrency/hard server crash, party shared EXP/leave, guild, representative skills/quests/crafting/events, wider rendering/AI and long-session stability. No permanent hosted service exists; CI processes stopped after saving DB.

## FILES / ARTIFACTS TO REUSE

- Server: OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8 + current patch; successful patched-openmu-runtime artifact11630698202/run37959672391. Private durable runtime libfile_e442fc7253b88191aee21b3a19a679ab. No rebuild required.
- NEWEST WORKING DB/evidence: gameplay-final artifact11647981651/run37996918917; private durable archive libfile_6e1c5002e01881919a8e9284aac71584; SHA25642c1372b158b1bbec16a1f571c3129f5976ef7e995e30a92d1ae1a907837e9ab. Previous proven11630634143/libfile_384c0829e2548191a69976943a31e85f remains fallback. Retains core/ordinary-trade progress. Do not restore failed37954653808 or interrupted37881728154/37882579366 snapshots as working baseline.
- MuMain validated8d18a2b/run37813650810/artifact11567737809/423PASS unchanged. Data/fonts hashes and full backups in resource-registry.md.
- Reuse existing bulk272PASS/scalar7PASS and client-resource check; no export/rebuild needed. scripts/check-trade-snapshot.py supports scoped cancel assertions; score-baseline.py freezes owner weights. Audit/navigation/test-history route further work.

GitHub source/docs are canonical; private backup IDs/checksums preserve large runtime/DB evidence beyond CI retention. Never commit DB dumps, passwords, tokens or account hashes. GitHub connector writes previously403; owner-authorized browser upload fallback is documented. Credits/reset time are not visible to the agent; do not promise automatic balance warnings. Fresh-agent handoff: YES with this GitHub repository and the same owner's backup access.

