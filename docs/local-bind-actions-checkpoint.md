# Approved disposable console setting — 2026-10-11 03:34 UTC

Owner approved the exact conditional one-field configuration change at03:29:29UTC. Prepared and published3a9dff7a7304c5ca0ddbeaaa81e90ab6b1df32f8 on task/local-bind-isolated-check, exact remote readback and independent static review PASS. Source runtime/artifact and original dump unchanged. New function verifies owned PG process/listener/data-directory/DB identity, locks SystemConfiguration in a bounded transaction, requires exactly one row and boolean flag, updates only false to true, checks other fields unchanged, and records safe committed evidence. True is no-op. Unexpected row count/value or SQL error stops/rolls back. Gameplay fixture checked again. No runtime execution yet.

Next owner NEW manual Windows Client Build run on task/local-bind-isolated-check at3a9dff7, no extra inputs. Full server/native/persistence still NOT_RUN; Readiness65.5 unchanged. Endpoint schema confirmed in pinned source, but current all-row query may reject unused/unlinked definitions; this remaining strict runtime gate was not silently weakened. Native world entry still requires visual evidence. No automatic dispatch or access changes.

# Current blocker — 2026-10-11 03:28 UTC

Manual run38108174523 at9e0ee2591d9e86f462b2250b11eb2927eba3756b failed at line167 before server startup. Evidence11691160010,15279bytes,SHA2562079c09346b4013db351678d3105d6930d6664dd2fea0cce2e6189fa2009f5a6. DB restore, configuration/child-environment prelaunch guard and expected character fixture PASS; owned PG cleanup PASS. Explicit CLR parser correction is now verified through the guard. No OpenMU/native start, restart or persistence proof.

ReadConsoleInput guard requires exactly one SystemConfiguration row with true. Evidence does not distinguish false from unexpected row count. Pinned initialization defaults false; schema has no singleton constraint. Pinned Program has no CLI override for this flag; console pid/exit loop is conditional on it. Do not substitute unproven Ctrl+C/process-kill shutdown. Existing dump/pg_restore not present in parent workspace; no extra run or download was made just to learn this value.

Owner decision requested03:28UTC: conditionally enable only ReadConsoleInput in the disposable restored copy if exactly one row exists and value is false; preserve source artifact and gameplay fixture, stop on multiple/unknown rows. Pending approval; no DB correction implemented or performed. This changes the previous no-SQL-repair contract narrowly only if approved. No repeat run yet. Readiness65.5 unchanged.

# Latest DB guard correction — 2026-10-11 03:22 UTC

Manual run38107679674 at60bec9e, job114376540995 FAILED before OpenMU launch. Verified evidence artifact11690019550,13352bytes,SHA256018b80d7c861d41cc678d840d2c56e283639b151c220bd673fa1989775d41564. PG version/init/start/createdb/roles/restore/identity-write completed successfully; pipe fix now verified. Owned PG cleanup completed successfully. Failure evidence identifies scriptLine456, the DB option allowlist rejection. No native action, server startup or persistence result.

Pinned XML uses only permitted keys. Source-level diagnosis: PowerShell IDictionary adaptation directs dot-property assignment to dictionary set_Item; assigning ConnectionString that way creates an unexpected key rather than calling the CLR parser. Explicit set_ConnectionString/get_Keys resolves this mechanism while retaining host/database/port and key guards. References: PowerShell v7.4.6 Binders.cs lines5530–5558; dotnet/runtime v10.0.0 DbConnectionStringBuilder.cs lines153–172. No local pwsh reproduction available, so fixed runtime remains UNVERIFIED.

One-file patch published at9e0ee2591d9e86f462b2250b11eb2927eba3756b on task/local-bind-isolated-check; exact remote readback and independent static review PASS. Safe diagnostics include only entry index, error type and restricted key metadata, never connection values. No rebuild or automatic dispatch. Next owner NEW manual Windows Client Build run on this branch/head9e0ee25, no inputs; supersedes60bec9e Run instruction. Owner informed03:21UTC.

Access read-only check: saved environment has gh2.46.0 at/usr/bin/gh, but API request receives proxy CONNECT403 and gh auth status reports invalid token. Account/authentication and Actions write remain UNCONFIRMED; network failure prevents attributing failure to credentials alone. No setup/access changes; owner deferred access work in favor of current smoke. Browser dispatch remains paused. Readiness65.5 unchanged.

# Current prepared integration check — 2026-10-11 03:07 UTC

Latest test branch commit: 60bec9e87db2ec35e2b36716b6fff13ae5aa91ac (task/local-bind-isolated-check). Published one-file PS guard correction with exact remote readback; includes prior pg_ctl output-pipe fix abe181f. No new run dispatched. This supersedes the older instruction to launch abe181f.

