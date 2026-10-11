Preservation branch note (2026-10-11): see [packaging preservation](windows11-package-preservation/README.md). Earlier unpublished/transfer/migration statements below are historical. Current owner decisions remain on docs/s6-owner-strategy-2026-10-10; this branch preserves the original local packaging chronology without enabling launch.

## 2026-10-11 continuation after 07:48 UTC owner instruction

See windows11-package-static-continuation.md for pinned client dependency/shader evidence and the exact missing migration inputs. One supported Library read failed at tools/list with network; no retry/upload. Existing ZIP hashes and launcher activation remain unchanged.

# Packaging save outcome — local artifacts retained

Full partial-package ZIP:470,974,707bytes,
SHA256fb1f389a640bb83b9bfedbf14526655647031600e48402358e94f9a1d55b3f28.
Readback verified13,223payload members plus checksum catalog. Review ZIP:2,138,966bytes,
SHA2560e51834cfec24be6b93241d5416d9e6b14af2aee955406623c853abb2306eafe.
Inventory SHA25614f6ff7096579cca0b1eac0a4336a8ea91af349e1d2bd9d446439a0a9fe3f00f;
draft manifest SHA25630e7a94ef5e801447767a8d4053cbcbcdcb006501ba070ded0eda37fb04c826f.
Packaging implementation local commit ebebc705793c4f13193c785485871018fe97fa6c.

The required prepared Library upload helper was invoked once for the full package
and review archive as one ordered batch. It failed before preparation with
`library upload failed: hosted apps tools/list request failed: network`.
Neither new artifact has a confirmed Library ID. No retry/direct-action fallback,
permission change or alternate route was attempted. Local archives remain intact.
This is an output-transfer blocker in addition to the separate input-download
failures, not a package/runtime incompatibility. Stop here; resolve supported file
transfer before another packaging stage. No additional owner setup decision is
needed merely to finish private artifact transfer.

# Private local packaging stage — 2026-10-11 (not published)

Owner approved one bounded MEDIUM packaging stage at07:28UTC. Launcher source is
published7f5b44a930a501dfc7ea4f522584cb59a22c9499; this packaging work is local/private.
Latest authoritative docs branch92a3c08 was read. Executor remained responsive after
the parent's disconnected notification; no duplicate task or build was started.

Available package candidate:13,188Data files +13font files +8unchanged launcher files,
13,209inventoried files/750,478,371bytes. Source Data tree77f7830f542d106fc519c8821832d49a3dd8ae3a
and fonts tree149f928e2547aa6658977c3f41c63abccfa471ed matched; every copied file was
checked against its pinned Git blob. The existing overlay was applied only to the
package copy; resulting Group12 SHA2561441360f93d80291659f63912022e0816125863acd0212ab4ec02fca33ebbb73.
The original overlay backup is retained under evidence, outside client/Data.
Repository assets and reviewed launcher bytes are unchanged. Font notices retained.
Five NEW packaging/path/hash/draft tests PASS; no unchanged lifecycle/build/gameplay
checks repeated. Recipe: scripts/package-windows11-local.py; tests/windows11/test_packaging.py.

Blockers, not compatibility findings:
- Server Library libfile_b1e2679ae4088191859d97f0bbd4903c and client Library
  libfile_1174bdeb6c048191ad0be1ac163fdad5 both resolved to expected metadata.
  One supported materialization attempt per file with an explicit destination in
  this executor returned `library file transfer failed: download failed`. Neither
  yielded readable local bytes. No HTTP status/cause was exposed; do not label
  this a proven permission denial, missing backup, or broken game component.
  No alternate URL, credential or generic-file route was tried.
- Compiled migration assembly is unavailable. The pinned GitHub migrations
  directory request through the web tool returned `Failed to fetch restricted URL`.
  No alternate retrieval route was used. Existing pinned Program/context-provider
  source establishes migration-check behavior, not the migration ID set.
  migrationIds/migrationSchema remain null, never inferred from a live database.
- Windows .NET/ASP.NET, PostgreSQL and PowerShell dependency archives are not local.
  PE imports and actual Windows dependency compatibility remain unverified.

