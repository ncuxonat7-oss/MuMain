# Current state — canonical handoff

Updated 2026-10-09 UTC. Repository: ncuxonat7-oss/MuMain, main. Read this before running anything. GitHub is source of truth; Work scratch and CI runners are disposable.

## LAST CONFIRMED STATE

VERIFIED: native MuMain → pinned OpenMU → PostgreSQL17.11 → authentication → seeded test0/test0Dk → Lorencia. Existing Windows build passed423 tests. Normal warp/shop/purchase already verified. Core smoke is COMPLETE: real monster kills →115 EXP → natural level2 → normal Small Axe/Vine Gloves drops/pickup → three UI STR allocations28→31 → purchased Small Shield equipped offhand → client restart/relog → same character, stats and44 item UUIDs persisted. Latest seven persisted assertions PASS, run37860870710/artifact11585339277. Do not repeat this chain.

Last successful stage: existing config export mass-validated (272 structural checks,0FAIL,3NOT_CHECKED), then pinned client metadata/manifest cross-check and durable memory/readiness ledger. No new CI, builds or gameplay tests during this audit. Two native connections exist as prior evidence; party/trade interactions have NOT been verified.

Working client source/artifacts/server configuration were not modified. Processes are stopped; the successful environment was disposable Windows CI, not a currently hosted game service. New character creation UI is not proven; test character was seeded.

## CURRENT UNFINISHED TASK / EXACT NEXT ACTION

Next recommended bounded milestone: minimum two-client party/trade transaction and persisted-result check, reusing the existing native build and newest DB snapshot. Use existing workflows as starting points; inspect current inputs once, not CI internals. Confirm party membership, transfer one ordinary item/Zen, relog recipient, save logs/db and update readiness. Do not retest warp/shop/kill/STR/shield to position the clients. This may require one targeted runtime job; tell owner why before starting it. Not launched during this checkpoint because static audit already delivered substantial evidence at lower cost.

Known follow-up defects: Hanzo/GM duplicate stock anchors; missing Sphere4/5 client records;12 Seed Sphere4/5 zero-sized client entries. Diagnose/fix smallest affected metadata/seed scope with targeted validation; no new resource packs or stack replacement. Crywolf/Illusion Temple full standard lifecycle remains incomplete. Exile object and five model mappings remain uncertain, not proven runtime failures.

## CURRENT BASELINE READINESS

58%, MEDIUM evidence confidence, model1.0. First owner-weighted score; previous weighted score N/A. Legacy63.3% used a different presence-based rubric and is not comparable. Weighted criterion evidence:35% runtime,23% automatic,19% static,17% unknown,6% broken/missing. Two critical standard-content RED areas: Crywolf and Illusion Temple full lifecycle. No demonstrated fundamental connectivity/progression/persistence blocker. NOT YET READY FOR MAJOR CUSTOMIZATION. Ledger and exact acceptance criteria: baseline-readiness.json; readable matrix/history: baseline-content-audit.md.

## FILES / ARTIFACTS TO REUSE

Client run37813650810/artifact11567737809; frozen build8d18a2b, upstream21728b1e. OpenMU d067b3c; server cache openmu-windows-runtime-d067b3c-net10-v1. Resource package data-4b0ab29c58b27fc4. Newest persisted snapshot is gameplay-final, run37860870710, NOT earlier pre-shield snapshot. Complete config export run37863153228/artifact11587091295. Exact hashes, stable authorized-user backup IDs and restore instructions in resource-registry.md.

No passwords/tokens committed. DB dumps may contain fixture credential hashes; restore from authorized-user evidence backup, never push raw dumps. No permanent service credentials exist here. GitHub artifacts expire; backups are already preserved. Private backup access requires the same owner's connected file tools, not conversation history. External source/resource availability cannot be guaranteed indefinitely; source cache loss may require a targeted server build after explaining cost.

## CHECKPOINT / GUARDRAILS

Phase0 state checkpoint450b540a01edb94cc92a11aa13b3eba08f741561. The durable-memory milestone is the commit containing this file, audit, ledger, navigation and supporting docs/scripts; get exact hash from GitHub rather than embedding a self-referential future hash.

No broad research/imports/rebuilds. After two same failures reassess. Prefer references/bounds/metadata validators; source existence is not runtime verification. Update test-history/audit/ledger/current-state after meaningful milestones and commit+push. Owner credit balance is unavailable; warn before a costly new stage without promising automatic budget detection. No purchase/public deployment/production-changing action without explicit owner approval. See AGENTS.md for task-specific routing.