Read-only inspection of the already verified runtime artifact11689365514 found three deterministic prelaunch guard mismatches: actual appsettings sections DetailedErrors/Database/Serilog, the two packaged Web.AdminPanel/Web.Map runtimeconfig files, and Startup NullabilityInfoContext=true. These were test-harness assumptions, not demonstrated game-server defects. Guard now accepts only the four exact root-level JSON files with their independently verified SHA256 values and actual shapes. Unknown files, changed bytes, endpoint overrides, unsafe DB destinations and inherited hosting environment overrides remain rejected. Runtime files were not modified. Independent static review PASS; Windows PowerShell execution and end-to-end result remain UNVERIFIED.

Confirmed evidence remains: full server build38104421623 PASS;186 runtime manifest entries verified; last diagnostic38106487089 confirmed PostgreSQL start exit0 followed by output pipe timeout and successful owned cleanup. DB restore, OpenMU startup, native action/relog and persistence are NOT_RUN for this integration stage. Readiness remains65.5/model1.1/MEDIUM; no new gameplay credit. Do not repeat unchanged builds or helper tests.

Exact next action when owner returns: NEW manual Run workflow at https://github.com/ncuxonat7-oss/MuMain/actions/workflows/windows-client.yml, branch task/local-bind-isolated-check, no additional inputs; verify head60bec9e. Send the run URL. No old-job rerun. One existing smoke reuses the pinned runtime/client/Data and temporary baseline DB, then checks ownership/configuration, native STR action, graceful restart and stored state; parent must inspect screenshots before claiming native relog. Remaining guarded runtime prerequisites may still fail and must be diagnosed from evidence without claiming success.

Autonomous dispatch remains blocked by the explicitly paused browser route and absence of a verified alternative dispatch tool. Read-only access investigation is complete: connector file writes do not establish Actions write; CLI may be a supported future route only after explicit pause/access decisions and verification. No network, persistent access, credentials or automation changes were made. Preserve approved boundaries.

# Latest diagnosis / next prepared run — 2026-10-11 02:56 UTC

Manualrun38106487089 at90aa59dffe371c7e14567add11d442e4c57aa766 failed quickly with useful stage evidence. Artifact11689437943,12836bytes,SHA256fa29fb020f78ec5bd27e82be29af48314195ccb0910e03d986dd015f9f4cc847. versionprobePASS; initdbPASS2.74s; pg_ctl start exited0, then output drain hit5-second pipe_timeout. Owned postmaster.pid existed; cleanup pg_ctl stop exited0, postgresStopped=true/completed=true. Restore/OpenMU/native/persistence were NOT RUN. This establishes the output-wait failure; daemon inheritance explains it plausibly but exact handle ownership was not traced.

One-file fix published/readback exact at abe181f3693b58853a6eb18461e07c5e5fb324be on task/local-bind-isolated-check: only pg_ctl start inherits console stdout/stderr rather than waiting for pipe EOF. PostgreSQL still logs via existing -l. Utility deadline, exitcode, PG readiness/ownership checks and cleanup remain; all other utilities retain bounded drain checks. Static applicability checked, Windows behavior NOT YET VERIFIED. No server rebuild, no new permissions or trigger changes, no automatic dispatch.

Next needed action: owner NEW manual Windows Client Build run on task/local-bind-isolated-check selecting abe181f. Existing browser dispatch remains paused. Do not rerun old job SHA as test of this fix. Owner requested continuing bounded fixes/diagnosis within this stage and investigation of minimal supported autonomous access; access investigation is read-only, no pause bypass or token creation.

Verified runtime backup: private Library libfile_b1e2679ae4088191859d97f0bbd4903c version0, file_00000000470081fd83bbe9138f5398a6, openmu-money-local-bind-38104421623.zip. Outer/inner hashes matched existing artifact; no runtime execution. Retain for reuse rather than rebuild after Actions retention.

# Latest runtime attempt — 2026-10-11 02:40 UTC

Owner manually ran38105086865 at a8789a10524a7469e5bb391b183364e62fee516a; job114368780036 FAILED on smoke12-minute timeout (02:27:00–02:39:00). New runtime11689365514 reused: outer/inner hash/provenance, exact186manifestfiles PASS; client/DB/Data stagingPASS. Source checkout/build/helper checks SKIPPED as intended, no rebuild.

