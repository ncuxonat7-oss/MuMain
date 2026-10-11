# Prepared database guards: mock execution and disabled integration

2026-10-11 20:30 UTC. This supersedes the prior NOT_RUN status only for the
existing 40 mock-only PowerShell cases and source-only staging limitation.

Official portable Linux x64 PowerShell7.4.20 was downloaded after explicit owner
approval: 72,533,071 bytes, SHA256
ed8008345c7f5337f5e293145f5e243ce132e5ee4dfc24ac551c45a4b3092181.
Source: https://github.com/PowerShell/PowerShell/releases/tag/v7.4.20
671 safe regular/directory archive members,185,160,327 expanded bytes, extracted
under the phase workspace. No apt/root/global PATH/service changes. Linux runtime
is a test tool outside the Windows candidate and is not included in it.

The first invocation stopped before tests with exit134: default PowerShell cache
<user-home>/.cache/powershell is on a read-only filesystem. A single same-test
retry used process-local XDG_CACHE_HOME/XDG_CONFIG_HOME/XDG_DATA_HOME under the
phase workspace, without changing global environment or installing dependencies.
Telemetry/update checks were disabled in that child environment.

Unchanged Test-DatabaseGuards.ps1 (SHA256
0c56cce00ee90aaef0c7c40463528ededeb6f2c9bf9334c53c194ebeca85e98b)
ran with -NoLogo -NoProfile -NonInteractive and a60-second timeout.
Actual result40/40PASS, exit0. No new suite, test expansion or test-source fix.
No database connection, Windows function, game/server launch or credential access.
This does not prove PostgreSQL behavior, Windows ACLs/loaders or gameplay.

## Exact packager continuation

The existing packager adds one narrow --database-guards mode:

    python scripts/package-windows11-local.py --base-package /local/control-dependencies-20261011 --database-guards --destination /local/new-disabled-control

It pins the exact prior16,160-entry inventory and packaging-status hashes and
exact three reviewed source SHA256 values. It reuses the existing guarded
copy_existing_control implementation; existing destination is refused.
After copying, it replaces only Database.ps1/Guards.ps1 and adds
scripts/windows11/database-source-contract.json. New bytes are checked after
staging. Inventory rows retain replaced hashes and distinct source provenance.
No generic overlay engine, installer or database setup procedure was added.

The resulting draft schema2 includes independently known migration histories,
configuration IDs and endpoint ports. Roles, credential path and cluster system
identifier remain null. Approved manifest is absent. The existing launcher
contract remains launchEnabled=false/approvedLaunchManifestSha256=null.
The original launcher Git commit is retained as base provenance; the explicit
launcher_overlay and database_guard_pins fields identify the local extension.

Actual candidate: phase2027-powershell-check/control-database-guards-20261011.
16,161 inventory entries,1,437,924,984 payload bytes.16,158 unchanged old entries
reuse earlier hashes after size/non-symlink checks; they were not content-rehashed
in this stage. This is not fresh full-package hash certification. Keep the old
control immutable and require the full existing launcher hash gate before a
later approved launch. Old inventory/status identities were verified unchanged.

## Remaining work

The first-setup database creation/restore procedure is still NOT_IMPLEMENTED.
Neither PostgreSQL cluster nor roles/credentials/ACLs were created. The original
baseline remains AutoUpdateSchema=true and ReadConsoleInput=false. Those future
persistent setup changes require explicit approval. Actual restored histories,
permissions, schema and Windows startup/persistence acceptance remain pending.
No approved entrypoint, Windows execution, full integration or runnable-alpha
claim follows from the40mock passes. Portable Web UI remains unverified.

Preservation is local only: the small review checkpoint contains source changes,
acquisition/execution/integration evidence and hashes, not the Linux runtime,
Windows candidate or database. No publication, main or workflow modification.