The private package contains complete inventories for AVAILABLE inputs, a clearly
named windows11-launch-manifest.draft.json, disabled original session contract,
Russian readme, dependency/transfer/migration evidence and new static test output.
It is incomplete and NOT runnable. It includes no DB dump, credentials, prepared
cluster, installed dependencies, service or activation. The expected server/client
archive hashes are recorded as expected values, not falsely claimed byte checks.
Package/archive identities and Library save outcome are supplied in the final
private artifact handoff, not guessed in advance here.

Next technical prerequisite is supported delivery of the already pinned missing
bytes; no new owner decision is required merely to verify those files or complete
static inventory/migration analysis. Genuine later owner approval is for initial
DB selection/provisioning, persistent authentication/roles/secret handling,
dependency installation/local directories and a new bounded Windows acceptance.
Keep launchEnabled=false until complete actual setup and acceptance are reviewed.
No GitHub publication, workflow dispatch, new access, installation, Windows run,
main changes or architecture work in this packaging stage.

# Three-finding review closeout — 2026-10-11 (unpublished)

Limited corrections after independent review of c07bfb31:
- Start now checks the returned client's retained identity and liveness before
  RUNNING. A live client with invalid identity retains the session without acting
  on it; an already-exited client permits owned server/PG cleanup.
- Historical server error markers remain visible in sanitized reports and
  STOPPED_WITH_WARNINGS after owned exit0/drain and PostgreSQL-last shutdown.
  They no longer permanently block PostgreSQL shutdown. Timeout, nonzero exit or
  incomplete drain still refuses PG shutdown. Retry sends no duplicate stdin exit;
  warning evidence survives successful cleanup. Persistence remains UNKNOWN.
- A failed menu report write emits fixed REPORT_FAILED text and keeps the active
  controller/session open, without entering the outer cleanup path.

25 lifecycle checks PASS (5 new focused regressions); previous28 guard PASS retained,
not rerun. Linux/synthetic only. Setup activation remains disabled; no Windows run,
publication, dispatch, architecture or additional features in this closeout.

# Bounded Windows 11 daily launcher — 2026-10-11 (unpublished)

CODEX PREFERRED, owner-approved MEDIUM at06:00:12UTC. This replaces the partial
candidate9dbf42e3 and uses `scripts/windows11`, not parallel candidate entrypoints.
No setup tool, installer, service, updater, hosting, main merge, workflow dispatch,
server build or gameplay work. No laptop changes. Parent reviews the exact patch
before publication. Readiness65.5/model1.1/MEDIUM unchanged.

## Source reconciliation

The seven existing remote branch tips and available path history did not contain
the four old named files. The referenced Library archive was subsequently recovered
by the parent through supported materialization; parent verified archive SHA256
`726b2747d45dc9fc6f625533b489ed3aad0058ffe10043a4a9c5aba2d3d4dfa9`.
Archive: MuMain-local-bind-review-2e7bb515.zip,
`libfile_153e4f2e7f4481919c41f665ee93208c`, original commit2e7bb515.
Parent supplied the exact original StartMU.ps1, CollectReport.ps1 and
local-session-contract.json in this task. They have been reconciled and extended
at their original paths. Parent confirmed windows11-launch-manifest.json is absent
from that archive. No authoritative launch manifest was invented.

The earlier child transfer failed once; that access failure is superseded by the
parent-supplied source. Runtime backup remains
`libfile_b1e2679ae4088191859d97f0bbd4903c`. No runtime/client/Data/DB archive was
retrieved in this task. No unchanged successful helper/build/gameplay tests rerun.

## Implemented daily controls

StartMU opens one small Russian-language menu: Start, explicit Stop, CollectReport,
and Stop-and-exit. The controller stays open while playing so it retains OpenMU
stdin. `-Action Preflight` performs the offline checks and exits; `-Action Start`
starts then retains the menu. A separate `-Action Stop` refuses with
NO_OWNED_SESSION and directs the user to the existing window; it cannot recover
another process's stdin. No IPC service or process adoption is introduced.

Start validates the reviewed manifest, every inventoried file, configuration,
local paths/dependencies, cluster identity, and vacant ports. It acquires a mutex
and durable ownership marker, rechecks ports, starts its PostgreSQL child, executes
read-only DB checks, starts OpenMU, requires owned loopback listeners AND a stdin
PID round-trip, then launches the client. Unexpected exits, unknown identity,
missing readiness, extra TCP/UDP listeners or config mismatch refuse progression.
The environment is cleared and rebuilt from validated local Windows directories
and fixed local-only settings. No CI authentication is inherited.