Evidence11689786581,11577bytes,SHA25629bb1a0681de1e58c5c793006c2b28c755c61ddf08ccebba13ddc22eb75a9bb1. smoke-result NOT_RUN, cleanup completed=true/serverForceKill=false/clusterDeleted=false, server-log-summary empty. No database-identity, state, endpoint/listener snapshots or native screenshots. Do not claim server start, completedDBrestore, STR action, persistence or relog. Successful setup of input archives is not database initialization proof.

Current cause UNKNOWN; one bounded read-only review of operations before first durable DB evidence is underway. Private PG setup logs were not preserved by this evidence bundle. Do not run another blind12-minute attempt or rebuildserver. Preserve current buildPASS/helperPASS independently; readinessunchanged65.5.

# Latest verified build — 2026-10-11 02:17 UTC

Manual run38104421623 source71159136c8f8cba949735be3ed0904fc15e5ad73, job114366770737 SUCCESS. SDK10.0.401; pinnedOpenMU d067b3c + unchanged Money/local-bind patches; same -c Release -p:ci=true and LF. Full Startup build succeeded in3m01.73s,267warnings,0errors. Build-only resultPASS; DB/client downloads and all integration steps deliberately SKIPPED. No listener/shutdown/persistence/native world-entry proof.

Reusable new runtime artifact11689365514 (openmu-money-local-bind-38104421623),22410241bytes, outerZIP SHA256505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c, expires2026-11-10. Inner runtimeZIP SHA2564b1b1d71a0aa992fb3f2dbac7e447a5704cccc7ed38ebacfdebe97eabebf1eec. Contains runtime and hash/provenance records. This differs from old Money-only artifact11630698202. Do not rebuild unchanged source for next smoke; verify/reuse this output.

Evidence artifact11689275690,25044bytes,SHA256929cb0627486f50225874f56eee317a70abdc6feb313d89ff477311a4787c010,expires2026-10-25. Parent read BUILD_ONLY_PASS, sdk/source provenance, matching_errors0, untruncateddiagnostics and buildtail. SDK10.0.109 failedpreviousfullbuild;10.0.401 nowworks. Precise compiler-internal root cause not claimed.

Next proposed action: reuse exactnewruntime for already scoped temporaryDB nativeSTR/gracefulrestart smoke, with no new build. Any new manual run must select corrected workflowversion; current branch still build-only. Existing integrated smoke safety/readConsoleInput/endpoint schema remain runtimeUNKNOWN and shouldfailclosed. Earlier12helperchecks remainPASS. Readiness65.5unchanged until relevant actualgameplayevidence.

# Latest execution — 2026-10-11 02:05 UTC

Owner manual run38103777523, source25321d0e38a25e66572e77f13872bdd66cda3e65, job114364892672: server build FAILED. PowerShell syntax, approved artifact hashes/staging, pinned source/patch checks and SDK setup PASS. Build tail reports 165 errors/273 warnings in generated AdminPanel Pages_LogFiles_razor.g.cs, including CS0246 __builder, CS7014 and CS0103; elapsed2m01.91s. Root cause NOT YET ESTABLISHED; do not call cascade count165 separate defects.

New runtime archive skipped. DB restore, server start, STR action, shutdown and relog NOT_RUN. Earlier isolated helper12/12 PASS remains valid and is not full server compile proof. Readiness unchanged.

Evidence artifact11688443945, local-bind-server-smoke-38103777523-1, 14015bytes, SHA256c16bbd37f682e3fe2dcd8e7476898bd1bac77c3004548a97114784fb78500d92, expires2026-10-25. Parent read build-tail/job-status/result; tail may omit the first causal compiler error. One LOW read-only comparison of pinned Razor/source and previous successful toolchain is underway. No repeat build/dispatch or code change authorized by this diagnostic continuation.

# Prepared integration stage — 2026-10-11 02:00 UTC

Owner approved MEDIUM server-only build and one isolated Windows smoke with baseline DB artifact11651520969 at 01:30 UTC. Published and exact read-back verified: task/local-bind-isolated-check commit25321d0e38a25e66572e77f13872bdd66cda3e65. Three files: existing windows-client.yml plus scripts/prepare-local-bind-smoke.py and scripts/local-bind-server-smoke.ps1. One manual Windows job35min, build18min, smoke12min. No dispatch by parent; awaiting owner Run. Integration NOT_RUN.

Inputs: pinned OpenMU d067b3c with unchanged Money/local-bind patches, SDK10.0.109, existing client11567737809 and disposable baselineDB11651520969. Historical STR scenario from finish-gameplay.yml at52971f34461304a76587cfe3b6c694be239fc54d: guarded test0Dk STR31→32, points2→1, level2/EXP115/44items/shieldslot1 unchanged. No fixture repair on mismatch. New runtime archived before startup. Existing12helperchecks not repeated.

