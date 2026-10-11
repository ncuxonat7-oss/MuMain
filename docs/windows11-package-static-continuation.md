# Windows packaging static continuation — 2026-10-11

Scope: SAME bounded MEDIUM packaging stage, continued after owner 07:48 UTC
instruction. No rebuild, client/server/DB execution, archive regeneration,
installation, setup, credentials, network configuration or publication.
Parent reports docs checkpoint72e9ae606bddec91cfa710aefeb673f7e1b04145;
that object is not in this local repository and was not fetched in this pass.

## One supported Library health check

Loaded current Library hosted-app companion from its skill source in a fresh
private directory and called its supported public read method for the known
server Library ID. It failed during discovery, before the read/transfer:
`hosted apps tools/list request failed: network`.
Exactly one service attempt; no transfer retry, alternate route or upload.
Previous download and output failure records remain valid; no new Library IDs.
This does not establish a missing file, permission denial or component defect.

## Independently derived client requirements

Evidence is exact locally available client source commit
8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5, not an assumption from latest main.

| Component | Source-established requirement | Remaining byte-level proof |
|---|---|---|
| Client/bridge | Main.exe, MUnique.Client.Library.dll, config.ini; Windows x64; bridge PublishAot=true and win-x64 RID | Pinned ZIP member hashes, PE architecture and transitive/delay/dynamic imports |
| SDL / turbojpeg | SDL_STATIC ON and turbojpeg-static link target | Actual linked archive and binary closure; do not add guessed DLLs |
| curl / OpenSSL | CMake CURL and OpenSSL Crypto dependencies; vcpkg curl ssl, openssl | Resolved package versions, runtime DLL names/hashes and notices |
| Native dependency DLLs | CMake TARGET_RUNTIME_DLLS staging | Exact staged inventory and full import closure |
| MSVC CRT | Workflow copies all DLLs from the active x64 Microsoft.VC*.CRT directory | Actual copied version, hashes and notices; source alone does not prove laptop compatibility |
| Shader tooling | glslang, SPIRV-Cross, DXC are source build inputs; runtime requires compiled shader outputs | Preserve archived shader bytes; no local compiler/SDK installation required by ordinary launcher |
| OS libraries | Workflow uses an explicit 56-name Windows OS allowlist and verifies OS resolution in CI | Target laptop OS/graphics/driver and OS import availability remain untested; allowlist is not the actual import list |

The bridge's net10.0 target is a build property; NativeAOT source does not by
itself establish a separate shared .NET requirement for the bridge. The server
launcher independently requires Microsoft.NETCore.App and Microsoft.AspNetCore.App
10.0.11, PostgreSQL17.11 tools, PowerShell7.4+, Windows11 x64. Actual server
runtimeconfig/deps files, Windows dependency archives, hashes and license notices
remain unavailable. SDK10.0.401 is build provenance, not a daily-launch prerequisite.
Python applies the overlay during packaging; reviewed daily Start does not call it.
No inferred minimum RAM/GPU/disk requirements are introduced.

The exact source-required 18 shader members (under client/shaders):

- `basic_colored.frag.dxil`
- `basic_colored.frag.msl`
- `basic_colored.frag.spv`
- `basic_colored.vert.dxil`
- `basic_colored.vert.msl`
- `basic_colored.vert.spv`
- `basic_textured.frag.dxil`
- `basic_textured.frag.msl`
- `basic_textured.frag.spv`
- `basic_textured.vert.dxil`
- `basic_textured.vert.msl`
- `basic_textured.vert.spv`
- `shadow_volume.vert.dxil`
- `shadow_volume.vert.msl`
- `shadow_volume.vert.spv`
- `skinned_textured.vert.dxil`
- `skinned_textured.vert.msl`
- `skinned_textured.vert.spv`

## Migration terminal blocker

Scanned filenames in all locally available project Git refs: no OpenMU Migrations
subtree, ConnectionConfigurator.cs or ExtendedTypeContext.cs. Retained pinned
EntityDataContext.cs inherits ExtendedTypeContext and delegates options through
Configure; retained Program/PersistenceContextProvider files establish applied /
pending migration behavior but contain no complete migration definition set or
history-table configuration. A model's config/data schemas are not sufficient to
infer the migration-history schema. No live database was read.

Required input: complete EntityDataContext migration definitions/designer metadata
and connection/history-table configuration at OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8,
including relevant build inclusion/patch information, OR inspectable pinned
runtime metadata providing equivalent migration/context and history evidence.
Enumerate the full ordered distinct IDs for that context independently of the DB.
Until then migrationIds and migrationSchema remain unknown; never substitute the
DB's current history or an empty list. No new source-download workaround attempted.

## Preserved state and next boundary

Original package tree, draft manifest and both ZIPs are unchanged. Existing
archive SHA256 values remain fb1f389a640bb83b9bfedbf14526655647031600e48402358e94f9a1d55b3f28
(full) and 0e51834cfec24be6b93241d5416d9e6b14af2aee955406623c853abb2306eafe
(review). Launcher unchanged7f5b44a9; launchEnabled=false and approved digest null.
Five prior packaging checks remain PASS; no unchanged tests rerun. This pass
cross-checked the 18 unique shader names and pinned source hashes only.

Technical terminal blocker: supported Library path remains unavailable. Complete
runtime/client/dependency bytes and independent migration evidence are needed
before a complete manifest can be produced. No new owner authority is needed to
resolve the transfer service. Initial persistent DB/authentication/installation
and Windows acceptance remain separate future decisions. Stop this bounded pass.

Pinned source SHA256 evidence:

- `.github/workflows/windows-client.yml`: SHA256 `51a50b565d2b248f53648f63fe187a75522dc450765917dded9eb3fbe5fe5a58`.
- `ClientLibrary/MUnique.Client.Library.csproj`: SHA256 `76fc1208ec7755f3bfc0680086c7c198dd6d21df27f197940f9cbfbcb59bce6a`.
- `src/CMakeLists.txt`: SHA256 `3b9601f83371c0cd4d8a33e57757c34a067b6013556688680921e5fc9e107dbf`.
- `vcpkg.json`: SHA256 `34c8d4edaad0172ef5a502aec35aad9b4c2694f617b700d60a77ee757fbe4ca9`.
