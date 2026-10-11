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
