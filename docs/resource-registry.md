# Resource registry and stack freeze
Last verified: 2026-10-08. Canonical project record: ncuxonat7-oss/MuMain, docs/resource-registry.md.
Scope: current OpenMU/MuMain prototype; narrow resource evaluation only. No purchases, no server-engine comparison.

## CURRENT PROTOTYPE RESOURCES
### Current execution status
- OpenMU source: https://github.com/MUnique/OpenMU at d067b3c11c23c3145de6e2c76201ab9a93b267c8; local working tree clean at audit.
- Client fork: https://github.com/ncuxonat7-oss/MuMain at 8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5. Upstream code baseline: https://github.com/sven-n/MuMain at 21728b1e5b03e0763b38ef9e23f79645e0df7ad2. Fork changes are CI workflow changes.
- Successful Windows native x64 Release, editor OFF, no Data/fonts: https://github.com/ncuxonat7-oss/MuMain/actions/runs/37813650810. All 423 tests passed. Do not repeat without a runtime-driven reason.
- Artifact: mu-client-windows-native-x64-release-editor-off-no-data-main, artifact ID 11567737809; ZIP SHA256 eefe0a710518bc6536dd47cde45fb8605ae4ef5c7f4faca4095e8abb5f23297e. Source-built Main.exe and NativeAOT MUnique.Client.Library.dll, compiled shaders and dependencies.
- Server demo smoke run passed: existing Release DLL, .NET/ASP.NET runtime 10.0.11, flags -demo -autostart -adminpanel:disabled, TCP 44406 greeting c1040001. Process stopped after check. Demo uses memory persistence; this does NOT prove PostgreSQL works.
- No graphical client run, account/character creation through MuMain, or Lorencia entry proven. No Lorencia screenshot exists.

### Selected resource candidate — NOT YET USED
Source: https://github.com/sven-n/MuMain/releases/tag/data-4b0ab29c58b27fc4
Archive: https://github.com/sven-n/MuMain/releases/download/data-4b0ab29c58b27fc4/MuMain-data-4b0ab29c58b27fc4.tar.gz
Checksum sidecar: same URL with .sha256 suffix.
Size: 457104401 bytes. Free download. Contains Data/ and fonts/; release describes content-addressed resources.
Exact source trees at client baseline:
- src/bin/Data: 77f7830f542d106fc519c8821832d49a3dd8ae3a
- src/bin/fonts: 149f928e2547aa6658977c3f41c63abccfa471ed
- ID: first 16 hex characters of SHA256(dataTreeSHA + newline + fontsTreeSHA + newline).
Version: Season 5.2-derived client targeting Season 6 Episode 3, extended OpenMU protocol; not an arbitrary retail S6 client.
Technical fit: exact tree match to our build, best available immediate prototype candidate; actual runtime verification still pending.
Origin: published by the MuMain maintainer, with game resources traceable to the repository. Repository credits Webzen/Louis/community. This establishes distribution provenance, NOT a license from the original asset owner.
Rights: no root license or Data license granting use/modification/redistribution found in the inspected baseline tree. Models, maps, textures and audio have unresolved permissions. No claim that the package is proven stolen, malware or cracked software.
Gate: user requires stopping before use of a disputed resource. Archive has not been downloaded, extracted, attached to the client or redistributed. Obtain an explicit user decision on this exact package/risk, or find a compatible authorized replacement. A YELLOW label alone is not a gate; this specific user policy is.

