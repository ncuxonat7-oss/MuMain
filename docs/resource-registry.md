# Resource registry / stack freeze / recovery

Updated2026-10-09. Current prototype uses exact frozen resources below. Auth/Lorencia/normal gameplay/relog are VERIFIED, not pending. Historical future candidates were checked2026-10-08; prices are historical, not a fresh offer. No purchases/imports during this audit.

## CURRENT PROTOTYPE RESOURCES

|Component|Exact source / identity|Type / provenance / rights|
|---|---|---|
|OpenMU|https://github.com/MUnique/OpenMU commit d067b3c11c23c3145de6e2c76201ab9a93b267c8|MIT C# source, existing Release build; no server source changes|
|MuMain|https://github.com/ncuxonat7-oss/MuMain validated8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5; upstream https://github.com/sven-n/MuMain at21728b1e5b03e0763b38ef9e23f79645e0df7ad2|Source-built C++/NativeAOT Windows binary,423 tests passed; original source permissions unresolved YELLOW|
|Data/fonts package|https://github.com/sven-n/MuMain/releases/tag/data-4b0ab29c58b27fc4 ; MuMain-data-4b0ab29c58b27fc4.tar.gz|457104401bytes; SHA256 8c62a98aaabf13d80c24c0c688dbfafd4b23813966dd3a2f13c445c3a35e8d1d; maintainer published, exact match to build|
|Data tree|77f7830f542d106fc519c8821832d49a3dd8ae3a|13,188 files; complete nontruncated manifest captured; game-content permission/redistribution unresolved|
|Fonts tree|149f928e2547aa6658977c3f41c63abccfa471ed|Cousine/Liberation/Nanum/Noto:OFL1.1; DejaVu:Bitstream Vera plus public-domain changes; retain notices/reserved names|

Season5.2-derived client targeting Season6Episode3 with OpenMU extended protocol. Maintainer provenance is not original rightsholder permission. Owner authorized this exact uncertain-rights pack for closed technical prototype after risk disclosure2026-10-08. No commercial/source redistribution clearance claimed. Do not import positively identified leaked source/cracks/suspicious binaries. Existing workflow verifies tar hash and unsafe/executable asset paths. Binary bundle omits Data/fonts; keep package boundary replaceable. Original editable artist sources unknown.

### Durable recovery inventory

These authorized-user backup IDs are permanent recovery pointers, not public download URLs. GitHub docs are canonical metadata; large archives/evidence are private user files. A fresh agent with the same connected file tool can find/materialize by exact ID/name using the Library skill, verify SHA, then restore. Do not publish DB dumps or raw asset JSON. If file access is unavailable, request only restoration of the named saved archive, not source research.

|Saved artifact|GitHub provenance|Authorized-user backup ID|Integrity / scope|
|---|---|---|---|
|validated-mumain-native-build.zip|run37813650810 artifact11567737809|libfile_1174bdeb6c048191ad0be1ac163fdad5|258057783bytes; SHA256 eefe0a710518bc6536dd47cde45fb8605ae4ef5c7f4faca4095e8abb5f23297e; inner MuMain-windows-native-x64-release-editor-off-no-data.tar.gz; full bridge/shaders runtime, not Main.exe-only|
|gameplay-final evidence ZIP|run37860870710 artifact11585339277|libfile_33e96d9c75048191adff00a6c4235a5b|11495834bytes; SHA256 bebf351e6a295dc15f9e47e9abe83aeb8653fbccbef401c2fcb8aa03bd137615; latest pg snapshot/logs/screenshots; confirmed equipped shield|
|05-level screenshot|same finite smoke|libfile_1ce42f4769f48191b6b4638c964b8b35|Authentic native UI screenshot|
|06-shield screenshot|same finite smoke|libfile_b03de463cba8819198a6d940cc8ff55d|Authentic native equipped/relogged character|
|baseline-config-evidence ZIP|run37863153228 artifact11587091295|libfile_ffa8a767ce3481919c5ce75cf65117c3|1059611bytes; SHA256 b952abed311e6f77cc9aa3ae1f5fbb43ca302b75e5f58b602200bf70e029accd; complete baseline-config.jsonl export and reference result|
|client-resource-audit-inputs.zip|2026-10-09 exact pinned tree/metadata retrieval, no CI|libfile_7131d39798708191a06116bb1ca38305|127791bytes; SHA256 c68b65f373f09ff0c2a7f01dcafc3f8e1766ff7bdf7d6d50de6e666869354da1; manifest,33 metadata files, prior scalar checks, derived result; private source inputs, not rights-cleared redistribution|

