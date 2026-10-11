> Current external checkpoint: [actual C# build/test evidence](../checkpoints/local-alpha/2026-10-11-csharp/README.md).
> Earlier phase-specific NOT_RUN statements below are historical; the current packaged baseline still remains disabled and unintegrated.

> Phase2104 continuation: a source-only caller concurrency correction is now
> proposed. See admin-availability-concurrency-candidate.md. Earlier phase2049
> findings below remain historical; no new binary or runtime validation exists.

> Phase2049 candidate note: this inherited procedure remains blocked. See
> windows11-preprovisioned-runtime.md for the source-only admin-mode patch,
> 55 current mock checks, source/binary gates and unresolved caller/grant limits.
> Earlier phase2033 results below remain historical evidence, not new validation.

# First database setup: partial implementation, deployment blocked

2026-10-11 20:45 UTC. This is one bounded implementation/mock phase. The real
entry returns BLOCKED_RUNTIME_GRANTS before filesystem claims, credentials or
PostgreSQL. Do not describe this as a working first-deployment procedure.

## Implemented source

- SetupMU.ps1: explicit one-time entry, separate from daily StartMU.
- FirstSetup.ps1: dedicated new database/setup-<id> directory validation and
  refusal of existing state; atomic nonreusable claim; bounded sanitized journal.
- Pinned current disabled package inventory, baseline ZIP size/SHA256 and exact
  dump member verification. Existing package payload must verify before future use.
- Owner-provided private credential-bundle boundary, ACL checks/private directory
  preparation, no credential generation, no secret command-line parameters.
- Explicit future PG17 sequence: SCRAM initdb, loopback-only start with repeated
  port check, owned process identity, setup-only bootstrap/NOLOGIN object owner,
  restricted login definitions, fresh openmu, transactional no-owner/no-acl restore
  under mu_owner, no --clean/overwrite or extension fallback.
- Baseline dump metadata says SQL_ASCII, libc locale C. The draft preserves this;
  no implicit UTF8 conversion/migration. This is not a recommendation for new data
  design, and language/text behavior remains a later acceptance concern.
- Exact guarded transaction for the new restored copy: one fixed SystemConfiguration
  row, before ReadConsoleInput=false/AutoUpdateSchema=true, after true/false;
  unchanged other fields, final values and row count checked before COMMIT.
- Eight-context private ConnectionSettings staging, probe pgpass, HBA staging,
  two-context read-only acceptance hook and staged setup-result draft. The shipped
  server ConnectionSettings is not overwritten and no approved manifest is written.
- Owned cluster stop only, uncertain ownership/start retained for owner review,
  no recursive kill, no database/file deletion, no automatic resume of partial state.
- Setup statement-log suppression survives sealing. Existing read-only Guards.ps1
  allows only log_statement=none and log_min_error_statement=panic when supplied.

Every OS/database/credential operation above is SOURCE ONLY. All executed tests
mock those operations; no actual cluster, role, password, ACL or network change.
The utility wrapper and Windows ACL/process/port implementations are NOT validated
by the Linux mocks. No real restore or Windows acceptance was performed.

## What is deliberately incomplete

Set-MuSetupRuntimeGrants contains an unconditional RUNTIME_GRANTS_UNRESOLVED fence.
Get-MuSetupKnownGrantsSql is only a source-proven account/config/friend/guild/probe
subset; it is not called as if it were a complete runtime policy. Entity/Typed
minimum access is unresolved. Admin's automatic migration path conflicts with
no-DDL runtime access. No owner/schema-CREATE escape hatch is supplied.

first-setup-policy.json is hash-pinned and BLOCKED_SOURCE_NO_DDL_INCOMPATIBILITY.
The entry checks this before any mutating stage. Even editing status in a future
policy cannot bypass the separate full-grant implementation fence. Resolving the
source contract and implementing/reviewing the full grants is required first.

The context/configuration staging and acceptance sequence can be unit-exercised
behind mocks, but that is not evidence that the incomplete full grant stage works.
The current source is not integrated into the16,161-file disabled control. Its
existing packager pins remain the prior reviewed guard integration: running that
mode against this changed Guards.ps1 will correctly reject changed source until
an explicitly reviewed integration updates pins. The setup policy targets that
unchanged prior package inventory; no control was patched in place.

## Exact blocker and its scope

Pinned OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8:
AdminUserRepository.cs, blob df601609eef27bdb7d4b9b3566d25a61edb8f90b,
EnsureStorageAsync calls Database.MigrateAsync after CanConnect; several repository
reads/auth paths invoke it. EF Core10.0.2 Migrator.cs blob
a767c77be06b76c1e5be7c37a100a26400d31a30 calls CreateIfNotExistsAsync before migration
enumeration. Npgsql10.0.0 history provider generates CREATE TABLE IF NOT EXISTS
and takes ACCESS EXCLUSIVE on admin.__EFMigrationsHistory.

PostgreSQL17 REL_17_0 parse_utilcmd.c lines187–195 calls
RangeVarGetAndCheckCreationNamespace before IF NOT EXISTS skip; namespace.c
line777 checks ACL_CREATE. Thus an existing history does not remove the schema
CREATE requirement when this admin migration path runs. UPDATE on history would
solve its LOCK permission only. DML-only does not solve the create-history path.

This is a conditional call-path incompatibility. It is NOT proof that every
server startup invokes admin storage with -adminpanel:disabled. Proving that this
path is safely optional remains UNVERIFIED and was not expanded into another audit.
No disabled-admin assumption, runtime DDL grant, rebuild or source patch is made.
Full evidence and exact upstream links: evidence/runtime-role-grant-matrix.md and
pinned-ef-migrator-source.json / pinned-pg17-create-privilege-source.json.

## Actual mock results

Test-FirstSetup.ps1:43/43PASS on the existing portable Linux PowerShell7.4.20,
-NoLogo -NoProfile -NonInteractive,60-second bound. This is a NEW first-setup suite,
separate from the earlier40guard checks. It tests the actual pinned block first,
then simulates a future resolved policy with every mutating stage mocked.
Cases cover explicit approvals, destination shape, pins/encoding, journal privacy,
restore flags, no trust authentication, secret transport via stdin, conditional
flags, ordered control flow, failure at each stage, uncertain startup, owned-only
cleanup and strict final logging settings. Static review findings were fixed:
post-flag values/count and persistent statement-log suppression.

## One concrete path to first deployment

Recommended next decision: authorize a narrow runtime change for explicitly
provisioned local databases that checks history without automatic DDL, plus close
Entity/Typed grant requirements. Keep the existing no-DDL guard; do not silently
trade it for schema ownership. This source/runtime change is outside this phase
and may require a separately approved bounded build/integration test.

Only after that reviewed gate is closed:
1. Finish/pin the full grant SQL and remove the named fences through review; keep
   activation disabled. Integrate the setup source and compatible guards with
   updated package inventory pins into a new candidate, preserving the old one.
2. Select one Windows11 x64 machine and new local package/DB directories; verify
   dependencies, VC++ availability/signatures, package hashes and free5432.
3. Obtain actual setup approval naming baseline11651520969, isolated target,
   role/credential/ACL operations and both new-copy flag changes. Owner performs
   the secure credential-entry/final-action handoff. No secret in chat or report.
4. Run the bounded setup once. Failure preserves the new directory and evidence;
   no retry into it. Verify both histories, identities, grants and owned shutdown.
5. Review/promote staged private ConnectionSettings and the complete private
   launch manifest. Approve a separate Windows start/stop/persistence acceptance.

Today step1 remains blocked. No actual deployment command is presented as ready.