Stop closes the owned client normally, confirms PostgreSQL health, sends OpenMU
`exit` once, waits for exit0 and output drain, checks conservative error markers,
then runs pg_ctl fast stop against the owned cluster. No OpenMU/client force kill.
A timed-out pg_ctl is retained and reused on retry. Failed or uncertain process teardown retains control
handles, PostgreSQL where still alive, and the marker. The cluster is never deleted.
Historical log error markers alone produce warnings after safe shutdown.
An orphan marker blocks later starts; it is never automatically cleared or used to
adopt processes. Console termination/crash recovery remains intentionally manual.

CollectReport writes a local allowlisted JSON containing fixed provenance, UTC,
status and explicit evidence limits. It rejects UNC/mapped network destinations
and reparse paths. It reads no raw logs, DB, environment, screenshots or dumps and
uploads nothing. Menu reports carry that controller's status; a standalone report
has IDLE for its own fresh context, not a claim about other processes. Runtime
Serilog may still create its pinned local logs; those are never copied into reports.
The bounded observer retains only PID-seen/error-seen booleans, not output text.

## Real input gates; no unconditional implementation stubs

Get-MuApprovedSetup and Assert-MuDatabase now implement validation and query paths.
The supplied contract correctly remains launchEnabled=false and its approved
manifest SHA256 is null because no approved persistent owner setup exists.
Changing a boolean alone cannot pass: an independently reviewed manifest digest,
actual matching bytes and all guards are required. No setup evidence is generated
by Start. Tests activate only isolated synthetic copies of the contract.

The missing windows11-launch-manifest.json is an INPUT prerequisite. Its digest
must be inserted into the release-controlled session contract only in the separate
approved setup/package review. This is not a user checkbox or a claim of approval.
Do not hand the disabled source tree to the owner as a ready one-click package.

Manifest schema1 is enforced by Guards.ps1:
- Relative paths: runtimeArchive, server, clientDirectory, pgDirectory,
  dotnetDirectory, pgData, dotnet, postgres, pgCtl, pgControlData, psql, client.
  Code/data areas must be distinct. PostgreSQL tools reside under pgDirectory/bin;
  dotnet.exe and Main.exe reside at their declared area roots.
- hashes: complete SHA256 map for immutable package/dependency/config files,
  including private ConnectionSettings.xml, the approved probe password file and
  PG_VERSION/postgresql.conf/postgresql.auto.conf/pg_hba.conf/pg_ident.conf.
  Every actual code/asset tree file must be inventoried, apart from bounded known
  server/client log locations. Extra DLL/config/plugin files are refused.
- database: name=openmu, queryUser, pgPassFile, systemIdentifier, migrationSchema,
  migrationIds, runtimeRoles and configurationIds. IDs must come from independently
  reviewed setup and pinned runtime/source evidence, never copied from the current
  DB merely to make a mismatch pass. In particular, migrationIds must be the full
  EntityDataContext migration set for the pinned runtime, not a DB-derived guess.
- endpoints: exact game(port,published), chat(port), connect(port) arrays. Include
  44406/55902 and configured chat; web18080 and PG5432 remain distinct fixed ports.
- versions: approved existing .NET/ASP.NET10.0.11 and PostgreSQL17.11. These are
  prerequisites, not installation instructions or evidence of owner PC support.

Runtime is pinned independently of that manifest to outer archive
505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c and inner archive
4b1b1d71a0aa992fb3f2dbac7e447a5704cccc7ed38ebacfdebe97eabebf1eec. It is read locally,
never extracted/downloaded by Start. Exactly186 runtime inventory entries are
required. Only the separately reviewed ConnectionSettings.xml may differ from
build bytes. Client Main.exe, bridge DLL and corrected Group12 overlay hashes are
also fixed from resource-registry; remaining client/Data/fonts/shaders and tool
inventories require the real reviewed manifest. No Main.exe-only package accepted.

## Authentication and no-initialization boundary

