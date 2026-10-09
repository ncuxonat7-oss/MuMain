# Current confirmed state — 2026-10-09

## LAST CONFIRMED STATE

**Baseline Readiness:60% →60.5%(+0.5), model1.0; Evidence Confidence:MEDIUM. Critical RED blockers:2. NOT YET READY FOR MAJOR CUSTOMIZATION.**

Working MuMain→OpenMU→PostgreSQL→authentication→Dark Knight→Lorencia remains preserved. Previously confirmed warp/shop/kill/EXP/drop/level-up/STR/Small Shield/relog, party membership and ordinary item+100Zen trade are not to be repeated.

Latest successful milestone: run37959672391, head5a3cd675df6095995b2355bdd4368b1ac2260bd5, completedSUCCESS. OpenMU d067b3c plus patches/openmu-trade-money.patch compiled; TradeCancelRestoresMoneyAsync:1/1PASS. Actual native normal cancellation after item+100Zen offer, then BOTH clients restarted/relogged:14 scoped persisted assertionsPASS. Donor9999900→9999900; recipient9996100 unchanged; offered potion UUID511da101-0000-7bac-41a0-aad9f93fe7fd/quantity3 restored exactly to original owner/slot37. Item-ID union and baseline test0Dk unchanged. Native evidence fixed-23–26 is genuine.

The real Money defect was an ItemStorageAdapter that forwarded Items but not nonvirtual Money. Current patch unwraps to actual persisted storage for backup/refund; DataModel/schema/client/resources unchanged. The earlier virtual-Money patch failed generated clone compilation and is discarded; see lessons-learned.md. Disconnect/crash safety is not proven by normal cancellation.

## CURRENT UNFINISHED TASK / EXACT NEXT ACTION

No runtime/build is active. Gameplay control is idle; current workflow reuses verified server binary/cache and latest DB. Next shortest optional validation: ONE finite open-trade CLIENT DISCONNECT→refund→relog, reusing run37959672391 runtime and DB. Explain runtime cost before launching. Do not repeat completed trade, party invite or normal cancel tests. Review the finite plan/validator for that changed scenario before dispatch.

Then target confirmed seed/item metadata gaps with bulk checks; no broad research. A server/client build requires a specific source change or unrecoverable artifact loss, not a cache miss alone.

## KNOWN BLOCKERS / UNKNOWN

Critical standard-content RED: incomplete Crywolf and Illusion Temple lifecycles. Scoped RED: Hanzo/GM duplicate item anchors, absent Sphere4/5 entries,12 zero-sized Seed Sphere4/5 client entries. Unknown: interrupted trade/concurrency/crash, party shared EXP/leave, guild, representative skills/quests/crafting/events, wider rendering/AI and long-session stability. No permanent hosted service exists; CI processes stopped after saving DB.

## FILES / ARTIFACTS TO REUSE

- Server: OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8 + current patch; successful patched-openmu-runtime artifact11630698202/run37959672391. Private durable runtime libfile_e442fc7253b88191aee21b3a19a679ab. No rebuild required.
- NEWEST WORKING DB/evidence: gameplay-final artifact11630634143/run37959672391; private durable archive libfile_384c0829e2548191a69976943a31e85f. Retains core/ordinary-trade progress. Do not restore failed37954653808 or interrupted37881728154/37882579366 snapshots as working baseline.
- MuMain validated8d18a2b/run37813650810/artifact11567737809/423PASS unchanged. Data/fonts hashes and full backups in resource-registry.md.
- Reuse existing bulk272PASS/scalar7PASS and client-resource check; no export/rebuild needed. scripts/check-trade-snapshot.py supports scoped cancel assertions; score-baseline.py freezes owner weights. Audit/navigation/test-history route further work.

GitHub source/docs are canonical; private backup IDs/checksums preserve large runtime/DB evidence beyond CI retention. Never commit DB dumps, passwords, tokens or account hashes. GitHub connector writes previously403; owner-authorized browser upload fallback is documented. Credits/reset time are not visible to the agent; do not promise automatic balance warnings. Fresh-agent handoff: YES with this GitHub repository and the same owner's backup access.
