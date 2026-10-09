# Architecture — frozen working baseline

| Layer | Identity | Role / confirmed relationship |
|---|---|---|
| MuMain native client | fork ncuxonat7-oss/MuMain; validated build8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5; upstream21728b1e5b03e0763b38ef9e23f79645e0df7ad2 | Windows x64 Release, editor OFF; C++ client plus NativeAOT MUnique.Client.Library.dll and compiled shaders; S6E3 extended protocol |
| Data/fonts | maintainer release data-4b0ab29c58b27fc4; frozen trees/hashes in resource-registry.md | Separate replaceable resource package, not embedded server rules; unresolved game-content rights |
| OpenMU | MUnique/OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8, MIT | Existing source-built .NET10 Release runtime; SeasonSix initializer; modular handlers/plugins/configuration |
| PostgreSQL | actual successful Windows PG17.11 | Persisted accounts, characters, inventory and game configuration; EF/Npgsql. Restore saved database instead of reseeding progression |
| Runtime/test harness | existing GitHub manual workflows | Disposable localhost Windows session; real native graphics/input. Stop processes and preserve evidence/db in finally blocks |

Actual test flow: client → extended connect port44406 → game endpoint55902 → OpenMU → PostgreSQL5432. Loopback addresses and these ports are test fixtures, not public hosting. No permanent service/VPS has been deployed. No production authentication design is inferred from disposable localhost fixtures.

Resource/content separation: server defines behavior and IDs; client metadata/renderers/assets must match those IDs. Database foreign keys cannot verify client models, effects or event rules. A resource replacement does not implement missing server event logic.

Current source/build provenance: server net10.0; recorded runtime .NET/ASP.NET10.0.11, setup-dotnet10.0.x (historical SDK patch not fully frozen). EF Core10.0.2, Npgsql/provider10.0.0, Serilog4.3.0, BCrypt.Net-Next4.0.3, BlazorInputFile0.2.0. Exact dependency inventory remains in pinned Directory.Packages.props/deps.json. Windows build: VS18 Enterprise, MSVC19.51.36260.0/tools14.51.36231, SDK10.0.26100.0, CMake>=3.25/Ninja/vcpkg. No updates performed during this audit.

Client dependency identities: SDL d9d5536704d585616d4db3c8ba3c4ff6fc2757e1; SDL3_ttf a1ce3670aec736ecbf0936c43f2f0cc53aa61e5b (3.2.2); glm1.0.1; spdlogv1.15.3; miniaudio9634bedb5b5a2ca38c1ee7108a9358a4e233f14d; editor-OFF imgui21d3299e588b5c702dcca0f448b4f937af369b4a. vcpkg curl/OpenSSL, glslang, SPIRV-Cross and DXC resolution/notices need a future release inventory, not an immediate reconfiguration.

Future staging, incremental updater, diagnostics/API and rollback can be added around this structure. OpenMU extensibility suggests feasibility; these are INFERRED architectural possibilities, not implemented/verified product features. Native MU marketplace/offline progression/personalized customer deployment need scoped design and testing later.

Recovery: resource-registry.md lists exact sources, build/db artifacts, checksums, durable authorized-user backup references and expiry caveats. Current server is d067b3c plus patches/openmu-trade-money.patch, verified run37959672391. Prefer patched cache keyed by patch hash; fallback to verified patched-openmu-runtime artifact11630698202/private backup. Do not rebuild on cache miss. DataModel/schema/client/resources unchanged; normal cancellation and both relogs verified, disconnect/crash UNKNOWN. Original unpatched cache retained for historical comparison only.

