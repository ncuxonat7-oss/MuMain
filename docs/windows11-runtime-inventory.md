# Windows 11 runtime inventory — 2026-10-11 18:00 UTC

## Scope and provenance

Completed bounded 17:55 static inventory on the current dot cloud host, using project instructions and the preserved packaging recipe at MuMain `f2fdde60a3c49592be6d4925e500e216d5499310` (`task/windows11-package-candidate`). Findings below come from the inventory worker's report and supplied evidence maps; this documentation pass did not rerun archive inspection. Exact client/server bytes are now available on this host; that does not establish transfers into another executor.

Client provenance: artifact 11567737809 / run 37813650810 / MuMain source `8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5`, retained from project records, not a new workflow query. Server provenance: OpenMU `d067b3c11c23c3145de6e2c76201ab9a93b267c8`, workflow source `71159136c8f8cba949735be3ed0904fc15e5ad73`, SDK 10.0.401, release build with Money and local-only-bind patches.

| Archive | Bytes | SHA256 | Evidence |
|---|---:|---|---|
| validated-mumain-native-build.zip | 258057783 | eefe0a710518bc6536dd47cde45fb8605ae4ef5c7f4faca4095e8abb5f23297e | Newly verified |
| MuMain-windows-native-x64-release-editor-off-no-data.tar.gz | 258774906 | ccfcfc6c8d199d3a192a5abf22551926de35aaa88ebeea7c5ef6f905f695e66a | Newly verified nested TAR |
| openmu-money-local-bind-38104421623.zip | 22410241 | 505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c | Reused parent verification, not rehashed in this phase |
| openmu-money-local-bind-runtime.zip | 22966886 | 4b1b1d71a0aa992fb3f2dbac7e447a5704cccc7ed38ebacfdebe97eabebf1eec | Newly verified nested ZIP |

[Sanitized exact file/hash and dependency maps](windows11-runtime-inventory.json) preserve 36 client entries, 186 server entries, 15 client PE import lists and 110 server dependency references. Paths in these maps are archive-relative source and proposed staging destinations only. They are evidence, not an approved final manifest.

## Static results

- ZIP/TAR metadata inspection found no traversal, absolute paths, drive prefixes, backslashes, case-insensitive collisions, links or nonregular files. Entries were selected/streamed under size guards; no blanket extraction.
- Client proposed runtime selection: 36 files, 33,202,353 bytes. All 18 required shader outputs are present (six shader stems, each with DXIL/MSL/SPV), plus 15 x64 PE files, config/template and icon. Named non-OS direct/transitive static imports resolve within the bundle; delay-import directories are empty. Actual Windows OS/API-set resolution and dynamic loads remain untested.
- The bridge has no CLR directory, consistent with NativeAOT; a separate shared .NET client runtime is not inferred.
- Future staging proposal excludes build/debug-only MuClient.lib (971661260 bytes), Main.map (57218812) and Main.pdb (92827648). The initial 600 MiB member guard stopped at MuClient.lib; it was identified as build-only and not extracted. No source archive or package changed. Data/fonts are intentionally separate pinned inputs and were not downloaded or rehashed.
- Client config has localhost:44405, windowed 1024x768, English and empty saved credentials. No credentials configured.
- Server: all 186 member hashes match the archived runtime manifest; total 133,210,540 bytes. All 110 deps.json runtime/native/resource/runtimeTargets references resolve by package/root/locale paths. Preserve the whole server tree initially; no pruning approved.
- Startup.exe is x64 native PE; Startup.dll is managed PE with CLR directory. Its i386 PE container does not prove a 32-bit runtime requirement. Target is .NETCoreApp v10.0 without platform RID.
- Compiled runtimeconfig framework baseline is Microsoft.NETCore.App and Microsoft.AspNetCore.App 10.0.0; preserved launcher selects patch 10.0.11. These are different roles, not contradictory exact versions. Windows patch compatibility remains untested.
- Portable web UI remains UNKNOWN: staticwebassets.runtime.json contains 19 CI-machine content roots and no wwwroot/assets tree is packaged. This does not invalidate the previously tested game-server scenario. No replacement UI bundle retrieved.

## Remaining boundary and next proposal

Still missing: verified Windows x64 dotnet host and NETCore/ASP.NET Core bundles for the approved selected version; PostgreSQL 17.11 binaries/share/lib; PowerShell 7.4+ availability/distribution; dependency hashes, provenance and redistribution notices. Client native DLLs are present but their archive has no license/notice files. SDK, C++/shader compilers and Python are not established daily-launch dependencies.

Approved persistent DB/setup, authentication, final endpoints/manifest and independent migration verification remain unresolved; reconcile newer context-specific evidence separately rather than treating historical migration notes as current proof. No DB downloaded, restored or read.

Future implementation may accept exact local archives, validate nested paths/hashes, stage the selected client files and unchanged server tree, then merge separately pinned Data/fonts/launcher inventory in a fresh destination. Additional Windows dependencies and notices require their own verified bytes and approved scope. Deterministic final ZIP reconstruction is unproven. Portable UI work depends on the owner's agreed package scope.

No runnable package assembled; no build, installation, runtime execution, DB action or new tests. Proposed future tests are not PASS evidence. Existing recipe unchanged; `launchEnabled=false`, approved digest null, readiness 65.5/model1.1/MEDIUM unchanged.