Build executable Main.exe SHA256 9d895c638eb256b98d728dfc511f4c57d4a9e88cdba703e639426712b0b57cd5; MUnique.Client.Library.dll SHA256 9292041494d9226f105fc07a94c2451f6303b906123b2932ea05a3469c378cb7.

GitHub artifact retention is finite; saved backups prevent client rebuild/export repetition. Prototype Data457MB is at pinned maintainer release, NOT duplicated in this checkpoint; upstream disappearance would require recovery of that exact pack, not arbitrary repacks. Server cache openmu-windows-runtime-d067b3c-net10-v1 is opportunistic; if unavailable, use pinned source and explain targeted build cost first. Exact historical SDK patch is unknown; other frozen dependencies in architecture.md and pinned package files. No permanent VPS/service to reconnect to.

Restore order:materialize validated client + newest gameplay-final evidence; inspect archive names; restore its PostgreSQL dump with existing workflow (secrets as temporary fixtures, no commits); acquire exact separate resource pack/check hash; reuse server cache/pinned source; run only targeted next scenario. Configuration validators work from saved export without a server. Client checker works from saved metadata/manifest. Local scratch paths are not recovery pointers.

Newest character511da101-0000-71fb-6952-30e15c234eb0; inventory511da101-0000-7e11-4d14-43e066028e6a; shield801da101-0000-760d-a605-a410efe9185d. Latest expected level2,EXP115,STR31,points2,offhand1,44 same item UUIDs. Never use pre-shield snapshot accidentally.

## PRODUCTION CANDIDATES
These are a shortlist, not purchase recommendations or complete ready-to-distribute MU packages. No verified licensed drop-in MU Data replacement found in this narrow check.

### A. MuMain exact Data release
Name/URL/version/content/source: see selected candidate above. Price: free download.
Editable assets: present in Data; original artist project files and rights to modify are not established.
License/redistribution: unresolved for proprietary game content. Production risk: high until rights cleared.
Benefit: best technical fit and least prototype setup work. Drawback: cannot mark commercial distribution approved.
Stack change: none for prototype fit; production replacement may need conversion and remapping. The client source rights are a separate issue.

### B. WEBZEN negotiated MU IP licensing
Source: https://company.webzen.com/en/business/partnership
Price: not public; contractual inquiry/quote required. Do not send an inquiry or buy without authorization.
Season/content/source delivery: not specified publicly; legacy S6 assets, source delivery, modification, redistribution, private hosting and sublicensing to customer instances must be negotiated explicitly.
Compatibility: unverified; no evidence a license for this fork will be offered.
Benefit: rightsholder route for original MU IP. Drawback: availability, price and exact grant unknown.
Risk: high commercial/availability uncertainty, not an established offering of a legacy asset archive.
Stack change: unknown, depends on contract and delivered assets. Do not infer the official retail download provides these rights.

### C. Kenney Mini Dungeon (free original substitute components)
Source: https://kenney.nl/assets/mini-dungeon
Price: free; version 2.0 shown; Season: not MU.
Includes: 30 listed 3D files, animation/variations, character rigs, weapons/shields and dungeon objects.
Source: downloadable editable model assets; original artist scene/source completeness not checked; no client/server source.
License: CC0, permits commercial use/modification/redistribution.
Compatibility: NOT drop-in BMD/OZ*/terrain/animation replacements. Conversion, skeleton/action mapping and server/client IDs must be validated; no conversion implemented.
Benefit: clearly licensed original components. Drawback: different style, incomplete MU world/UI/sounds, not Lorencia.
Risk: low rights risk; substantial asset adaptation risk.
Stack change: no demonstrated need to replace OpenMU; MuMain asset conversion/import changes may be necessary. Not selected for immediate E2E.

### D. Kenney Game Assets All-in-1 (paid convenience bundle)
Source: https://kenney.itch.io/kenney-game-assets
Price checked: USD 19.95 minimum; package 3.7.0 listed. Season: not MU.
Includes: 60,000+ models, sprites, UI, audio and fonts; optional asset launcher. Editable PNG/SVG/OBJ/FBX/GLTF/OGG formats listed; original DCC source completeness not checked.
License: CC0 assets, commercial projects permitted. The bundle collects also freely available packs; buying it does not grant MU IP rights.
Modification/redistribution: CC0 assets permit both; assess optional launcher separately if ever used. No purchase made.
Compatibility: generic assets, NOT complete compatible MU Data. Conversion/mapping required.
Benefit: broad reusable licensed content in one download. Drawback: no MU maps, protocol definitions or ready Lorencia package.
Risk: low rights risk for CC0 assets, high integration/completeness risk.
Stack change: same as candidate C; server need not be replaced based on these assets alone.

