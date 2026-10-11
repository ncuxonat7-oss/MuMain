# Windows launcher candidate checkpoint — 2026-10-11 06:50 UTC

Owner approved bounded MEDIUM Start/Stop/local CollectReport implementation at06:00UTC. Candidate remains UNPUBLISHED on task/windows11-local-launcher; no Windows activation or laptop configuration. Latest local commit7f5b44a930a501dfc7ea4f522584cb59a22c9499 follows c07bfb3187a8211815a88ab73c3cee6d0457082a.

Full implementation review bundle: libfile_fc6111425688819189eeb7838bd73db8 v0/file_0000000077ac81fdbeccbeb0c1be3d73,112225bytes,SHA2565184b8dee937e009afc1e01ca17acdd1ee628d103b6c0e5d7a5aedbf769b5fbe. Closeout diff bundle: libfile_0c32fdd12508819198876d8997b0a39b v0/file_00000000fd7881fdbacb8a09c75f0161,13231bytes,SHA25660b23bfe6ee744ae80f3b3815e2b2f8f14fdcaf380804004faa85cbdde0aad48. Both needed to reconstruct final source; cloud task01a1298c-f57f-759b-9875-f0d4d820d037 retains commits.

Original three scripts/contract recovered from prior exact-hash Library review archive and reconciled under scripts/windows11; duplicate candidate path removed. Implemented lifecycle ownership guards, config/inventory/manifest validation, read-only DB checks, PID handshake, graceful shutdown/PG-last ordering, local allowlisted report. No ordinary restore/init commands. Actual reviewed package manifest and persistent setup are still absent, launchEnabled=false. No ready runnable laptop package claim.

Evidence: author reports25 focused lifecycle checks PASS (five new closeout regressions), prior28 guard checks PASS unchanged and not repeated; Linux PowerShell/mock coverage, not Windows integration. Independent static review found and then verified closure of three issues: client could falsely report RUNNING; historical error markers could block PG stop forever; report write failure could accidentally stop active session. Closure PASS06:49UTC. Minor residual: server-error warning can carry to later sessions in same controller; record as nonblocking follow-up, do not expand this stage. Actual Windows ACLs, direct-child PG process behavior, role/schema checks and launcher Stop/relaunch persistence NOT_RUN. Previously proven smoke38108874540 is a separate valid result, not launcher acceptance.

Reusable process lessons: verify materializable source/manifest inputs before implementation; define startup/stop/report failure acceptance up front; return atomic intermediate deliverables rather than long silent work; test synthetic lifecycle errors before costly Windows runs; do not repeat unchanged gameplay/build evidence. Missing implementation is not an owner-permission blocker. Stop at reviewable resource checkpoints.

Next bounded decision: review publication of the prepared candidate to a test branch and separately scope package manifest/first-setup plus Windows acceptance. No code publication, workflow dispatch, persistent authentication/configuration change, production or main merge authorized by this checkpoint alone. Safe docs persistence only. Readiness65.5 unchanged.

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