The implemented validation profile is deliberately narrow: numeric IPv4 loopback,
SCRAM-only per-role HBA rows, no config includes or preloads, empty auto-config and
identity mappings, private Windows ACLs on credential files, no CI default passwords,
and exact approved XML context/connection options. It ONLY checks existing files;
it never writes config, credentials, roles or ACLs. Owner must separately approve
and prepare that security profile before activation; it is not silently applied.

Every runtime credential is tested by fixed read-only probes. Elevated roles,
role memberships, DB/schema creation permission and table/database ownership are
rejected. The probe role also needs approved read access to the configuration and
migration tables. PGPASSFILE/PGPASSWORD are passed only in the isolated child
process environment, never command arguments, reports or global environment.
Queries use -X/-w/ON_ERROR_STOP, bounded connection/statement timeouts and an explicit
READ ONLY transaction. The only force termination is of a timed-out synchronous
read-only/version probe utility, never a service or process tree.

Important correction from pinned source: AssumeExternallyProvisioned=true is NOT
"disable initialization". Program.cs618–656 can still migrate/build schema and
initialize data. The launcher leaves the pinned false setting unchanged. Before
OpenMU, it verifies exact applied migrations, expected nonempty GameConfiguration
IDs, singleton ReadConsoleInput=true/AutoUpdateSchema=false and complete endpoint
inventory. It repeats the snapshot using EntityDataContext's actual credential,
whose migration-read failure would otherwise enter the initializer. Restricted
non-owner/non-DDL roles provide a second refusal boundary. Start contains no SQL
writes, initialization, restore, role creation, -reinit, -demo or migration command.
Starting/stopping PostgreSQL itself can perform normal internal housekeeping; no
claim of byte-identical physical cluster files is made.

Source checks (read-only, no build) used pinned OpenMU d067b3c:
Program.cs618–656 and Persistence/EntityFramework/PersistenceContextProvider.cs47–55,
108–119,136–149. DatabaseExists means any applied migration; UpToDate means no
pending migration. These findings replace the earlier suggestion that toggling
AssumeExternallyProvisioned would make daily launch safe by itself.

## Verification and remaining boundaries

New tests: 20 lifecycle +28 guard checks PASS under portable PowerShell7.4.6 on
Linux. These cover real loader parsing with an isolated synthetic approved manifest,
receipt tampering, inventories/hashes/path/config refusals, read-only SQL adapter,
all-credential checks, migration/console/endpoint mismatches, PID observation,
server and PG utility retry logic, output drainage and report secret canaries.
Only harmless child processes run. Positive archive/dependency/Windows ACL checks
use explicit mocks; actual artifact validation is tested negatively against
unpinned bytes. No claim of successful real package validation is made.
Commands: tests/windows11/lifecycle.tests.ps1 and tests/windows11/guards.tests.ps1.
JSON parsing and git diff whitespace checks also pass. Original successful game
integration38108874540 remains preserved, not repeated or relabeled as launcher QA.