### Fonts (license texts checked individually)
Source for each: https://github.com/sven-n/MuMain/tree/21728b1e5b03e0763b38ef9e23f79645e0df7ad2/src/bin/fonts
- Cousine: SIL OFL 1.1, Google 2010, reserved font name Cousine.
- Liberation Sans: SIL OFL 1.1; Google/Red Hat copyright and reserved font names.
- Nanum Gothic: SIL OFL 1.1, NHN 2010, reserved names.
- Noto Sans TC: included SIL OFL 1.1 text.
- DejaVu Sans: Bitstream Vera license; DejaVu changes public domain.
Commercial embedding/modification/redistribution allowed subject to each license's notices and naming/sale restrictions. Preserve all accompanying license files. Fonts do not authorize the game's Data. Nothing deployed yet.

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
| Data | Exact data-4b0ab29c58b27fc4; ready assets, not yet used | No verified game-content permission | YELLOW |
| Fonts | Above five families; ready font assets | OFL/Bitstream Vera texts verified; preserve notices | GREEN |
| .NET | Server net10.0 requires .NET/ASP.NET 10.0.0+; current portable runtime 10.0.11; CI setup-dotnet 10.0.x | Microsoft runtime/source licensing and redistribution notices apply; exact historical SDK patch not established | GREEN |
| PostgreSQL | Official Ubuntu portable PostgreSQL 16 packages; no initialized working database yet | PostgreSQL License; runtime blocked in current root-only execution environment | YELLOW (deployment) |
| EF/Npgsql | EF Core 10.0.2, Npgsql/provider 10.0.0 in existing server deps.json | Permissive upstream licenses; final dependency notices audit outstanding | GREEN |
| Other server dependencies | Serilog 4.3.0, BCrypt.Net-Next 4.0.3, BlazorInputFile 0.2.0; exact full set in deps.json and src/Directory.Packages.props | Transitive rights/security inventory not completed | YELLOW (release audit) |
| Windows toolchain | CI Visual Studio 18 Enterprise; MSVC 19.51.36260.0, tools 14.51.36231, Windows SDK 10.0.26100.0; CMake >=3.25, Ninja, vcpkg | Tool use and CRT redistribution governed by Microsoft terms; CRT staged in artifact | YELLOW (release/tool freeze) |
| SDL | submodule d9d5536704d585616d4db3c8ba3c4ff6fc2757e1; source-built | SDL zlib license; preserve license | GREEN |
| SDL3_ttf | a1ce3670aec736ecbf0936c43f2f0cc53aa61e5b, CI reports 3.2.2 | zlib; FreeType/HarfBuzz/plutosvg dependencies need notice inventory | YELLOW (transitive audit) |
| glm / spdlog / miniaudio | 1.0.1 / v1.15.3 / 9634bedb5b5a2ca38c1ee7108a9358a4e233f14d; source fetched by CMake | Permissive upstream licenses; preserve notices | GREEN |
| imgui | submodule 21d3299e588b5c702dcca0f448b4f937af369b4a; editor OFF, not needed by current build | MIT upstream | GREEN |
| Client build/runtime dependencies | vcpkg curl+SSL, OpenSSL, glslang, SPIRV-Cross, DXC; source/build packages and resulting DLLs/shaders | Exact package resolutions in successful CI log, vcpkg.json not baseline-pinned; per-package notices/runtime inventory outstanding | YELLOW (reproducibility/distribution) |
| GitHub Actions | Windows runner, proven compilation only; future runtime experiment not executed | Available CI route, desktop/GPU suitability not yet established | YELLOW (execution) |

Database blocker already tried: system apt install failed on protected package-cache path; portable initdb refuses root; only UID 0 is mapped; PRoot non-root emulation fails ptrace(TRACEME) operation not permitted. Do not attempt security bypass. A permitted Windows runner with PostgreSQL is the concrete next environment to test, not proof it already works.

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

## NEXT EXECUTION CHECKPOINT
1. Await user's decision ONLY on the exact disputed game Data package, per their current explicit policy; do not request a user-supplied link.
2. If authorized, download exact archive plus checksum, verify before extraction and inspect contents; never run added untrusted executables.
3. Reuse successful Windows runtime. Try permitted Windows CI instance with PostgreSQL and our pinned OpenMU; no needless repeat of 423 tests.
4. Establish real database persistence, client graphics, actual server connection, test account/character and Lorencia entry. Save authentic client screenshot/log evidence.
5. If real GPU/input automation requires a developer/control-socket build, explain the specific necessity first; existing player build has editor/control socket disabled.
6. Do not label a TCP probe or in-memory demo as completed E2E. No purchases, no external contacts/messages without explicit instruction.

