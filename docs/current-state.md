# Current state — canonical handoff

Updated 2026-10-09 UTC. Repository: ncuxonat7-oss/MuMain, main. Read this before running anything. GitHub is source of truth; Work scratch and CI runners are disposable.

## LAST CONFIRMED STATE

VERIFIED: native MuMain → pinned OpenMU → PostgreSQL17.11 → authentication → seeded test0/test0Dk → Lorencia. Existing Windows build passed423 tests. Normal warp/shop/purchase already verified. Core smoke is COMPLETE: real monster kills →115 EXP → natural level2 → normal Small Axe/Vine Gloves drops/pickup → three UI STR allocations28→31 → purchased Small Shield equipped offhand → client restart/relog → same character, stats and44 item UUIDs persisted. Latest core seven persisted assertions PASS, run37860870710/artifact11585339277; run37879360808 additionally preserved these unchanged. Do not repeat this chain.

Last successful stage: existing config export mass-validated (272 structural checks,0FAIL,3NOT_CHECKED), then pinned client metadata/manifest cross-check and durable memory/readiness ledger. No builds or core test repeats during audit; one native party session and two finite trade attempts completed; only party earned additional readiness credit. Two native connections exist as prior evidence; party invitation/membership now verified; trade completion/persistence NOT verified.

Working client source/artifacts/server configuration were not modified. Processes are stopped; the successful environment was disposable Windows CI, not a currently hosted game service. New character creation UI is not proven; test character was seeded.

## CURRENT UNFINISHED TASK / EXACT NEXT ACTION

2026-10-09: party invite/accept and two member lists VERIFIED. Two finite trade attempts37881728154 and37882579366 both failed actual transfer assertions: trade grids empty, trade UI still open at capture14, donor-100Zen/recipient0 after teardown, original item remains donor. Both preserve core DK stats/items/IDs. Processes are stopped. No completed trade or multiplayer persistence is claimed. DO NOT restore these interrupted snapshots as the working baseline. Use clean pre-trade snapshot37879360808/artifact11594420323.

EXACT NEXT ACTION: stop repeating click-drag finite plans07/08. Inspect only the pinned inventory caller of CNewUITrade::ProcessMyInvenItemAutoMove; the validated8d18a2b source has a direct auto-move method and confirmation explicitly rejects a held item. Then stage one right-click auto-move item offer from the same clean DB, require a screenshot actually showing an item in the trade grid BEFORE confirmation, and reuse scripts/check-trade-snapshot.py. Native binding/held-item root cause is still UNKNOWN; do not assume the empty-grid state means an empty inventory cell was clicked. A claimed empty-cell explanation in the previous checkpoint was not established and is superseded. No input framework, build, party/warp/shop/combat repeat. Explain cost before any new Windows job. A separate interrupted-trade100Zen refund/teardown issue remains unresolved even if normal transfer later passes; examine this exact path, not Guild/SDL/CI internals. No owner laptop action is required to resume these scoped checks.

Known follow-up defects: Hanzo/GM duplicate stock anchors; missing Sphere4/5 client records;12 Seed Sphere4/5 zero-sized client entries. Diagnose/fix smallest affected metadata/seed scope with targeted validation; no new resource packs or stack replacement. Crywolf/Illusion Temple full standard lifecycle remains incomplete. Exile object and five model mappings remain uncertain, not proven runtime failures.

## CURRENT BASELINE READINESS

58.5%, MEDIUM evidence confidence, model1.0; previous58%, change+0.5 points for confirmed party membership only. Legacy63.3% used a different presence-based rubric and is not comparable. Weighted criterion evidence:35.5% runtime,23% automatic,18% static,17.5% unknown,6% broken/missing. Two critical standard-content RED areas: Crywolf and Illusion Temple full lifecycle. Core persisted progression remains verified; multiplayer transaction/interruption safety is unresolved and must not be declared safe. NOT YET READY FOR MAJOR CUSTOMIZATION. Ledger and exact acceptance criteria: baseline-readiness.json; readable matrix/history: baseline-content-audit.md.

## FILES / ARTIFACTS TO REUSE

Client run37813650810/artifact11567737809; frozen build8d18a2b, upstream21728b1e. OpenMU d067b3c; server cache openmu-windows-runtime-d067b3c-net10-v1. Resource package data-4b0ab29c58b27fc4. Newest persisted snapshot is gameplay-final run37879360808/artifact11594420323 (party fixture positioning; no trade completed); core shield progression remains from run37860870710. NOT earlier pre-shield snapshot. Complete config export run37863153228/artifact11587091295. Exact hashes, stable authorized-user backup IDs and restore instructions in resource-registry.md.

No passwords/tokens committed. DB dumps may contain fixture credential hashes; restore from authorized-user evidence backup, never push raw dumps. No permanent service credentials exist here. GitHub artifacts expire; backups are already preserved. Private backup access requires the same owner's connected file tools, not conversation history. External source/resource availability cannot be guaranteed indefinitely; source cache loss may require a targeted server build after explaining cost.

## CHECKPOINT / GUARDRAILS

Phase0 state checkpoint450b540a01edb94cc92a11aa13b3eba08f741561. The durable-memory milestone is the commit containing this file, audit, ledger, navigation and supporting docs/scripts; get exact hash from GitHub rather than embedding a self-referential future hash.

No broad research/imports/rebuilds. After two same failures reassess. Prefer references/bounds/metadata validators; source existence is not runtime verification. Update test-history/audit/ledger/current-state after meaningful milestones and commit+push. Owner credit balance is unavailable; warn before a costly new stage without promising automatic budget detection. No purchase/public deployment/production-changing action without explicit owner approval. See AGENTS.md for task-specific routing.
