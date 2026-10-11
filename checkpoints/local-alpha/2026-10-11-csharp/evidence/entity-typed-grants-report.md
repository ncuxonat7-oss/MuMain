# Entity/Typed bounded least-privilege findings

Pin: OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8. Source-only review, local evidence output. No database, secrets, runtime, build, install, implementation edits or publication.

## Decision

Keep the executable grant-profile/activation blocker. This review establishes a concrete lower bound of observed operations, not a complete minimum grant profile. Unresolved read/navigation closure and feature scope cannot safely be filled by generic schema-level DML.

The old assumption that Entity/Typed can simply be read-only is false for the full pinned runtime: ordinary Startup.Program conditionally creates missing plugin configurations through EntityDataContext and fills missing custom configuration through TypedContext. Kanturu/Bot runtime features subsequently update persisted plugin custom configuration. This does NOT justify writes to all configuration tables.

## Observed operation matrix

All schema identifiers/table mappings were checked against full latest game migration target model blob6998fddb12645ba0a3e44340a6c75049c5fbad16. Operations describe source call paths, not privileges already granted or tested.

| Context | Object | Observed operations | Condition / evidence |
|---|---|---|---|
| Entity | public.__EFMigrationsHistory | SELECT | PersistenceContextProvider existence/currentness checks |
| Entity | config.GameConfiguration | SELECT | ConfigurationExists plus startup missing-plugin loading; graph reads also needed |
| Entity | config.SystemConfiguration.AutoUpdateSchema | SELECT column | ShouldDoAutoSchemaUpdateAsync raw query |
| Entity | config.PlugInConfiguration | INSERT | Startup.Program lines511–542 inserts missing known plugins, attaches existing game configuration |
| Entity | config.PlugInConfiguration | UPDATE | KanturuTowerWindow lines49–64; BotFeaturePlugIn lines658–669; BotsController lines113–125 call SetConfiguration and save |
| Typed | config.PlugInConfiguration | SELECT; conditional UPDATE | Startup.Program lines426–454 fills missing custom configurations; no evidence for DELETE |
| Typed | config.SystemConfiguration | SELECT | Startup.Program lines683–684 and NetworkObservationExtensions lines80–81; no runtime-write grant inferred |
| Typed | data.GensAbuse | SELECT, DELETE | GensRankingPlugIn lines79–91 removes expired abuse rows |
| Typed | data.GensMember | SELECT, UPDATE Rank/RankingPosition | GensRankingPlugIn lines127–146 |
| Typed | data.MiniGameRankingEntry | INSERT | MiniGameRewardService lines107–123 |
| Typed | data.CastleSiegePendingReward | INSERT | CastleSiegeRewardDelivery lines62–73 |
| Typed | data.CastleSiegeData | SELECT, INSERT, UPDATE | CastleSiegeContext lines422–427,871–879 |
| Typed | data.CastleSiegeGuild | SELECT, INSERT, DELETE | CastleSiegeContext lines437–461 |
| Typed | data.CastleSiegeNpcState | SELECT, INSERT, UPDATE, DELETE | CastleSiegeContext lines487–511 |
| Typed | data.CastleSiegeGuildRegistration | SELECT, INSERT, UPDATE, DELETE | CastleSiegeContext lines519–525,674–728 |

Feature-specific rows are conditional capabilities. This review does not prove that Gens, castle, minigame, Kanturu or bot branches are enabled in the exact local baseline. Conversely, absence of a feature from a short historical smoke test does not prove it cannot execute later.

Schema USAGE and database CONNECT are prerequisites for any approved object grant. No admin-schema access, runtime ownership, CREATE, migration privileges, history writes, sequence grants, function grants or privilege inheritance are derived here.

Column-level UPDATE on CustomConfiguration is a promising reduction for the config update paths, but this report does not certify emitted EF SQL/change-tracker closure. Table-wide UPDATE would permit changing CustomPlugInSource/ExternalAssemblyName/IsActive too, so do not silently broaden to it. Missing-plugin INSERT similarly includes plugin activation and configuration fields; exact required columns and nullable/default behavior need emitted-operation evidence or a reviewed static proof.

## Why no complete executable grant profile

