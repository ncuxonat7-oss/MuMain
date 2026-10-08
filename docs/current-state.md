# Current confirmed state

Updated: 2026-10-08. Goal completed: real MuMain login into Lorencia on our OpenMU with PostgreSQL.

## Last successful step

Authenticated as disposable seeded account `test0`, selected Dark Knight `test0Dk`, entered **Lorencia (149, 123)**. Authentic `06-world-attempt.png` displays “Welcome to Lorencia” and “test0Dk entered the game.” Client log records `Character selected: slot 1` and `Main Scene init success` at 19:18:58 UTC. Screenshot inspected on 2026-10-08; success is based on actual client output, not merely a green workflow.

## Confirmed components

- OpenMU source: https://github.com/MUnique/OpenMU, commit `d067b3c11c23c3145de6e2c76201ab9a93b267c8`, MIT; Windows .NET 10 runtime, cached server build.
- PostgreSQL **17.11**, real local database; initialization created 20 disposable test accounts and 76 characters, including the character used above.
- Existing MuMain Windows x64 Release build (editor off), previously passed **423 tests**. No client rebuild or repeat tests for this runtime check. Build run: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37813650810 ; artifact `11567737809`.
- Exact reused `Main.exe` SHA256: `9d895c638eb256b98d728dfc511f4c57d4a9e88cdba703e639426712b0b57cd5`.
- Exact reused `MUnique.Client.Library.dll` SHA256: `9292041494d9226f105fc07a94c2451f6303b906123b2932ea05a3469c378cb7`.
- SDL Direct3D 12 rendering on Windows CI. Connect server port 44406; actual game connection `127.127.127.127:55902`. Evidence includes client/server connection endpoints and server database connections to localhost:5432.
- Assets/fonts: upstream release `data-4b0ab29c58b27fc4`, checked archive checksum. Exact source/trees and prototype authorization are recorded in [resource-registry.md](resource-registry.md). Prototype authorization does not grant commercial redistribution rights.

## Reproducible evidence

- Workflow: [.github/workflows/lorencia-runtime.yml](../.github/workflows/lorencia-runtime.yml), manual dispatch only.
- Successful runtime run: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37830707804
- Runtime workflow commit: `3b7088f1ca44e056dea5169435dbc4959d3e39b1`.
- Artifact: `lorencia-runtime-probe`, ID **11573356702**, ZIP size 8,962,127 bytes.
- Downloaded ZIP SHA256 verified: `1dd7ffe7478abe7686682928f1b18ef8fc68c7532e5e9a9b385c2ba2bd7a92d7`.
- Evidence files: `06-world-attempt.png`, `05b-selected-knight.png`, `client-MuError.log`, `client-binary-hashes.txt`, `connections.json`, `database-version.txt`, `database-counts.txt`, `resources.txt`, server logs and earlier UI screenshots.
- GitHub artifact expires 2027-01-06. Original ZIP and final screenshot are additionally saved as user deliverables; do not rely on transient Work paths for recovery.

## Current blocker

**None for the requested Lorencia end-to-end prototype.** Correct UI selection resolved the previous character-selection click issue. Missing models for other maps remain in logs; they did not prevent this Lorencia login. This result does not validate other maps, gameplay, or production distribution.

## Runtime lifecycle and next action

This was a real but ephemeral Windows GitHub Actions session. Workflow cleanup stopped client, server and PostgreSQL after evidence collection. No persistent public server or hosting was deployed. The disposable database is recreated from OpenMU initialization on each test run.

**Stop: requested stage is complete.** Preserve existing commits, client artifact, cached server and evidence. Do not rerun builds/tests/CI merely to reconfirm this result. Future hosting or broader tests require a separate user request. Before any substantial new build/research/retry series, explain its concrete necessity. Available Work credit balance is not visible to the agent.

## Latest completed stage — Baseline + Reference Gap Audit (2026-10-08)

