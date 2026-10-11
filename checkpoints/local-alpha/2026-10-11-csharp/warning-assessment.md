# Build-warning assessment

Assessment date: 2026-10-11 UTC. Scope: existing successful Startup build, bounded first-party image-use inspection, and the five advisory URLs emitted by that build. No build/test rerun, package update, exploit reproduction, or broad audit was performed.

## Result

- The build reported **247 warnings, 0 errors**. There are **43 warning codes**.
- The log prints the same 247 diagnostics during execution and again after `Build succeeded.`. The 494 raw warning lines must not be reported as 494 distinct warnings.
- ImageSharp produces **20 project/advisory diagnostics across four projects**, corresponding to **five distinct advisories: three high and two moderate**.
- The remaining 227 diagnostics are compiler/analyzer/UI warnings. Successful compilation does not dispose of either the security advisories or runtime-oriented warnings.

## ImageSharp advisories

The central pin is `SixLabors.ImageSharp` **2.1.11** (`src/Directory.Packages.props:66`); `SixLabors.ImageSharp.Drawing` remains **1.0.0** (line 67). The warning-bearing projects are Startup, Web/AdminPanel, Web/Map, and Web/Shared. Each emits all five advisories.

| Advisory | Severity / CVSS 3.1 | Affected versions | Listed patched version |
|---|---|---|---|
| [GHSA-gwg2-r3hj-4w44](https://github.com/advisories/GHSA-gwg2-r3hj-4w44) | moderate / 5.3 | >= 1.0.0-beta0001, <= 4.1.1 | 4.1.2 |
| [GHSA-j3p4-wp97-rph4](https://github.com/advisories/GHSA-j3p4-wp97-rph4) | high / 7.5 | >= 2.0.0, <= 4.1.1 | 4.1.2 |
| [GHSA-j9gm-c75j-xc9q](https://github.com/advisories/GHSA-j9gm-c75j-xc9q) | high / 7.5 | >= 2.0.0, <= 4.1.1 | 4.1.2 |
| [GHSA-jjfr-hcj7-qf5w](https://github.com/advisories/GHSA-jjfr-hcj7-qf5w) | high / 7.5 | >= 2.1.0, <= 4.1.1 | 4.1.2 |
| [GHSA-wmxv-xphr-5c9g](https://github.com/advisories/GHSA-wmxv-xphr-5c9g) | moderate / 5.3 | >= 2.0.0, <= 4.1.1 | 4.1.2 |

All five reviewed official records include the pinned 2.1.11 in their affected ranges. Scores describe the upstream vulnerability; they do not measure this application's demonstrated exposure.

- **ICC profile allocation (CVE-2026-106114):** Excessive allocation while parsing malformed ICC CLUT metadata. For ImageSharp v1-v3, the relevant public path accesses IccProfile.Entries after decode; automatic conversion applies to v4. The advisory demonstrates memory pressure, not unhandled process termination. [Source](https://github.com/advisories/GHSA-gwg2-r3hj-4w44).
- **Histogram equalization indexing (CVE-2026-106113):** Unsafe histogram indexing can terminate a process when a crafted floating-point TIFF is decoded as HalfVector4 and HistogramEqualization is applied. This is operation-specific, not a claim about every image load. [Source](https://github.com/advisories/GHSA-j3p4-wp97-rph4).
- **TIFF Group 3 encoder buffer (CVE-2026-106110):** TIFF CCITT Group 3 one-bit encoding can overrun its output buffer and terminate the process. Re-encoding TIFF with retained compression metadata can reach this path. [Source](https://github.com/advisories/GHSA-j9gm-c75j-xc9q).
- **TIFF Group 4 encoder buffer (CVE-2026-106115):** TIFF CCITT Group 4 one-bit encoding can write beyond its logical buffer. The advisory reproduces an unhandled exception during decode and re-encode; this assessment makes no remote-code-execution claim. [Source](https://github.com/advisories/GHSA-jjfr-hcj7-qf5w).
- **BigTIFF decoder non-progress (CVE-2026-106116):** A malformed BigTIFF entry count can keep one decoder thread busy without consuming input. The advisory demonstrates prolonged execution of one invocation, not worker-pool exhaustion. [Source](https://github.com/advisories/GHSA-wmxv-xphr-5c9g).

### Reachability evidence and limits

Bounded static search of first-party src C# and Razor files, excluding obj and bin, followed by inspection of ImageSharp use sites. No exploit execution or full call-graph audit.

- `src/Web/Shared/GameMapTerrainExtensions.cs:24`: Creates a fixed 256 x 256 Image<Rgba32> from terrain flags.
- `src/Web/Map/Map/GameMapTerrainExtensions.cs:23`: Creates a fixed 256 x 256 Image<Rgba32> from terrain flags.
- `src/Web/Map/Map/GameMapInfoExtensions.cs:80`: Writes the generated terrain bitmap with SaveAsPng.
- `src/Web/Shared/Components/ExitGatePicker.razor.cs:64`: Converts generated terrain image to PNG using PngFormat.Instance.
- `src/Web/Shared/Components/MapEditor/MapEditor.razor.cs:140`: Converts generated terrain image to PNG using PngFormat.Instance.

The bounded first-party search found no direct references to `Image.Load`, `Image.Identify`, `TiffEncoder`, `TiffCompression`, `HistogramEqualization`, `HalfVector4`, `IccProfile`.

**No direct route to these five vulnerable operations was established in the inspected first-party image uses. This is not proof of non-reachability or non-exploitability.**

- No inspection of third-party package internals, dynamically loaded plugins, reflection paths, or deployment network controls.
- No end-to-end trace from all input entry points; keyword search can miss aliases or indirect use.
- The build log is a point-in-time warning list, not an exhaustive current vulnerability scan.
- Existing successful builds and tests do not establish security of untested operations.

## Private alpha and future public exposure

**Private alpha:** These warnings do not by themselves invalidate an isolated private-alpha checkpoint. Continuing such a checkpoint is conditional on verified restricted access, trusted inputs/operators, no untrusted image decode or TIFF processing, bounded resources, and owner acceptance of remaining risk. Those deployment controls were not verified in this assessment.

**Future public exposure:** Do not treat successful build/tests as public-release security approval. Before public exposure, close the dependency-risk decision with a reviewed compatibility/remediation plan or defensible non-reachability evidence and compensating controls, and review the concrete runtime-oriented warnings. No public-readiness verdict is established here.

**Dependency decision:** The advisory-listed patched version 4.1.2 is factual reference information, not a recommendation to upgrade automatically. The current ImageSharp.Drawing 1.0.0 pin and API/runtime/license compatibility require a separate, approved evaluation. No dependency was changed.

## Other warnings that deserve focused review

- `VSTHRD101` (1): `src/Web/AdminPanel/API/ServerController.cs:93` uses an async lambda in a void-returning iteration delegate. Inspect exception handling and completion semantics; a warning alone does not establish an observed crash.
- `VSTHRD003` (2): `src/GameLogic/MiniGames/SkippableDelay.cs:94` and `src/GameLogic/NPC/GateNpc.cs:63` flag awaiting tasks outside their originating context. Deadlock behavior was not tested.
- `CA2265` (2): span/default comparisons in `src/GameServer/RemoteView/World/ObjectMovedPlugIn.cs:192` and `ObjectMovedPlugInExtended.cs:68` warrant intent review.
- `RZ10012` (1): `src/Web/AdminPanel/Components/Routes.razor:8` does not recognize `Pages.AccessDenied` as a component. Verify denial-page rendering. This warning is not evidence that authorization is bypassed.
- `ASP0006` (33) concerns render-tree sequence-number construction; `BL0007` (1) concerns the `MuItemStorage.SelectedItem` component parameter.
- The 85 StyleCop diagnostics and 72 XML-documentation compiler diagnostics primarily concern documentation/style or disabled XML analysis. `CS1591` alone contributes 68 warnings in generated `Resources.Designer.cs`.
- The remaining compiler diagnostics include obsolete APIs, hidden members, unused events, and ineffective optional-argument defaults. They need context-specific cleanup rather than being classified as vulnerabilities.
- `VSTHRD200` (2) is async-method naming, distinct from the runtime-oriented threading warnings above.

## Counts by warning code

The JSON report contains every sanitized diagnostic, original execution-log line, source location, project, all files per code, and all codes per file. `CSC` diagnostics have no source location, so they are keyed by their project.

| Code | Count | Affected files / project-scoped CSC entries |
|---|---:|---|
| ASP0006 | 33 | `src/Web/AdminPanel/Pages/EditAccount.razor.cs` (7); `src/Web/AdminPanel/Pages/EditConfig.cs` (9); plus 3 more (JSON) |
| BL0007 | 1 | `src/Web/ItemEditor/MuItemStorage.razor.cs` |
| CA2265 | 2 | `src/GameServer/RemoteView/World/ObjectMovedPlugIn.cs`; `src/GameServer/RemoteView/World/ObjectMovedPlugInExtended.cs` |
| CS0067 | 5 | `src/DataModel/Entities/AppearanceData.cs`; `src/GameLogic/NPC/SoccerBall.cs`; plus 3 more (JSON) |
| CS0108 | 5 | `src/GameLogic/MiniGames/ImperialGuardian/ImperialGuardianContext.cs`; `src/Persistence/Initialization/Updates/FixEventItemsDropFromMonstersUpdatePlugIn095d.cs` (2); plus 1 more (JSON) |
| CS0612 | 1 | `src/Web/Map/Program.cs` |
| CS0618 | 8 | `src/Persistence/EntityFramework/Json/JsonQueryBuilder.cs`; `src/Persistence/EntityFramework/ModelExtensions.cs` (2); plus 5 more (JSON) |
| CS1066 | 9 | `src/Persistence/EntityFramework/CachedRepository{T}.cs` (2); `src/Persistence/EntityFramework/ConfigurationTypeRepository.cs` (2); plus 3 more (JSON) |
| CS1570 | 2 | `src/Web/AdminPanel/Pages/NetworkAnalyzer.razor.cs` (2) |
| CS1574 | 2 | `src/GameServer/DefaultTcpGameServerListener.cs`; `src/Web/AdminPanel/Auth/AdminPolicies.cs` |
| CS1591 | 68 | `src/Web/Shared/Properties/Resources.Designer.cs` (68) |
| NU1902 | 8 | `src/Startup/MUnique.OpenMU.Startup.csproj` (2); `src/Web/AdminPanel/MUnique.OpenMU.Web.AdminPanel.csproj` (2); plus 2 more (JSON) |
| NU1903 | 12 | `src/Startup/MUnique.OpenMU.Startup.csproj` (3); `src/Web/AdminPanel/MUnique.OpenMU.Web.AdminPanel.csproj` (3); plus 2 more (JSON) |
| RZ10012 | 1 | `src/Web/AdminPanel/Components/Routes.razor` |
| SA0001 | 2 | `CSC [src/Annotations/MUnique.OpenMU.Annotations.csproj]`; `CSC [src/SourceGenerators/MUnique.OpenMU.SourceGenerators.csproj]` |
| SA1100 | 1 | `src/Persistence/InMemory/InMemoryRepositoryProvider.cs` |
| SA1101 | 2 | `src/GameLogic/AttackableExtensions.cs`; `src/Persistence/Initialization/Updates/IConfigurationUpdatePlugIn.cs` |
| SA1108 | 7 | `src/GameLogic/Player.cs`; `src/GameLogic/PlayerActions/Skills/DrainLifeSkillPlugIn.cs`; plus 4 more (JSON) |
| SA1118 | 2 | `src/Web/AdminPanel/Auth/AdminLoginService.cs`; `src/Web/AdminPanel/Auth/AdminPanelAuthExtensions.cs` |
| SA1124 | 3 | `src/GameLogic/PlayerActions/Craftings/RefineStoneCrafting.cs`; `src/Persistence/Initialization/Skills/MagicEffectNumber.cs` (2) |
| SA1129 | 1 | `src/Web/Shared/Components/Form/ValueTable.razor.cs` |
| SA1201 | 6 | `CSC [src/GameLogic/MUnique.OpenMU.GameLogic.csproj]`; `src/Network/IpAddressResolverFactory.cs`; plus 4 more (JSON) |
| SA1202 | 7 | `src/GameLogic/CastleSiege/CastleSiegeContext.cs` (3); `src/GameLogic/PlayerMapTransitions.cs`; plus 3 more (JSON) |
| SA1203 | 2 | `src/Web/Shared/Services/BotAccountService.cs`; `src/Web/Shared/Services/LoggedInAccountService.cs` |
| SA1204 | 8 | `src/GameLogic/Bots/BotFeaturePlugIn.cs`; `src/GameLogic/Bots/BotGenerator.cs`; plus 6 more (JSON) |
| SA1208 | 1 | `src/Web/AdminPanel/WebApplicationExtensions.cs` |
| SA1210 | 1 | `src/Web/AdminPanel/Components/Layout/ConfigurationSearch.razor.cs` |
| SA1211 | 1 | `src/GameServer/RemoteView/CastleSiege/CastleSiegeMachineRegionNotifyPlugIn.cs` |
| SA1214 | 2 | `src/Persistence/EntityFramework/AdminAuth/AdminUserRepository.cs`; `src/Web/AdminPanel/Pages/Captions.razor.cs` |
| SA1402 | 5 | `src/Web/AdminPanel/Auth/AdminAccessRequirement.cs`; `src/Web/AdminPanel/Auth/AdminLoginService.cs`; plus 3 more (JSON) |
| SA1413 | 9 | `src/Persistence/EntityFramework/Migrations/20260930044257_AddGensMember.cs`; `src/Persistence/EntityFramework/Migrations/20261001002816_AddGensAbuse.cs`; plus 3 more (JSON) |
| SA1507 | 1 | `src/Web/AdminPanel/Pages/NetworkAnalyzer.razor.cs` |
| SA1513 | 1 | `src/PlugIns/PlugInProxyTypeGenerator.cs` |
| SA1514 | 2 | `src/Persistence/EntityFramework/DatabaseConnectionStringHelper.cs` (2) |
| SA1515 | 3 | `src/GameLogic/MiniGames/MiniGameContext.cs`; `src/GameLogic/PlayerMapTransitions.cs`; plus 1 more (JSON) |
| SA1600 | 1 | `src/Network/LocalOnlyBinding.cs` |
| SA1623 | 1 | `src/GameLogic/Bots/BotStartupProfile.cs` |
| SA1625 | 2 | `src/Web/AdminPanel/Auth/AuthEndpoints.cs`; `src/Web/AdminPanel/Auth/UnavailableApiKeyRepository.cs` |
| SA1633 | 11 | `src/Persistence/EntityFramework/Migrations/20260813000114_AddSystemConfigurationTimeZoneId.cs`; `src/Persistence/EntityFramework/Migrations/20260819100503_AddConstValueAttributeAggregateType.cs`; plus 9 more (JSON) |
| SA1649 | 3 | `src/PlugIns/AsyncEventHandler.cs`; `src/Web/AdminPanel/Auth/AdminLoginService.cs`; plus 1 more (JSON) |
| VSTHRD003 | 2 | `src/GameLogic/MiniGames/SkippableDelay.cs`; `src/GameLogic/NPC/GateNpc.cs` |
| VSTHRD101 | 1 | `src/Web/AdminPanel/API/ServerController.cs` |
| VSTHRD200 | 2 | `src/Persistence/EntityFramework/AdminAuth/AdminUserRepository.cs`; `src/Web/AdminPanel/Auth/AdminPanelAuthExtensions.cs` |

## Reproducibility and publication boundary

- Input: `phase2129-csharp-build/build-startup.log`.
- Input SHA-256: `4f53e0d4ba55882f49c962810fece56eaad454704bbdb7066c59dc886fb7db7f`.
- Companion: `warning-inventory.json`.
- Only this report and its JSON companion are intended for review as publication candidates. They include repository-relative source paths and diagnostic text, with no absolute workspace/user paths, credential values, private certificate paths, database content, or copied raw build log.
- This report is a point-in-time assessment of the emitted warnings. It does not claim that every dependency or vulnerability has been examined.