1. Entity startup calls GetAsync<GameConfiguration>, whose GameConfigurationRepository uses GameConfigurationJsonObjectLoader/JsonObjectLoader. The latter builds SQL from model navigation metadata and reads whole object graphs. SELECT on GameConfiguration alone is demonstrably an incomplete description. The exact read closure has not been computed.
2. GenericRepositoryBase eagerly traverses navigation/collection references through repositories. GenericRepository creates a TypedContext for T when no current context exists. Thus direct CreateNewTypedContext searches do not exhaust typed runtime access.
3. TypedContext selects edit types, aggregate members, back-references and additional read-only types from CompleteModel. The compiled-type list includes SystemConfiguration/PlugInConfiguration plus game data, but a compiled list is not an exclusive runtime allowlist.
4. EntityFrameworkContextBase saves tracked changes and aggregates; operation roots do not prove every emitted table/column. INSERT on a plugin with GameConfigurationId is visible in model; unrelated GameConfiguration UPDATE is not justified simply because the existing parent is attached.
5. Neither source search nor generic editing APIs establish that every supported table is exercised by the authorized local runtime. No blanket game-schema DML is defensible as minimum privilege.
6. Latest full target model yields 119 tables across config/data/friend/guild. This is model inventory only, explicitly not a grant allowlist or compiled-runtime proof. No admin table appears there. Its model-level UseIdentityByDefaultColumns is not evidence of an actual required sequence; catalog/default/trigger effects remain unchecked.
7. Admin editing endpoints have broader editing capabilities but are outside the requested narrow startup/game baseline grant inference; granting them implicitly would expand scope.

Stop condition met: completing exact minimum privileges would require further read-closure computation, enabled-feature baseline evidence and binary-aligned validation. Parent is retaining real setup blocking pending separate approval/validation; this report should not weaken it.

## Evidence and source hashes

All paths below are in MUnique/OpenMU at the pin above. Source URLs are https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/ plus path.

- src/Persistence/EntityFramework/PersistenceContextProvider.cs — 42f42e3ef00f2fe3741d92bf8ee0c2ca8e0dae87
- src/Persistence/EntityFramework/EntityFrameworkContextBase.cs — 9ad677ddefcf426389e6be8e2de0853d2bc019ae
- src/Persistence/EntityFramework/GenericRepository.cs — f3bfeb2ca6c0c6b379cab24bc4c53a39b8a9b802
- src/Persistence/EntityFramework/GenericRepositoryBase.cs — cc97af90ab1a91b3aad9959bd99a41952ed49507
- src/Persistence/EntityFramework/RepositoryProvider.cs — 1cc3e01d93a2c0859e8942eba66b0120e45c04a1
- src/Persistence/EntityFramework/GameConfigurationRepository.cs — 3d45474a8b7c844b359761d529b4e74d2827ba53
- src/Persistence/EntityFramework/Json/GameConfigurationJsonObjectLoader.cs — 144048db5d77214835f91762ebfa5ca6cb60c391
- src/Persistence/EntityFramework/Json/JsonObjectLoader.cs — f4eb2b80357240c81b677eaf862fdfbb91b3ee31
- src/Startup/Program.cs — 6100b973211af3cc67546ec5f64b8a7686db982b
- src/GameServer/NetworkObservationExtensions.cs — d19ea7e6a75851e016f166a21969b93b30a635e7
- src/GameLogic/Gens/GensRankingPlugIn.cs — 281f25b92bd05d896db7b065d1b303de71cbd299
- src/GameLogic/MiniGames/MiniGameRewardService.cs — 648b98a56cc3114fd2cc3538d7f92c5af6ce2658
- src/GameLogic/CastleSiege/CastleSiegeRewardDelivery.cs — 470abca2df1369c9b3c78699e7b289f7fa783ed0
- src/GameLogic/CastleSiege/CastleSiegeContext.cs — 14bf7948b186c253c9a067c4cd500cec2ef96d3c
- src/GameLogic/MiniGames/Kanturu/KanturuTowerWindow.cs — 1a00b54a295581e5f1fa222a4541213534f48bba
- src/GameLogic/TestActors/BotsController.cs — e46ad9c123f476fc0e8e19a3d0ad5725c05c22a6
- src/GameLogic/Bots/BotFeaturePlugIn.cs — 27bbeb75dce470a9c64b9afc329942e2dcc1c974
- src/Persistence/EntityFramework/Migrations/20261006212931_AddCashShop.Designer.cs — 6998fddb12645ba0a3e44340a6c75049c5fbad16
- src/Persistence/EntityFramework/TypedContext.cs — 72bf17534a42f6ee719758fe0de32da463d1461e (phase2033 preserved source)
- src/Persistence/EntityFramework/ConnectionConfigurator.cs — 1c0f904695963acd9a98e03056863fc18c3a5868 (phase2006/2033 preserved source)

Evidence outputs:
- entity-typed-observed-contract.json: machine-readable lower-bound operations; executable=false, activationAllowed=false.
- entity-typed-callpath-source-reads.json, entity-typed-runtime-source-reads.json, typed-compiled-context-source-reads.json: full pinned connector source responses.
- latest-game-model-full-source.json and entity-final-migration-model.cs: full latest migration target model. Earlier phase2006 migration reads preserved only attribution headers; no grant conclusion used those header excerpts as full model evidence.
- entity-typed-table-allowlist.json: legacy filename, explicitly labeled MODEL INVENTORY ONLY in contents; 119 mappings, not grant authority.

GitHub code search was used only to discover candidate paths at default HEAD. Every substantive code finding above was then fetched at the exact pin; search snippets were not treated as pinned evidence. This was a bounded task-focused sample, not an exhaustive audit of all runtime call sites.