## REJECTED / UNSUITABLE
- Current official MU retail download: https://muonline.webzen.com/en/download/game-download . Authentic origin, but compatibility with our extended legacy client is unverified. https://www.webzen.com/Legal/EULA grants use with WEBZEN's service and restricts modification/unauthorized connections; it is not a verified resource license for our private prototype or redistribution. Not downloaded.
- Random S6 mirrors, repacks and commercial private-server file sellers: not selected; no demonstrated rights chain, checksum, exact tree compatibility or security review. A seller's license for its additions does not automatically cover Webzen content. No such binaries purchased/run.
- Generic CC0 models as an immediate Lorencia solution: unsuitable without an entire conversion/mapping/world resource effort; they remain possible future components.
- Quaternius: checked author catalogue https://quaternius.com ; individual targeted pack page unavailable through lookup. Not shortlisted with unverified price/package/terms; no download.
- Source provenance constraint: MuMain README says Season 5.2 sources uploaded by Louis. There is no verified root grant or original-owner authorization in the inspected tree. Public availability does not resolve rights. Do not import any positively identified leaked proprietary source, cracked software, credentials or suspicious executable package.

## STACK FREEZE CHECK
GREEN means a known permissive component is suitable subject to its license obligations; not a warranty or completed security/transitive-dependency audit.
YELLOW means unresolved license/runtime/reproducibility concerns; not proof of a fundamental dead end.
RED means an established fundamental technical dead end requiring substantial stack reconstruction. No such technical RED established by this bounded audit.

| Component | Frozen identity/type | License/status | Class |
|---|---|---|---|
| OpenMU | MUnique/OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8; C# source-built existing Release | Root MIT verified; retain notices | GREEN |
| MuMain | ncuxonat7-oss/MuMain 8d18a2b; upstream 21728b1; C++ source-built Windows executable | No root license found; original source rights/provenance unresolved; cannot promise distributable product | YELLOW |
| MUnique.Client.Library | Built with client, .NET NativeAOT DLL; OpenMU packets 0.9.10 dependency | Client tree includes community adaptations; per-file/upstream rights need distribution audit | YELLOW |
| Data | Exact data-4b0ab29c58b27fc4; ready assets, used in verified core gameplay | No verified game-content permission | YELLOW |
| Fonts | Above five families; ready font assets | OFL/Bitstream Vera texts verified; preserve notices | GREEN |
| .NET | Server net10.0 requires .NET/ASP.NET 10.0.0+; current portable runtime 10.0.11; CI setup-dotnet 10.0.x | Microsoft runtime/source licensing and redistribution notices apply; exact historical SDK patch not established | GREEN |
| PostgreSQL | Official Windows PostgreSQL17.11; actual saved/restored database in native runs | PostgreSQL License; confirmed working disposable Windows environment | GREEN |
| EF/Npgsql | EF Core 10.0.2, Npgsql/provider 10.0.0 in existing server deps.json | Permissive upstream licenses; final dependency notices audit outstanding | GREEN |
| Other server dependencies | Serilog 4.3.0, BCrypt.Net-Next 4.0.3, BlazorInputFile 0.2.0; exact full set in deps.json and src/Directory.Packages.props | Transitive rights/security inventory not completed | YELLOW (release audit) |
| Windows toolchain | CI Visual Studio 18 Enterprise; MSVC 19.51.36260.0, tools 14.51.36231, Windows SDK 10.0.26100.0; CMake >=3.25, Ninja, vcpkg | Tool use and CRT redistribution governed by Microsoft terms; CRT staged in artifact | YELLOW (release/tool freeze) |
| SDL | submodule d9d5536704d585616d4db3c8ba3c4ff6fc2757e1; source-built | SDL zlib license; preserve license | GREEN |
| SDL3_ttf | a1ce3670aec736ecbf0936c43f2f0cc53aa61e5b, CI reports 3.2.2 | zlib; FreeType/HarfBuzz/plutosvg dependencies need notice inventory | YELLOW (transitive audit) |
| glm / spdlog / miniaudio | 1.0.1 / v1.15.3 / 9634bedb5b5a2ca38c1ee7108a9358a4e233f14d; source fetched by CMake | Permissive upstream licenses; preserve notices | GREEN |
| imgui | submodule 21d3299e588b5c702dcca0f448b4f937af369b4a; editor OFF, not needed by current build | MIT upstream | GREEN |
| Client build/runtime dependencies | vcpkg curl+SSL, OpenSSL, glslang, SPIRV-Cross, DXC; source/build packages and resulting DLLs/shaders | Exact package resolutions in successful CI log, vcpkg.json not baseline-pinned; per-package notices/runtime inventory outstanding | YELLOW (reproducibility/distribution) |
| GitHub Actions | Windows runner, native client/gameplay and PostgreSQL tested; ephemeral sessions | Established native route; not permanent hosting | YELLOW (execution) |

