# Startup GameConfiguration reads — bounded static result

**PARTIAL: a pinned necessary read list is established; complete read closure is not.** Owner approved this source/saved-evidence continuation at 2026-10-12 03:17:58 UTC. This completes the approved source/saved-evidence analysis, not the permission gate. No database, migration, grant, assembly loading, build, test, Windows/workflow or write-closure work occurred. Existing activation fences remain unchanged.

The [machine-readable list](evidence/startup-read-contract.json) supplies every selected table/column, model line ranges, conditional projections and unresolved boundaries. [Provenance](evidence/startup-read-provenance.json) pins 17 consumed source files at OpenMU `d067b3c11c23c3145de6e2c76201ab9a93b267c8` plus five saved evidence files. The source model's selected columns match the already saved diagnostic schema. This is static source/model evidence, **not proof that the candidate's generated/compiled query model has identical navigations**. No 119-table inventory was promoted into grant authority.

## Paths and read requirements

1. `Program.CreateMissingPlugInConfigurations` calls CreateNewContext → GetAsync<GameConfiguration> → the registered GameConfigurationRepository → GameConfigurationJsonObjectLoader. In the inspected startup path this happens only after known plugins are found missing (Program426–454,507–514). Empty results do not turn the composed query into a root-table-only query. Other GameConfigurationDataSource calls exist, but this review does not assign their connections to the Entity role without evidence.
2. The JSON builder uses `alias.*` for each expanded entity. A one-to-many collection always reads its dependent table: a nonaggregate reads its key/FK, an aggregate reads the full row and recursively adds navigations. An ordinary reference may read only the parent's FK as a JSON `$ref`; inverse/shadow references can be skipped. Many-to-many handling reads join columns rather than automatically selecting the target entity. Recursion stops adding navigations at alias h (next alias i). These rules prohibit inferring reads from a generic transitive FK graph. See [builder64–94](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/Persistence/EntityFramework/Json/JsonQueryBuilder.cs#L64), [references103–143](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/Persistence/EntityFramework/Json/JsonQueryBuilder.cs#L103), and [collections146–223](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/Persistence/EntityFramework/Json/JsonQueryBuilder.cs#L146).
3. Startup reads PlugInConfiguration and SystemConfiguration with `CreateNewTypedContext(type,false)`. The generic repository materializes Set<T> and then enumerates navigations. In the pinned migration model neither selected entity has an outgoing navigation. PlugInConfiguration's incoming GameConfiguration collection can cause the parent type to be included in a TypedContext model; **model inclusion alone does not execute a parent query**. GenericRepository preserves the current context when present. Thus these two scalar-root reads do not establish a recursive TypedContext GameConfiguration load. Compiled typed-model parity remains unproven.

### Exact static root columns

`config.GameConfiguration`: Id, AreaSkillHitsPlayer, CashShopConfigurationId, CastleSiegeConfigurationId, CharacterNameRegex, ClampMoneyOnPickup, DamagePerOneItemDurability, DamagePerOnePetDurability, DuelConfigurationId, ExcellentItemDropLevelDelta, ExperienceFormula, ExperienceRate, HitsPerOneItemDurability, InfoRange, ItemDropDuration, LetterSendPrice, MasterExperienceFormula, MasterExperienceRate, MaximumCharactersPerAccount, MaximumInventoryMoney, MaximumItemOptionLevelDrop, MaximumLetters, MaximumLevel, MaximumMasterLevel, MaximumPartySize, MaximumPasswordLength, MaximumVaultMoney, MinimumMonsterLevelForMasterExperience, PreventExperienceOverflow, RecoveryInterval, ShouldDropMoney. These are the 31 physical columns in the pinned saved schema; `alias.*` means a future schema change requires reevaluation.

`config.PlugInConfiguration` Typed root: Id, CustomConfiguration, CustomPlugInSource, ExternalAssemblyName, GameConfigurationId, IsActive, TypeId (7 mapped columns).

`config.SystemConfiguration` Typed root: Id, AutoStart, AutoUpdateSchema, IpResolver, IpResolverParameter, NetworkAnalyzerLiveBufferSize, NetworkObservationArchivePath, NetworkObservationMaxSessionSizeMb, NetworkObservationMaxTotalSizeMb, NetworkObservationRetentionDays, ReadConsoleInput, TimeZoneId (12 mapped columns).

### Proven first-hop minimum under the pinned model