Review fixes: validate config/runtime hashes and loopback DB destination before each Process.Start; explicit child environment excludes inherited hosting overrides. Native relog is PENDING_VISUAL_REVIEW even if SQL persistedState=PASS; parent must inspect screenshots and cannot infer world entry from TCP/character-list alone. Strict config/schema/ReadConsoleInput prerequisites remain runtime UNKNOWN and fail closed. Server shutdown uses owned stdin exit while PG remains alive; no server force-kill. Client cleanup may terminate owned client.

Review archive Library libfile_7d3e417277c08191a53b9aa879b7ec41 version1, SHA256932a62351fa8381d91ef35db06ca4dc068fa2fe93afbd3786e51b98259bc4667. Static review only; no package readiness upgrade.

# Isolated local bind Actions checkpoint

## Current result — 2026-10-11 01:24 UTC
Owner manual run https://github.com/ncuxonat7-oss/MuMain/actions/runs/38101598438 on task/local-bind-isolated-check, exact commit c7a7552886ccbc3c657d443a6bda73590904d4b0, job 114358468931: SUCCESS.
- Pinned source SHA256, unchanged Money patch, patch scope, exact Listener byte change and reversal: PASS.
- Official .NET SDK 10.0.109 installed on Windows x64; helper restored and compiled.
- Existing helper/socket checks: 12/12 PASS (legacy selection, invalid options, loopback selection/socket/connect).
- Evidence artifact 11688226406, local-bind-isolated-38101598438-1, 3658 bytes, SHA256 acfd1c6d90392ea0eca6ab51c79a79f8bba0ab619c99b2379be9ad6d17233d5a. Expires 2026-10-18. Parent downloaded/read all five evidence files.
- No full OpenMU build/start, native client, PostgreSQL integration, production exposure check, persistence test or final Windows package proof was performed. Readiness remains 65.5; this is a narrow engineering blocker closure.

## Diagnosed newline mechanism
This runner's system Git config had core.autocrlf=true; core.eol unset.
Pinned original Listener: 6234 bytes, 167 LF, 0 CRLF, UTF-8 BOM, SHA256 63b9f3e22dbed204cfc6444a3d913c0a708bc659fc6bc30f9cf08837e349cc9a.
Expected patched Listener: 6250 bytes, 167 LF, 0 CRLF, SHA256 7f887ef3e58ee009beee04c6632ffe6b4f290669ae098f39ff72778c6561f2a3.
One temporary control application using recorded original settings succeeded but produced 6417 bytes, 167 CRLF, SHA256 371a6a52a79652f0ce19bb48083cf380f3d39da5dc8fb719120e85852f538df7; exact comparison FALSE.
Step-local core.autocrlf=false and core.eol=lf produced exact expected 6250 bytes/hash; strict checker and byte-exact reverse application passed.
This demonstrates the newline mechanism on the current runner. Historical run settings were not captured, so it is not direct evidence of every property of the older runner.
No comparison normalization or integrity-check suppression was used. No global Git configuration was changed.

## Previous attempts — retained to prevent repetition
First workflow 6c3f57410f61e1f0f5d196d7280fe1b3d1d7cbc3, manual run 38099276936: startup_failure, jobs=[], SDK/tests NOT RUN. Forbidden runner.temp at job-level env. Related push validation 38098977391 was not gameplay.
Correction 211dd945727554d9d93c01b317170684d6f7a2ce moved paths into GITHUB_ENV during initial step. Manual run 38099569774 passed seven source hashes but stopped at exact Listener comparison before SDK. 0/12 NOT RUN.
Diagnostic correction c7a7552 preserved strict checks, pinned step-local Git settings and captured one control application. Independently statically reviewed; owner approved publication by verified reaction and manually ran it. Browser dispatch path remains paused; parent did not dispatch.

## Next decision / handoff
Do not rerun these 12 checks merely to reconfirm unchanged inputs.
Recommend a bounded next integration stage using pinned OpenMU d067b3c + unchanged Money patch + reviewed local-bind patch, before constructing a launcher around unverified behavior. First determine the smallest supported build/runtime route from existing artifacts, then assess real listeners and safe start/stop on a disposable or backed-up approved environment.
This is a proposal, not approval for a large build, database restore/migration, persistent access change, main merge or new workflow publication. The successful helper route does not establish full server compatibility, correct local-only admin/PG bindings, or shutdown persistence.
Owner's current goal remains one easy-to-start local Windows 11 Alpha; reuse existing component manifest and seven QA cards. No new automation architecture.
