# Current state — canonical handoff

Updated 2026-10-09 UTC. Repository: ncuxonat7-oss/MuMain, main. Read this before running anything. GitHub is source of truth; Work scratch and CI runners are disposable.

## LAST CONFIRMED STATE

VERIFIED: native MuMain → pinned OpenMU → PostgreSQL17.11 → authentication → seeded test0/test0Dk → Lorencia. Existing Windows build passed423 tests. Normal warp/shop/purchase already verified. Core smoke is COMPLETE: real monster kills →115 EXP → natural level2 → normal Small Axe/Vine Gloves drops/pickup → three UI STR allocations28→31 → purchased Small Shield equipped offhand → client restart/relog → same character, stats and44 item UUIDs persisted. Latest core seven persisted assertions PASS, run37860870710/artifact11585339277; run37879360808 additionally preserved these unchanged. Do not repeat this chain.

Last successful stage: native ordinary trade and recipient relog VERIFIED in run37947724161/artifact11624674487; all nine persisted-state assertions PASS. Party invite/accept/member lists were already verified. No client/server build,423-test rerun, core/warp/shop/party retest or new resources were needed.

Working client source/artifacts/server configuration were not modified. Processes are stopped; the successful environment was disposable Windows CI, not a currently hosted game service. New character creation UI is not proven; test character was seeded.

## CURRENT UNFINISHED TASK / EXACT NEXT ACTION

2026-10-09: minimum party/trade smoke COMPLETE within its scope. Native right-click auto-move placed the original three-unit potion in both trade grids (17/18);19 offered item+100Zen;20 shows closed trade and100Zen Obtained;21 recipient restarted/relogged with item and updated balance. Final9 assertions PASS: donor-100/recipient+100/Zen conserved; same item UUID transferred, quantity/options preserved; two-inventory item IDs conserved; core DK stats/items/character IDs unchanged. Final donorZen9999900, recipient9996100; potion UUID511da101-0000-700b-5de4-04671daf33bc now recipient storage511da101-0000-722a-a59a-01a8959f4b96, slot57, quantity3. Processes stopped after successful run.

EXACT NEXT UNFINISHED STEP: cancellation/refund and interruption safety.

2026-10-09 targeted preflight: STATICALLY CONFIRMED at OpenMU d067b3c: TradeAcceptAction.OpenTradeAsync snapshots items and Money via BackupItemStorage; BaseTradeAction.CancelTradeAsync restores Money and item slots; Player.DisconnectAsync awaits CloseTradeIfNeededAsync before teardown/save. Existing TradeTest.TradeCancelTestAsync checks state/view only, not a nonzero Zen refund or PostgreSQL relog. No server defect diagnosed and no readiness increase from source inspection. Prepared one cached native run for item+100Zen normal cancellation and both-client relog with zero-delta assertions, restoring successful37947724161. This does not prove hard server-crash rollback. Earlier interrupted drag attempts37881728154/37882579366 ended donor-100Zen/recipient0; successful normal trade does not explain or clear this. Inspect only pinned server trade cancellation/save/disconnect handling and existing targeted tests first; then the minimum normal-cancel/relog check if still needed. Reuse newest working snapshot37947724161/artifact11624674487. No successful trade/party/core repeat, no drag/input framework, no unrelated Guild/SDL/CI research. Existing check-trade-snapshot.py asserts a COMPLETED transfer, not zero-delta cancellation; use correct targeted assertions before launching cancellation. The existing standard-gameplay.yml still defaults to the OLD pre-trade37879360808 fixture with a completed-transfer validator; before cancellation testing update only its restore run-id to37947724161 and use cancellation-specific zero-delta assertions. Do not launch with idle/old validator expecting a completed transfer. Explain cost before a new runtime/build. No owner laptop action is required. Current control is idle; completed batches09/10 are in Git history and run artifacts.

Known follow-up defects: Hanzo/GM duplicate stock anchors; missing Sphere4/5 client records;12 Seed Sphere4/5 zero-sized client entries. Diagnose/fix smallest affected metadata/seed scope with targeted validation; no new resource packs or stack replacement. Crywolf/Illusion Temple full standard lifecycle remains incomplete. Exile object and five model mappings remain uncertain, not proven runtime failures.

## CURRENT BASELINE READINESS

60%, MEDIUM evidence confidence, model1.0; previous58.5%, change+1.5 for ordinary trade/relog and scoped transaction persistence. Party/trade/guild40%, Persistence70%; other scores unchanged. Coverage:37% runtime,23% automatic,17% static,17% unknown,6% broken/missing; weighted acceptance criteria, not all-mechanic coverage. Critical standard-contentRED2: Crywolf and Illusion Temple full lifecycle. Normal progression and completed trade persistence verified; cancellation/disconnect/crash safety unresolved. NOT YET READY FOR MAJOR CUSTOMIZATION. Exact ledger/history:baseline-readiness.json; matrix:baseline-content-audit.md. Legacy63.3 presence score not comparable.

## FILES / ARTIFACTS TO REUSE

Client run37813650810/artifact11567737809; frozen build8d18a2b, upstream21728b1e. OpenMU d067b3c; server cache openmu-windows-runtime-d067b3c-net10-v1. Resource package data-4b0ab29c58b27fc4. Newest WORKING persisted snapshot is gameplay-final run37947724161/artifact11624674487 (completed conserved trade and relog); core shield progression remains unchanged from run37860870710. Clean older pre-trade fixture37879360808 is retained for recovery, not the newest state. NOT earlier pre-shield snapshot. Complete config export run37863153228/artifact11587091295. Exact hashes, stable authorized-user backup IDs and restore instructions in resource-registry.md.

No passwords/tokens committed. DB dumps may contain fixture credential hashes; restore from authorized-user evidence backup, never push raw dumps. No permanent service credentials exist here. GitHub artifacts expire; backups are already preserved. Private backup access requires the same owner's connected file tools, not conversation history. External source/resource availability cannot be guaranteed indefinitely; source cache loss may require a targeted server build after explaining cost.

## CHECKPOINT / GUARDRAILS

Phase0 state checkpoint450b540a01edb94cc92a11aa13b3eba08f741561. The durable-memory milestone is the commit containing this file, audit, ledger, navigation and supporting docs/scripts; get exact hash from GitHub rather than embedding a self-referential future hash.

No broad research/imports/rebuilds. After two same failures reassess. Prefer references/bounds/metadata validators; source existence is not runtime verification. Update test-history/audit/ledger/current-state after meaningful milestones and commit+push. Owner credit balance is unavailable; warn before a costly new stage without promising automatic budget detection. No purchase/public deployment/production-changing action without explicit owner approval. See AGENTS.md for task-specific routing.

