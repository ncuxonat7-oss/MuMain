## 2026-10-12: full disabled Alpha package

This local candidate combines the unchanged phase2027 client/Data/fonts and
Windows dependencies with the phase1042 published server and an integrated
launcher/setup source copy. It contains 24,417 payload files plus four detached
control documents. The obsolete runtime ZIP is not included or asserted to
certify the new server. Earlier packages remain untouched.

A single package-inventory.json covers every payload file, including all 12
launcher/setup files. The schema-3 draft setup manifest has matching hashes and
explicit runtimeProvenance. Owner DB fields remain null. Detached
package-admission.json pins the inventory, draft and staging status without a
circular self-hash. This is unsigned integrity metadata, not permission to run.
The independent inventory SHA from staging-result.json or a reviewed checkpoint
is required for full read-only verification; do not trust a SHA supplied only
by a possibly modified package.

Use the existing StartMU.ps1 entry with -Action Verify -PackageRoot <root>
-ExpectedInventorySha256 <independently retained SHA>. It calls the existing
Test-MuPreflight with -IntegrityOnly and the shared Assert-MuPackageContract.
Get-MuApprovedSetup and Invoke-MuFirstSetup use that same contract before their
explicit runtime-grants stop. No parallel component checker is installed.
Ordinary blocked paths verify metadata and the executing launcher files, then
stop; only explicit Verify hashes the entire payload. The executing scripts
must belong to the target package root.

The candidate-specific runtime reader uses the full package inventory and
8,440 published server files, not historical archive pins. Only the exact
server/web.config SHA is allowed in the server .config check. The fixed EF SHA
is 67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1.
The database-source contract pins that same assembly. Runtime grants remain
unconditionally fenced, and false/null launch fields cannot activate this copy.
Process-observer compilation is deferred to the unreachable server-start path;
read-only verification and blocked entry tests compile no C#.

Windows, web HTTP, full runtime grants/Typed closure and game lifecycle remain
unaccepted. Five existing ImageSharp publish warnings remain. No DB dump,
credentials or prepared cluster is included in the new output. Source checkpoint,
publish checkpoint, client/dependency provenance and original archive provenance
are distinct; one does not certify another.

The local phase integration report is the test evidence. Root metadata records
read-only integrity verification; it is not a runtime acceptance report.

---

> Phase2104 continuation: a source-only caller concurrency correction is now
> proposed. See admin-availability-concurrency-candidate.md. Earlier phase2049
> findings below remain historical; no new binary or runtime validation exists.

# Explicit preprovisioned runtime: source-only candidate

This local candidate continues phase2033. No binary was built, replaced, loaded or run.
The original OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8 runtime and its
Money/local-bind evidence stay unchanged. Existing package controls are preserved.

## Explicit configuration

Only the admin connection receives `<AdminSchemaManagement>ExternallyProvisioned</AdminSchemaManagement>`.
The new server source preserves omitted/default RuntimeMigrations for other deployments.
This candidate launcher instead requires the exact external mode, rejects its absence,
unknown value, duplicate or wrong namespace, and rejects this element on other contexts.
The prepared private XML carries this value; no actual private XML was generated.

## Deployment fences

The copied setup policy is hash-pinned and remains blocked. Even a future reviewed
status change also requires explicit source review, boolean binary alignment and
passed live validation. A source patch plus mocked/static tests cannot establish
any of these deployment facts. The incomplete grant setter retains its independent
stop. launchEnabled is false and approvedLaunchManifestSha256 is null.

The new source-mode patch must preserve the default migration behavior. Only an
explicit externally-provisioned mode may use a read-only exact applied-versus-
compiled migration-history check. Unknown, missing, extra or malformed history,
unavailable DB and timeout must deny readiness rather than enter admin bootstrap.
The actual auth caller treats false readiness as initial setup; this is why a
blind migration skip or false-returning validation is insufficient. Moreover,
AdminUserAvailabilityService returns its cached false if its semaphore is busy.
This source patch does NOT close that caller-level concurrent-bootstrap path.
Whole-panel fail-closed behavior remains a deployment blocker; the repository
branch alone is the scope of this patch.

## Single conditional deployment path

1. Review the exact server patch and source-derived role contract. Resolve each
   unsupported role assumption without broadening runtime CREATE/ownership.
2. Separately approve a build of the pinned source plus Money/local-bind patches
   and this narrow fix. Record new commit/patch hashes, binary hashes and actual
   compiled migration identities. Never reuse old binary proof for new bytes.
3. Review a new disabled package, updated exact inventories and mode/config
   guards. The unchanged packager pins intentionally reject changed guard bytes.
4. Separately approve the dedicated Windows PostgreSQL 17 deployment, credential
   handoff and ACL changes. Establish baseline archive/dump hashes, new-path
   isolation, SQL_ASCII/C compatibility, role grants and restore acceptance in a
   disposable target. No grant assumption is resolved by this document.
5. Independently validate both runtime histories, configuration IDs, endpoints,
   exact reviewed flags, absence of unexpected privileges, and fail-closed admin
   behavior under missing/extra history and restricted privileges. Approve launch
   only after those checks and owner review; this candidate never enables it.

Mock/static tests are control-flow/source evidence only. They are not PostgreSQL
SQL execution, C# compilation, Windows ACL/process tests or server/game smoke proof.

## Entity/Typed grant boundary

The source-derived observed contract is retained in
`evidence/entity-typed-observed-contract.json` with executable=false and
activationAllowed=false. Ordinary startup may INSERT/UPDATE
config.PlugInConfiguration; read-only Entity/Typed is not universally sufficient.
No blanket config DML or SystemConfiguration write is inferred. Exact eager-read
closure, enabled branches and emitted SaveChanges tables/columns remain unknown.
The 119-table model inventory is not a grant allowlist.

## Smallest next decision

Decide whether to authorize one narrow caller fix making unresolved/in-progress
admin availability fail closed in the explicit external mode. Do not grant runtime
DDL or broad config writes to bypass it. Full grant closure and approved build
remain separate prerequisites; no deployment or new audit is authorized here.