[baseline-content-audit.md](baseline-content-audit.md) audits the exact unchanged server/client/Data baseline. Static content is extensive: 73 map initializer entries / 68 distinct map IDs, 949 client item entries, 889 model records with no missing explicit BMD paths, 128 active weapon and 22 shield IDs cross-matched, 40 warp entries, 35 recipe attachments. These are source/inventory counts, not runtime success.

Last successful step: completed read-only content/reference audit; no builds, CI dispatches, new runtime tests, code/resource imports or stack changes. Existing Lorencia E2E evidence remains valid. Three bounded references: MuEmu, exact MuMain source/assets, Babylon client README; no imports.

Current completeness blocker: most gameplay has no runtime proof; full Crywolf and Illusion Temple server lifecycles were not found. RED labels are standard-content gaps, not a fundamental stack dead end. Estimated evidence readiness 63.3% (judgment range 55–75%); this is not measured playable/test coverage.

Next recommended action: a bounded existing-binary single-character loop (gate, merchant, kill, XP, pickup/equip, level/stats, relog with the same DB), then two-client party/trade/guild. Not executed. Stop after audit; wait for the next user task. Notify before substantial new builds/research/retry series.


## Active stage — Standard gameplay runtime validation (2026-10-08)

User authorized the bounded single-character gameplay loop followed by real two-client party/trade/guild checks. Previous stop-after-audit instruction is superseded by this explicit task.

Last successful step: committed `.github/workflows/standard-gameplay.yml` at `8d3cc2dfba516bc0a4cbcca448988dd890ed25c8` and initial `.github/gameplay-control.json` at `2305f706b1bcf6333ff934e317b56e167371ab34`. No application source, resources or game definitions changed. Existing client build and pinned server cache are reused.

Runtime run dispatched once: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37843108952 . Its harness accepts a bounded allowlist of native GUI actions, uploads authentic screenshots and read-only SQL snapshots between batches, and saves a PostgreSQL dump at cleanup. No experience/stat grants are used. Low-level test0Dk is reserved for combat/leveling; seeded level-11 test1Dk can meet normal map-warp level requirements.

Current blocker: gameplay results are not yet verified. Next action: inspect the ready-world screenshot, issue observed GUI actions, compare client UI and database state; then test a second real client. A workflow status alone is not feature proof. Available Work credit balance is not visible.

### Gameplay session 1 checkpoint

Run 37843108952 finished successfully as a harness run, not as a gameplay-suite pass. Existing client/server/PG reached Lorencia on test0Dk and test1Dk. Inventory opened by mouse; character UI opened and showed level 11, XP 19000/24200, 50 unused points, seeded items and 10,000,000 Zen. A real reconnect from test0 to test1 succeeded. Map warps remain **unverified**: chat text `/move Noria` was captured still in the input field after a short SendKeys Enter. This is a test-input timing defect, not evidence that server warp fails.

Evidence: ready artifact 11578638189; warp-01 11577984876; input-02 11578424712; warp-ui-03 11578684284. Final artifact **11580160294**, `gameplay-final`, ZIP 20,056,292 bytes, SHA256 `0908bda3fcfed47f1529e292ff7579ae0f2ce3bfb806a04a176df8205647ad5d`, includes compressed PostgreSQL dump `gameplay-test-db.dump` (1,366,613 bytes). Keep this dump when resuming rather than discarding progress. Original final ZIP and character screenshot additionally saved as durable user deliverables.

Fixed the harness at commit `ee4029ce666aa44fc7f8e110e5ff13cfb115e766`: 250 ms Win32 physical key presses, proper active-client cleanup, restore previous gameplay database before starting OpenMU. No application/client rebuild, 423 tests repeat, assets/config/content/stat grants or imports.

Continuation run **37845483038**, workflow/control commit `67cf1faffd30dbabc87bd5a360ec362c31c238d6`: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37845483038 . Initial actor is existing seeded `test300` for normal warp eligibility; natural leveling still reserved for `test0`. Current blocker: await physical-input and map-warp proof. Next action: inspect screenshots, then merchant/combat/XP/drop/equip/level/relog, followed by two clients for party/trade/guild. Do not claim gameplay completion from workflow success.