Earlier Linux-only initdb/root/ptrace blockers are solved for this prototype by the confirmed Windows PostgreSQL route. Failed attempts remain in lessons-learned.md; do not repeat them.

## FUTURE ARCHITECTURE CHECK (assessment only)
OpenMU already has plugin points, persisted configuration, reset counters/commands, offline leveling/player management, event/item/monster definitions and server/admin components. Findings from source/docs, not completed feature claims.
| Future requirement | Current extension route / unresolved work |
|---|---|
| Auto Reset | Existing reset counters and commands; automation policy/plugin still needs implementation/testing |
| Offline EXP | Existing offline-leveling command/OfflinePlayer infrastructure; validate limits and persistence later |
| VIP/subscriptions, Battle Pass | Persist entitlements/progress and server plugins; payment/web integration and UI are new work |
| Custom events, items, monsters | Server configuration/plugins plus mapped client assets; novel formats/animations may require client changes |
| Launcher/updater | External versioned deployment component; independently version runtime and resources |
| Website/account panel | Existing admin/auth infrastructure does not equal a customer website; new secured user flows needed |
| Marketplace | Transactions, ownership/concurrency/audit/API required; not claimed to exist |
| API/AI administration | Add narrow authenticated authorized API; no public unprotected admin control |
| PvP testing/bots | Server test actors/offline bots already documented; real graphical E2E separate |
| Multiple customer instances | Isolated DB/credentials/config/ports/resource versions and deployments; no multi-tenant control plane claimed |

No demonstrated technical reason to replace the server or client during the prototype. Legal clearance of the MuMain code itself remains a separate future product concern: asset replacement alone does not solve it.

Resource replacement boundary: runtime archive already omits Data/fonts and upstream publishes separate content-addressed packs. Keep this separation. Later packs must preserve expected format/path/IDs or provide conversion/mapping; not every arbitrary asset package is interchangeable without work. No architecture change implemented now.


### 2026-10-09 party membership recovery

run37879360808, artifact11593403578; saved party-accept.zip, authorized-user libfile_14d3ff11c6cc81919de262261fce9f58, SHA256 b6be122a32245dd47f6b1a4b880431b6f907981aafcf08f2a1ba49d0cff956b4. Genuine07/08 member lists and10 received trade request. No completed trade/DB persistence proof in this archive; active job final evidence will supersede it.

### Latest pre-trade persisted snapshot

run37879360808/artifact11594420323; party-trade-final.zip,23259299bytes,SHA256 58ac2b8bc1c916b83a660f2d881bc548096149ca2d921d0949ee90851bb93676; authorized-user libfile_5822066d47a481918d68a925818e17a3. Contains final DB/logs/screenshots. Core test0Dk stats/items unchanged; test300Dk repositioned to118,140. Trade UI opened but no transfer. Restore this for finite trade continuation; keep earlier run37860870710 as independent core checkpoint.

- Failed finite trade37881728154/artifact11595121043:9410516bytes, SHA2569707e0b09fe2cc01a37f1f2697083c08a25bf6f6d4df23fe7a88062e7bd71e93; authorized-user backup libfile_06af9997bb2481919f7df53072a65b14. Evidence only: do NOT promote its interrupted-trade DB over the clean baseline37879360808.

- Corrected failed trade37882579366/artifact11594978877:9420594bytes, SHA25673c4d78f48fde231a2b855b46f2363ba5be1038033589dde56083c5e54df26e5; authorized-user backup libfile_65ce7197607c8191bb0a9c01f69d018a. Includes consumed33-step plan, real screenshots13–16, final dump and assertion JSON. Evidence only; DO NOT promote interrupted DB.
