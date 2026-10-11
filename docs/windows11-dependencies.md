# Windows dependency continuation (local, disabled)

This extends the existing offline packager. It does not download, install, execute
Windows binaries, provision a DB or authorize launch. Source and result are local.

## Use

With the preserved merged control and already downloaded pinned archives:

    python scripts/package-windows11-local.py --base-package /local/control-merged --dependency-archives /local/dependency-archives --destination /local/fresh-dependency-control

Requires Python 3.11+ on the packaging host. The base inventory is pinned to the
13,432-file verified control; source file sizes and non-symlink paths are checked
while copying. Previous game-resource hashes are reused, not rerun. A same-size alteration of an
old base file is not detected by this continuation; there is no fresh whole-candidate
SHA256 certification. Keep the prior verified base immutable and require the complete
existing launcher hash gate before any later approved launch. New dependency
bytes are checked against pinned archive and per-member hashes. The destination
must not exist. A partial failure remains disabled and must be preserved.

`docs/windows11-dependencies.json` is the complete hash-pinned input specification.
The recipe verifies its SHA256 before using it. Do not edit versions or hashes to
force acceptance. The existing asset/runtime packaging interface remains available.

## Included versions and rationale

- .NET/ASP.NET Core 10.0.11 x64: exact operational pin in Guards.ps1. Server binary
  baseline10.0.0 remains distinct. Official ASP.NET ZIP contains both shared
  frameworks and host; all193 files from the separately verified .NET ZIP are an
  exact subset. Stage the combined339-file tree once, with its license and notices.
  No SDK, targeting pack, apphost pack, IIS hosting bundle or server Desktop Runtime.
- PostgreSQL17.11 vendor revision3: published EDB Windows binary archive and the
  corresponding checksum response in EDB's repository. Includes the four existing
  launcher tools, plus initdb/pg_restore/pg_dump for a later separately approved
  setup/backup phase; those tools are not run here. Preserve their20-file bin/DLL
  closure, runtime lib DLLs, share tree and two vendor license/notice files.
  No pgAdmin, StackBuilder, headers, import libraries, ecpg, pg_config, benchmark or
  development/test tools are staged. Vendor source ZIP is retained unchanged.
  Optional lib extensions may need additional interpreters; no extension activation
  or dynamic loading compatibility is claimed.
- PowerShell7.4.20 x64: latest servicing update in the launcher's7.4 LTS line at
  preparation time; supported through10-Nov-2026. Preserve its full924-file official
  portable distribution and module licenses. Its bundled .NET8.0.31 belongs to
  PowerShell itself and does not replace the server's private10.0.11 tree. Shipped
  reference/Roslyn assemblies support the existing launcher's Add-Type
  ConsoleObserver; no separate SDK or compiler package was added.
- Microsoft VC++ v14 redistributable14.51.36247.0: static PG imports show
  MSVCP140/VCRUNTIME140 absent from the selected PostgreSQL bin tree. Downloaded from
  Microsoft's official x64 link, then pinned by effective content-addressed URL,
  local SHA256 and PE file-version resource. Saved under prerequisites only.
  It was not run, installed, extracted into PG, or Authenticode-validated on Windows.
  Microsoft license terms and redistribution eligibility still require review before
  installation/distribution. Copying DLLs from unrelated client/pgAdmin trees was
  deliberately avoided.

## Security/support review limits

Microsoft already lists10.0.12 as a newer security patch;10.0.11 remains unchanged
because the launcher and owner's approved scope pin it exactly. Resolve the patch
policy before actual Windows activation; this is not a claim10.0.11 is current.
PowerShell7.4 support expires10-Nov-2026, so review its support status at Windows
acceptance. No silent major/minor upgrade is part of this stage.

Provider hashes checked: Microsoft SHA512 release metadata for both .NET archives,
PowerShell GitHub release asset SHA256, EDB contributor's checksum response for the
exact revision3 archive. VC++ uses the official download's content-addressed URL
and newly recorded SHA256, not an invented independently published checksum.

Original license/notice files are preserved in each runtime tree and individually
hashed in the manifest. This is not redistribution clearance for the pre-existing
MU assets/client bundle. VC++ installer contains its own terms; official terms link
is recorded below, and acceptance/installation remains a later user decision.

## Actual result and remaining first-launch requirements

Fresh control:16,160 inventory entries,1,437,915,551 bytes.2,728 new dependency or
prerequisite files (498,614,046bytes) verified;13,432 prior files reused without
rehashing game resources. Required dotnet/pwsh/PostgreSQL launcher executables are
statically x64.18 new dependency tests PASS. No Windows executable was launched.

launchEnabled=false and approvedLaunchManifestSha256=null. The final launch
manifest is absent; the draft leaves DB/endpoints null. Bundled PowerShell's path
is recorded in packaging status, but no ready desktop entrypoint or installer is
claimed. Web UI remains unverified and unchanged.

Still pending: Windows Authenticode checks where applicable; VC++ runtime approved
installation/availability; real Windows11 loader/OS/API/GPU behavior, PowerShell
Add-Type and launcher lifecycle; exact dependency probes; private DB setup,
credentials/ACLs, independently reconciled migrations/configuration/endpoints and
reviewed manifest. Static hashes/PE headers do not establish these runtime results.

## Concrete next DB step (proposal only)

Prepare and obtain approval for one initial-setup plan: choose the preserved known
working snapshot (latest successful local integration run38108874540 is the current
candidate, subject to exact backup identity confirmation), select a new dedicated
Windows PostgreSQL17 cluster directory and database name, and define separate
restricted runtime/probe roles plus owner-controlled credential/ACL handling.
Before any restore/start, reconcile the pinned runtime's EntityDataContext and
AdminPanelContext migration expectations independently, map configured endpoints
and expected configuration IDs, and specify read-only post-restore acceptance.
Only a separately approved phase may create the cluster/roles, restore a DB or
handle secrets. Do not populate the approved migration set from the restored DB
just to make checks pass. No such DB action was performed in this dependency stage.

## Official sources

- https://dotnet.microsoft.com/en-us/download/dotnet/10.0
- https://builds.dotnet.microsoft.com/dotnet/release-metadata/10.0/releases.json
- https://github.com/PowerShell/PowerShell/releases/tag/v7.4.20
- https://learn.microsoft.com/en-us/powershell/scripting/install/powershell-support-lifecycle
- https://www.enterprisedb.com/download-postgresql-binaries
- https://github.com/EnterpriseDB/edb-installers/issues/682
- https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist
- https://visualstudio.microsoft.com/license-terms/vs2026-ga-visualcpp-v14-redist-runtime/

## Unique files requiring a separately approved external checkpoint

1. Updated scripts/package-windows11-local.py (dependency continuation).
2. New tests/windows11/test_dependencies.py.
3. New docs/windows11-dependencies.json (archive/file identities and selections).
4. This docs/windows11-dependencies.md (usage, provenance, limits and next DB step).
5. New focused test output, acquisition evidence, static PG imports/version evidence,
   dependency verification, source checksums and patch in this local phase directory.

Official binary archives and the large fresh control remain local, separately from
small source/evidence. No external publication/backup or full-package ZIP was made.
