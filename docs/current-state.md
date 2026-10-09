# Current state — canonical handoff

Updated 2026-10-09 UTC. Repository: ncuxonat7-oss/MuMain, main. Read this before running anything. GitHub is source of truth; Work scratch and CI runners are disposable.

## LAST CONFIRMED STATE

VERIFIED: native MuMain → pinned OpenMU → PostgreSQL17.11 → authentication → seeded test0/test0Dk → Lorencia. Existing Windows build passed423 tests. Normal warp/shop/purchase already verified. Core smoke is COMPLETE: real monster kills →115 EXP → natural level2 → normal Small Axe/Vine Gloves drops/pickup → three UI STR allocations28→31 → purchased Small Shield equipped offhand → client restart/relog → same character, stats and44 item UUIDs persisted. Latest core seven persisted assertions PASS, run37860870710/artifact11585339277; run37879360808 additionally preserved these unchanged. Do not repeat this chain.

Last successful stage: existing config export mass-validated (272 structural checks,0FAIL,3NOT_CHECKED), then pinned client metadata/manifest cross-check and durable memory/readiness ledger. No builds or core test repeats during audit; one subsequent bounded native party/trade runtime completed. Two native connections exist as prior evidence; party invitation/membership now verified; trade completion/persistence NOT verified.

Working client source/artifacts/server configuration were not modified. Processes are stopped; the successful environment was disposable Windows CI, not a currently hosted game service. New character creation UI is not proven; test character was seeded.

## CURRENT UNFINISHED TASK / EXACT NEXT ACTION

2026-10-09: party membership remains VERIFIED, readiness58.5% MEDIUM. Finite trade run37881728154 completed its native actions but failed final assertions. Artifact11595121043 proves the trade windows were still open, item never offered (empty cell clicked), donor lost100Zen in the interrupted teardown, recipient gained0, original potion remained donor; baseline DK stats/items unchanged. Do NOT count this as completed trade or use its interrupted DB as the working baseline. Exact next action: one corrected finite33-step trade-corrected-finite-08, restoring the clean pre-trade DB run37879360808, selecting the visually confirmed potion cell792:428 and waiting20seconds after offering/another20before recipient confirmation. No party/warp/shop/combat retest or build. The100Zen interruption discrepancy remains UNKNOWN pending targeted confirmation; if corrected native confirmation fails, stop repeating the approach and checkpoint.


Next recommended bounded milestone: minimum two-client party/trade transaction and persisted-result check, reusing the existing native build and newest DB snapshot. Use existing workflows as starting points; inspect current inputs once, not CI internals. Confirm party membership, transfer one ordinary item/Zen, relog recipient, save logs/db and update readiness. Do not retest warp/shop/kill/STR/shield to position the clients. This may require one targeted runtime job; tell owner why before starting it. Next launch is a finite33-step trade-only continuation, no repeated party/warp/shop/combat tests. Existing workflow will validate the final DB automatically; no intermediate owner/agent input packets are needed. No new client/server build allowed.

Known follow-up defects: Hanzo/GM duplicate stock anchors; missing Sphere4/5 client records;12 Seed Sphere4/5 zero-sized client entries. Diagnose/fix smallest affected metadata/seed scope with targeted validation; no new resource packs or stack replacement. Crywolf/Illusion Temple full standard lifecycle remains incomplete. Exile object and five model mappings remain uncertain, not proven runtime failures.

## CURRENT BASELINE READINESS

58.5%, MEDIUM evidence confidence, model1.0; previous58%, change+0.5 points for confirmed party membership only. Legacy63.3% used a different presence-based rubric and is not comparable. Weighted criterion evidence:35.5% runtime,23% automatic,18% static,17.5% unknown,6% broken/missing. Two critical standard-content RED areas: Crywolf and Illusion Temple full lifecycle. No demonstrated fundamental connectivity/progression/persistence blocker. NOT YET READY FOR MAJOR CUSTOMIZATION. Ledger and exact acceptance criteria: baseline-readiness.json; readable matrix/history: baseline-content-audit.md.

## FILES / ARTIFACTS TO REUSE

Client run37813650810/artifact11567737809; frozen build8d18a2b, upstream21728b1e. OpenMU d067b3c; server cache openmu-windows-runtime-d067b3c-net10-v1. Resource package data-4b0ab29c58b27fc4. Newest persisted snapshot is gameplay-final run37879360808/artifact11594420323 (party fixture positioning; no trade completed); core shield progression remains from run37860870710. NOT earlier pre-shield snapshot. Complete config export run37863153228/artifact11587091295. Exact hashes, stable authorized-user backup IDs and restore instructions in resource-registry.md.

No passwords/tokens committed. DB dumps may contain fixture credential hashes; restore from authorized-user evidence backup, never push raw dumps. No permanent service credentials exist here. GitHub artifacts expire; backups are already preserved. Private backup access requires the same owner's connected file tools, not conversation history. External source/resource availability cannot be guaranteed indefinitely; source cache loss may require a targeted server build after explaining cost.

## CHECKPOINT / GUARDRAILS

Phase0 state checkpoint450b540a01edb94cc92a11aa13b3eba08f741561. The durable-memory milestone is the commit containing this file, audit, ledger, navigation and supporting docs/scripts; get exact hash from GitHub rather than embedding a self-referential future hash.

No broad research/imports/rebuilds. After two same failures reassess. Prefer references/bounds/metadata validators; source existence is not runtime verification. Update test-history/audit/ledger/current-state after meaningful milestones and commit+push. Owner credit balance is unavailable; warn before a costly new stage without promising automatic budget detection. No purchase/public deployment/production-changing action without explicit owner approval. See AGENTS.md for task-specific routing.
