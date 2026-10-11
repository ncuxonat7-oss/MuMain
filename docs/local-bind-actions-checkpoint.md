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
