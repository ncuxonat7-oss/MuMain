# Startup read connection attribution — 2026-10-12

**PASS for source attribution of the three scoped reads; PARTIAL for the broader startup profile.** This bounded follow-up starts at `a972354429cfe7aed506486f9e7cbc853d75bc29`. It reuses the [saved candidate metadata and reconciliation](metadata-inspection/RECONCILIATION.txt), whose 18 files were previously fetched back and verified unchanged. No candidate, application, database, compiler, tests, migrations, grants or workflows ran in this follow-up. No original connection file, credential bundle or environment values were read.

## Path → context → connection → intended role

All rows describe the pinned EF persistence provider, not the `-demo` in-memory branch. Context keys below have namespace `MUnique.OpenMU.Persistence.EntityFramework`. Intended roles come only from the disabled `Prepare-MuSetupAcceptance` template in `scripts/windows11/FirstSetup.ps1:279`.

| Identified read | Proven context / connection key | Intended setup role | Scope and condition |
|---|---|---|---|
| `Program.CreateMissingPlugInConfigurations` → `CreateNewContext()` → `GetAsync<GameConfiguration>()` | `EntityFrameworkContext` wraps `EntityDataContext`; key `EntityDataContext` | `mu_entity` | Conditional on missing known plugins. `GameConfigurationRepository.GetAllAsync` uses the current context's database connection and JSON loader. The saved 69 full-row + 12 join projection belongs to this root; it is not a grant profile. |
| `Program.PlugInConfigurationsFactory` → `CreateNewTypedContext(typeof(PlugInConfiguration), false)` → `GetAsync<PlugInConfiguration>()` | `PlugInConfigurationTypedContext`; normalized key `TypedContext` | `mu_typed` | Generic repository retains the current context. Saved candidate plugin root: 7 columns, zero outgoing navigations. The conditional fallback in `LoadPlugInConfigurationsAsync` creates the same Typed context. |
| `Program.ReadSystemConfigurationAsync` → `CreateNewTypedContext(typeof(SystemConfiguration), false)` → `GetAsync<SystemConfiguration>()` | `SystemConfigurationTypedContext`; normalized key `TypedContext` | `mu_typed` | Generic repository retains the current context. Saved candidate system root: 12 columns, zero outgoing navigations. |
| Already identified reference-handler default-ID lookup: `CreateNewConfigurationContext()` → `GetDefaultGameConfigurationIdAsync()` | `GameConfigurationContext` wraps `ConfigurationContext`; key `ConfigurationContext` | `mu_config` | Selects GameConfiguration.Id only. Sharing EntityDataContext's compiled model does not select its connection. The subsequent `dataSource.GetOwnerAsync(id)` is not assigned a role by this row. |

## Why these keys are proven

Pinned `Program.CreateHostAsync` initializes `ConfigFileDatabaseConnectionStringProvider` (line 253). `PersistenceContextProvider.CreateNewContext`, `CreateNewConfigurationContext` and `CreateNewTypedContext` construct the contexts listed above. `EntityFrameworkContextBase.GetAsync` pushes its context onto the repository context stack; `GenericRepository.GetContext` reuses that context when present rather than creating another Typed context. `GameConfigurationRepository` explicitly opens the current context's database connection; JSON model selection does not replace that connection.

`EntityDataContext.OnConfiguring` calls `ConnectionConfigurator.Configure`. Configure selects `typeof(TypedContext)` for any Typed subclass, otherwise the actual context type (and normalizes generic types). It passes the selected setting's connection string to `UseNpgsql`. `ConfigurationContext` inherits this configuration and then selects the shared compiled model. The saved patched ConnectionConfigurator adds the admin schema-mode accessor; its connection-key selection is the same as the pinned source. Its `DatabaseRole.Admin` enum entry points to EntityDataContext and must not be confused with the separate AdminPanelContext or interpreted as evidence of a PostgreSQL role's privileges.

The file provider reads ConnectionSettings.xml beside the persistence assembly, resolves each context name to a Type and performs an exact dictionary lookup. There is no base-type connection fallback after Configure's explicit Typed normalization; a missing key throws. The source helper may replace Server through DB_HOST. Its DB_ADMIN_USER/DB_ADMIN_PW substitutions are restricted to connection strings containing the exact postgres user token; they do not rewrite the setup template's mu_entity/mu_typed/mu_config identities. No environment values were inspected.

These facts prove source selection and template intent only. They do not prove which XML/provider is deployed, runtime session identity, candidate/package alignment, ACLs or successful reads. No actual database username is asserted. Setup policy, runtime-grant and launch fences remain unchanged and blocked.

## Precise remaining gap and one next step

The already observed `GameConfigurationDataSource`/custom-reference paths cannot yet be attributed: Program constructs that object in the plugin factory, registers a shared data source, and calls `GetOwnerAsync` in the reference-handler path; `LoadPlugInConfigurationsAsync` may call its `ForceDiscardChangesAsync` and `GetOwnerAsync`. The class implementation and inherited owner-loading context creation were not located in this bounded stage. Targeted immutable-file requests for `src/Web/AdminPanel/GameConfigurationDataSource.cs` and `src/Web/Shared/GameConfigurationDataSource.cs` returned 404. Those results do not prove the class is absent. No blocked API directory listing was retried or bypassed.

**Single next step:** locate the pinned GameConfigurationDataSource definition and its inherited GetOwnerAsync implementation, then trace only these already identified calls to their context/connection key using source. Keep complete Entity/Typed permission closure, executable grants, setup activation and Windows/full Alpha readiness blocked. No new candidate execution or database work follows from this report.

[Provenance](connection-attribution-provenance.json) records source pins, byte sizes, SHA256 and Git blobs, including the two failed exact-path lookups. The earlier startup-read report and all 18 metadata files retain their original bytes; their old missing-metadata/publication-next-step notes are historical and superseded by this checkpoint.
