# Bounded Windows 11 launcher candidate — 2026-10-11

Classification: CODEX PREFERRED. Owner approval at 06:00:12 UTC covers this bounded
MEDIUM implementation, not laptop setup or publication. Local task branch
`task/windows11-local-launcher` starts at authoritative docs commit
`47ff97ce2676d4b356b2c957535f331139f61e7a`; main remains historical `6fdebbdd`.
Parent must review the exact local patch before publication. Nothing was pushed,
merged, dispatched, installed on the owner's laptop, restored or rebuilt.

## Reconciliation and explicit limit

Read AGENTS.md, CODING_RULES.md, current-state, starter handoff, local-server-controls,
this checkpoint and latest local-bind-actions-checkpoint. No relevant local
`.agents/skills` were present. Read-only fetch inspected all seven existing remote
branch tips and available reachable path history. The four named original artifacts
were absent: StartMU.ps1, CollectReport.ps1, local-session-contract.json and
windows11-launch-manifest.json. Only documentation references were found.
The prior checkpoint identifies unpublished review archive
`libfile_153e4f2e7f4481919c41f665ee93208c`, commit `2e7bb5157e50d2bec1eaac6b1678bf1253266049`.
Its source must be supplied through an approved project reference, or the parent
must explicitly accept a replacement after comparing that source. No Library
archive, runtime, client or database archive was downloaded in this task.

The independent candidate lives under `scripts/windows11-candidate`, deliberately
not at the missing authoritative scaffold paths. It includes Start.ps1,
CollectReport.ps1, Launcher.psm1 and a provenance-only runtime-pin.json. This is
**not a runnable owner package**: Get-MuApprovedSetup and Assert-MuDatabase refuse
with SETUP_REQUIRED. There is no switch, editable approval receipt or ordinary
Start path that bypasses these gates. This is a tested lifecycle implementation
candidate plus prerequisite design, not completion of the deployable launcher.

## Candidate behavior and owner controls

After future reviewed integration, Start.ps1 is intended to stay open while playing:
1 = Start, 2 = explicit Stop, 3 = local CollectReport, 0 = Stop then exit. The same
owner process retains stdin; another shell cannot recover or adopt it. Failed Stop
keeps the menu/session available for retry. Closing/killing the console is not a
safe Stop and may lose stdin; a retained marker blocks subsequent launches.
There is no automatic marker deletion, process adoption or force-kill recovery.

Current Start always explains that separately approved preparation is missing and
starts no service. Report collection works independently; the menu report contains
the current allowlisted status. A separate CollectReport invocation reports IDLE
for its own fresh context, not the state of other processes. Reports contain only
fixed provenance, UTC and allowlisted status; no paths, process IDs, arbitrary
exceptions, configuration, raw logs, screenshots, dumps or credentials. They stay
in the selected local directory; nothing uploads. This conservative report cannot
diagnose game/log errors or prove a save succeeded.

Lifecycle code reuses the smoke's ownership, sanitized child environment, loopback
checks, retained stdin exit, bounded waits and PostgreSQL-last ordering. No CI
transfer, restore/init, roles, fixture repair, scripted gameplay or test assertions
are part of daily launch. PostgreSQL is a direct owned child in this candidate;
that differs from the smoke's pg_ctl-spawned daemon and needs Windows validation.
PID/start-time/path checks guard actions, and private session metadata stays out of
reports. A mutex prevents duplicate controllers; a durable marker blocks recovery
after controller loss. Client uses CloseMainWindow, without forced termination.
Server timeout/nonzero exit retains PostgreSQL and session ownership. Clean exit
alone does not assert persistence. Ordinary Stop never deletes the cluster.

## Exact prerequisites before enabling real Start

- Recover/reconcile the four original files, or review the independent replacement.
  Supply the complete pinned 186-entry runtime inventory plus client/Data/fonts,
  overlay, dependencies and executable hashes. The provenance-only pin file is
  deliberately incomplete; no synthetic hashes or inventory were generated.
- Separately approve database selection, local directory, initial provisioning,
  authentication/roles/secret handling and any persisted ReadConsoleInput change.
  No CI trust settings, temporary passwords, DB_ADMIN_USER or console-flag repair
  are copied into daily launch. Select/install dependencies only under separate
  approval; candidate needs PowerShell 7.4+, which is not assumed preinstalled.
- Integrate a reviewed, read-only setup loader/config guard. It must enforce full
  inventory coverage, reject extra config/plugin files and reparse paths, pin
  effective PostgreSQL includes/preloads/auth config, require numeric loopback DB
  destinations and approved connection options, and disable initialization/migration
  before any DB/server start. The smoke pins appsettings with
  `Database.AssumeExternallyProvisioned=false`; do not reuse this blindly. Review
  the pinned runtime's exact no-initialization behavior and any required config
  delta before admitting daily launch. The current hash helper alone does not
  establish those configuration guarantees.
- Integrate separately approved read-only DB authentication and actual queries for
  one ReadConsoleInput=true row and exact game/chat/connect endpoint inventory,
  comparing it with preflight ports (5432/44406/55902/18080 plus configured chat).
  Reuse Read-EndpointContract from verified helper3a9dff7; no SQL writes/repair.
  Do not enable the first gate without implementing and reviewing the second.
- Resolve Windows 11 dependency/hardware/package checks and client/PG environment
  needs, then validate the new launcher itself in an approved isolated Windows
  environment. Existing smoke PASS is retained; do not rerun it unchanged.

## New verification evidence

20 focused tests PASS under portable PowerShell7.4.6 on Linux. They cover parsing,
missing setup, lifecycle ordering, duplicate requests, preflight/start failures,
Stop failure retention/retry, sanitized report canaries, traversal/hash rejection,
occupied ports, missing/wildcard/extra/UDP listeners, single stdin-exit request on
retry, and one harmless real child with ownership mismatch rejection, pipe drain
and stdin exit0. Mocked checks are not Windows service or DB integration proof.
Command: `pwsh -NoLogo -NoProfile -File tests/windows11-candidate/lifecycle.tests.ps1`.
Only an official portable PowerShell test tool was downloaded into /tmp; release
checksum matched `6f6015203c47806c5cc444c19d8ed019695e610fbd948154264bf9ca8e157561`.
No global install/configuration; XDG test directories are also under /tmp.

Windows NOT_RUN: menu/console lifetime, cross-session mutex and stale marker,
actual TCP/UDP inventory, direct PostgreSQL process identity/shutdown and retries,
real client close, reviewed persistent auth/config preflight, service readiness,
ordinary Stop/relaunch progress retention and startup interruption recovery.
No runtime/gameplay/build/helper reruns, no laptop package or crash-safety claim,
no readiness-score change. Next action is parent review of this exact candidate
and missing-source/setup decision, not workflow dispatch or laptop installation.

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