Every row below needs at least `Id` and `GameConfigurationId` when the JSON GameConfiguration query is composed. All are schema `config`, single-column PK `Id` and one-to-many relationships. This minimum is **insufficient** if the generated navigation is aggregate: full-row columns and deeper reads then apply. The JSON records each table's exact full-row column alternative without authorizing it.

| Root navigation | Table |
|---|---|
| RawAttributes | AttributeDefinition |
| RawGlobalAttributeCombinations | AttributeRelationship |
| RawCharacterClasses | CharacterClass |
| RawGlobalBaseAttributeValues | ConstValueAttribute |
| RawDropItemGroups | DropItemGroup |
| RawMaps | GameMapDefinition |
| RawItems | ItemDefinition |
| RawItemLevelBonusTables | ItemLevelBonusTable |
| RawItemOptionCombinationBonuses | ItemOptionCombinationBonus |
| RawItemOptions | ItemOptionDefinition |
| RawItemOptionTypes | ItemOptionType |
| RawItemSetGroups | ItemSetGroup |
| RawItemSlotTypes | ItemSlotType |
| RawJewelMixes | JewelMix |
| RawMagicEffects | MagicEffectDefinition |
| RawMasterSkillRoots | MasterSkillRoot |
| RawMiniGameDefinitions | MiniGameDefinition |
| RawMonsters | MonsterDefinition |
| RawPlugInConfigurations | PlugInConfiguration |
| RawSkills | Skill |
| RawWarpList | WarpInfo |

### Conditional paths and exclusions

The root's three references target config.CashShopConfiguration, config.CastleSiegeConfiguration and config.DuelConfiguration. The parent's corresponding FK columns are already in the 31-column root projection. Target full-row reads depend on real/nonshadow aggregate navigation metadata; they cannot be asserted merely because a foreign key exists. Likewise, a feature being disabled does not prove its table is absent from a statically composed aggregate query. All 24 base GameConfiguration navigation properties have MemberOfAggregate annotations; the bridge to the generated persistent Raw* navigation flags was not established from the available saved metadata.

Missing-plugin/custom-configuration paths are conditional on stored configuration and plugin discovery. The ByDataSourceReferenceHandler can resolve additional game configuration references; exact activation and connection attribution are not proven here. No grants for Gens/castle state, minigame statistics, bot behavior, accounts, guild/friend tables or admin editing follow from this report.

The already observed Entity startup probes remain separate: ConfigurationExistsAsync uses AnyAsync on GameConfiguration (existence only; exact emitted minimal-column permission not captured), ShouldDoAutoSchemaUpdateAsync explicitly reads only SystemConfiguration.AutoUpdateSchema, and EF history checks read public.__EFMigrationsHistory. Their earlier evidence is reused, not retested or expanded into whole-row authority.

## Precise remaining fact and first-deployment impact

The saved compiled metadata proves 63+2 migration IDs/contexts and candidate DLL identity `f12b509a…437014`; it does not contain the runtime navigation graph, navigation PropertyInfo/MemberOfAggregate results, FK shadow status, join ordering or the selected compiled TypedContext projection. The migration designer supplies relational mappings but cannot by itself certify those CLR/runtime decisions. Expected persistent-model source paths returned404; this does not prove the source is absent elsewhere. One narrow extension-directory lookup at api.github.com was blocked by proxy403; that route was stopped without retry, alternate discovery or network expansion.

This result rules out root-only Entity SELECT as a sufficient profile, records the exact first-hop minimum, and prevents treating Typed model membership or every FK target as an executed read. It does **not** close recursive read permissions, write permissions, enabled-feature scope, source/package alignment or Windows acceptance. No GRANT SQL is emitted; setup/launch remain disabled and the readiness score is unchanged.

**Single next unfinished step:** obtain a pinned, navigation-only metadata export from the existing candidate for GameConfiguration and its reachable graph plus the PlugInConfiguration/SystemConfiguration compiled TypedContext models. Required fields: schema/table/property-column mapping, PK/FK order, IsCollection, declaring/target type, PropertyInfo presence, shadow status, aggregate/back-reference flags and model identity. Prefer an existing saved export; if none exists, a separate approval is needed for an offline candidate inspection method. No database connection, new build, grant change or feature audit is implied. Success is enough metadata to deterministically apply the existing query-builder rules, or a precise reason it cannot be obtained; further speculative grants are not a substitute.
