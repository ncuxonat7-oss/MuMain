# Two-context database guard candidate (local, disabled)

Update20:30UTC: all40 prepared mock-only PowerShell cases actually PASS in the
approved portable Linux7.4.20 runtime, and the guards are now integrated in a
new disabled control. See windows11-database-guard-integration.md. The original
phase-specific NOT_RUN/source-only statements below remain historical evidence;
real Windows/PostgreSQL acceptance and DB first-setup implementation remain open.

This phase changes only read-only guard/source-contract logic and focused tests.
No PostgreSQL command, restore, SQL mutation, migration, grant, credential, Windows
program, installer, server/client build or external publication ran. Existing
packaged controls and old source trees remain unchanged.

## Independently established expectations

OpenMU source is pinned to d067b3c11c23c3145de6e2c76201ab9a93b267c8. The untruncated
Git tree and actual Migration/DbContext attributes establish 63 EntityDataContext
and 2 AdminPanelContext migration IDs. Static PE/CLR metadata of the staged
MUnique.OpenMU.Persistence.EntityFramework.dll independently yields exactly the
same 65 nonabstract Migration subclasses and context associations. The DLL was
parsed as bytes, never loaded/executed. Its SHA256 is
f05e117d596f6bb74f953d8b4cbe83c73c0b30a6acf94876b6e8619bf92f1042.
The launcher now pins that DLL's expected inventory hash as well as its existing
full runtime/archive gates. Source includes initial lowercase .designer.cs and
three standalone attributed migrations; filename counting alone was not used.

AdminPanelContext explicitly uses admin.__EFMigrationsHistory. EntityDataContext
leaves history schema unspecified; PostgreSQL search_path controls resolution.
The candidate targets public.__EFMigrationsHistory and checks unqualified history
resolution in a fresh connection using each actual credential's role/database
settings. It preserves search_path only for the fully catalog-qualified history
probe; other probes retain search_path=pg_catalog. A shadowed/missing history
fails closed. No schema or role settings are changed.

The preserved baseline archive11651520969 already existed locally. Actual bytes
match archive SHA256 b40fbdbdb5c3bd9630331e0b9cb3bc7c1860db041a928bb976555635e03f79ea.
Its baseline-config.jsonl hashes to
8bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a, and dump member hashes
to 0a4b0744cb9be77c8f53a6f4a73e729402d17382069ba93261d394cbadf19478. No download or
DB tooling was needed. Safe selected fields establish GameConfiguration ID
00000001-0001-0000-0000-000000000000, SystemConfiguration ID
00000010-0000-0000-0000-000000000000, and expected endpoint port inventory.

Important: this original baseline has AutoUpdateSchema=true and
ReadConsoleInput=false. The safe persistent-launch requirements are false and
true respectively. This phase preserves that mismatch and refuses launch; it
does not silently modify the baseline or weaken the gate. Previous disposable
console-flag permission is not approval for either persistent configuration delta.

## Candidate contract and checks

The approved launch manifest schema is now 2 in this source candidate. Database
migrationSchema/migrationIds are replaced by migrationHistories keyed exactly by
EntityDataContext and AdminAuth.AdminPanelContext, each with schema/table/ids.
A fixed-hash database-source-contract.json independently binds these expectations,
configuration IDs, system ID, endpoints and persistence assembly identity. The
manifest cannot supply a different allowlist to bless an observed database.
Null, scalar, duplicate, missing, extra or swapped identities are rejected.
The probe identity must be separate from the listed runtime roles.

Each history is checked twice: under the probe and under its own context's actual
credential. The game snapshot is also checked under EntityDataContext, as before.
Both MigrationId and ProductVersion are selected because EF reads both via
GetString; missing/unreadable/null/nonstring/malformed ProductVersion fails.
Only IDs must equal the source set: historical EF product versions need not all
match one current version. Both probes remain bounded BEGIN READ ONLY queries.
The game role's access is not used as evidence of the admin role's access.

Pinned admin source calls EnsureStorageAsync/MigrateAsync on several read/auth
paths. Therefore these checks must run before server launch or admin requests.
No HTTP request was used as a supposedly read-only verification shortcut.

## Test scope and invocation

On the current host:

    PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s source/tests/windows11 -p test_database_contract.py -v

19 new offline evidence/source-contract checks PASS; 1 PowerShell behavior test
SKIPPED because pwsh is absent. These checks validate provenance/compiled-source
set equality, contract/hash binding, original baseline flags, query source shape,
separate credential call sites, activation fences and prepared test coverage.
They do not execute PowerShell branches or prove SQL/Windows compatibility.

Test-DatabaseGuards.ps1 contains 40 mock-only behavior cases for valid contracts,
missing/extra/duplicate/swapped histories, unsafe schemas, unknown config IDs,
wrong settings/system ID, ProductVersion failures, default history resolution,
and per-context credential/permission failures. It is prepared, NOT_RUN here.
With an approved available PowerShell7.4+ environment it can be run standalone:

    pwsh -NoProfile -NonInteractive -File source/tests/windows11/Test-DatabaseGuards.ps1

The harness imports guard function definitions only and mocks all DB/config
credential access for orchestration. It never starts the launcher or connects
to a database. PowerShell syntax/runtime and actual PostgreSQL query behavior
remain unverified until that separate execution opportunity.

## Not a repack or approved setup

The source candidate adds one launcher contract file and changes two guard files.
The prior packager still pins the old launcher baseline; it was deliberately not
reworked or run, and no control package was patched in place. A later authorized
small launcher-overlay/inventory integration is needed to stage these reviewed
source changes. That must preserve the existing game/runtime hash gates.

windows11-database-manifest-draft.json is a fragment/proposal, not a launchable
full manifest. Host root, cluster system identifier, runtime/probe role names,
credential paths/grants/ACLs and activation digest remain null/unapproved.
launchEnabled=false and approvedLaunchManifestSha256=null are unchanged.
No general schema framework, migration generator or mutating setup script added.

Other limits: full restored schema/content compatibility, required restricted-role
grants, actual history rows/ProductVersion, package loader/VC++ prerequisites,
Windows start/stop/persistence and portable Web UI remain unverified. Admin
migration code can also require advisory-lock permissions; no runtime behavior is
claimed merely from complete history IDs. Final setup must approve and validate
both configuration deltas, not use auto-migration to repair mismatches.

Evidence: phase2006-database-guards/evidence includes source/blob/attribute records,
compiled metadata and bounded reader, provider schema-resolution evidence,
original safe configuration projection, and verification hashes.