Still Windows NOT_RUN: Win11 x64 menu/console handling, global mutex, actual ACLs,
real dependency probes, direct-child postgres.exe ownership (different from the
smoke's pg_ctl daemon), TCP/UDP inventory, real psql credentials/queries, native
client close, real startup/shutdown/relaunch and persistence. PostgreSQL remains
running on unsafe/uncertain OpenMU shutdown. Clean exit is not proof all save
operations succeeded; crash safety and interruption recovery are not promised.

No blanket setup/query placeholders remain. Outstanding work requiring real inputs
is package/manifest materialization and independently verified migration/config
identities, separately approved initial DB/authentication/dependency setup, then
new launcher-specific Windows acceptance in an authorized environment. Parent
review of this exact patch comes first. No dispatch or laptop instructions now.

---

# Local-only bind implementation checkpoint

2026-10-10 21:52 UTC. Owner approved one bounded MEDIUM stage. Main and runtime baseline unchanged.

## Result

Local task commit `2e7bb5157e50d2bec1eaac6b1678bf1253266049`, branch `codex/local-only-bind-2026-10-10`, exact base `2757851d06c0c87e4cf6ea06162460ef6387ea2a`. Code is NOT published to GitHub. Review archive `MuMain-local-bind-review-2e7bb515.zip`, Library ID `libfile_153e4f2e7f4481919c41f665ee93208c`, 73404 bytes, SHA256 `726b2747d45dc9fc6f625533b489ed3aad0058ffe10043a4a9c5aba2d3d4dfa9`. Archive includes commit.diff, commit.patch and 14 changed files with checksums. It is a source-review artifact, not an installer or runnable package.

Opt-in `OPENMU_LOCAL_ONLY_TCP=1` selects loopback before shared TCP socket construction; unset/0 preserves original wildcard behavior and invalid values throw. Existing Money patch unchanged. Admin/web and optional actor endpoints remain separate controls.

Child reports source hashes, patch apply/reverse, altered-source rejection, JSON/XML and diff whitespace checks PASS. Independent parent-side static review verified archive and member checksums and actual exported patch/tests/scripts; no substantive source blocker found. It did NOT independently rerun source checks because original pinned OpenMU files and unchanged Money patch are absent from the export.

C# helper/socket tests added but NOT_RUN. They exercise helper and a separate TcpListener, not full production integration. Python checker verifies applicability and exact call-site replacement, not runtime containment.

## Starter state and remaining blocker

StartMU.ps1 and CollectReport.ps1 are non-operational fail-closed preparation. Start/Preflight remain BLOCKED, Stop refuses; no processes are launched/adopted/killed. local-session-contract.json describes intended environment propagation but does not implement it. No one-click readiness, persistence or readiness-model credit.

Saved cloud environment lacks OpenMU checkout, .NET, PowerShell and runtime archives. No substantial environment reconstruction was attempted. Compilation, production socket integration, Windows execution, actual effective endpoints, ReadConsoleInput baseline flag and graceful shutdown/persistence all remain UNKNOWN/NOT_RUN.

## Next bounded step

Retain reviewed source candidate. Before additional spend, select a prepared pinned OpenMU+Money/.NET environment; compile both patches together and run focused checks, record new binary identities. Do not restore the entire game stack or repeat gameplay merely to compile this change. Keep live launch blocked until setup/authentication, actual listener coverage and lifecycle prerequisites are resolved. The implementation task is paused at this boundary; no agent is currently implementing a working lifecycle.

## SDK attempt, 2026-10-10 22:54 UTC

Owner approved official .NET 10 SDK installation in the task cloud workspace and the isolated helper/socket test. The first environment request to Microsoft release metadata failed with `Tunnel connection failed: 403 Forbidden` (proxy CONNECT). No alternate route, retry, SDK download, installation, compilation or test was performed. All 12 helper/socket checks remain NOT_RUN. Exact root cause/configuration behind the proxy denial is unverified; do not attribute it to GitHub repository permissions. Do not bypass the denied route.

Cloud task retained documentation-only local commit `9601fbe9dab0caadf171458caa16e89d9bdabe13` with report and traceback; code commit remains `2e7bb515`. Needed next: authorized resolution of environment access or a properly approved prepared SDK environment. Full game stack is not needed for this isolated test. Owner reiterated the deliverable is a fully working low-friction package; a blocked scaffold does not satisfy it.

## Published network update and independent checks, 2026-10-11 00:25 UTC

Owner manually added official Microsoft hosts dotnetcli.blob.core.windows.net and builds.dotnet.microsoft.com, saved draft and published. Screenshot showed publication; environment catalog confirmed new version suffix cecfgver_6acad4ebdef48195814a8f15458e07ea. A NEW task used that published configuration; no assumption that an old task inherited it.

Supported Library transfer of review archive failed with `download failed`, including one bounded supported retry. No HTTP cause exposed; no alternate file route used. Independently, official releases-index.json request from the new environment returned HTTP 403 (curl exit 22). Stopped after denial. SDK not downloaded/installed; all 12 tests remain NOT_RUN. These are separate blockers; no conclusion that GitHub permissions or broad full-access settings solve them.

Task: 01a12855-31f9-7643-975b-e547dc3da020. Terminal evidence Library libfile_b5c83f89cf208191b888bc081160692d version 1, 19444 bytes, SHA256403cace9de513bec8fdb808b647996e9e0d1f3661ff1e2bfe8117de4bd5b813c. Source patch remains unchanged and recoverable from original review archive. Parent reported both blockers to owner.

api.github.com is a distinct deferred GitHub Actions connectivity task; owner explicitly postponed adding it. Paused browser dispatch remains paused. No broad access expansion or automatic retry authorized by these findings.
