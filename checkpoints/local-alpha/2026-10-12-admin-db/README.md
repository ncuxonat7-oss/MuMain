# Admin-only disposable database checkpoint — 2026-10-12

Owner-authorized preservation branch `checkpoint/local-alpha-db-20261012`, based on `e15e53eaeb3bf2229864f538c2073f10ad35bbb0`. This follows the [C# checkpoint](../2026-10-11-csharp/README.md); main and deployment remain unchanged. Overnight authorization at 02:36 UTC was renewed at 02:49 UTC. No DB tests were repeated for publication.

## Result and evidence

**PASS, bounded admin scope only.** Existing official EF10.0.2 generated both admin migrations through AdminPanelContextFactory; no Startup application was launched. [Exact invocation](evidence/generate.sh), [generator output](evidence/generator.log), [detailed report](evidence/REPORT.txt), [machine-readable results](evidence/results.json), and [source/script hashes](evidence/source-and-script-hashes.json) retain the actual proof.

Admin history is 2/2 with generated ProductVersion `10.0.2`; game history is 63/63 unchanged. Configuration IDs and original AutoStart=true, AutoUpdateSchema=true, ReadConsoleInput=false remain unchanged. All non-admin data-only dump streams matched SHA256 after excluding only random psql restrict markers. No records or streams are published.

The diagnostic NOLOGIN role had database CONNECT, admin schema USAGE, SELECT-only history, and SELECT/INSERT/UPDATE/DELETE on AdminUser/ApiKey. No ownership, memberships, superuser, database/role creation, replication, bypass-RLS, schema creation, TEMP, history writes or extra table privileges were granted. Reviewed zero-row full-column reads/CRUD passed and rolled back; no admin records exist. This does not prove actual row constraints, EF query equivalence, navigation closure or Windows acceptance.

Every database attempt stopped: [shutdown log](evidence/shutdown.log), [status](evidence/shutdown-status.log), and results prove no running postmaster/PID/socket. Initial PostgreSQL17 collation-query and SQL_ASCII BOM failures were recovered as recorded. The original generated SQL is preserved; the execution copy removes exactly its three BOM bytes, with [both hashes](evidence/sql-encoding-adjustment.json). No handwritten migration replacement was used.

## Preservation boundary

The [file manifest](files-manifest.json) covers exact copied diagnostic bytes. Scripts are historical evidence with fixed disposable paths, not a deployable installer or authorization to rerun. Private local archives, binaries, database directories/dumps/rows, credentials, certificates and signed transfer material are excluded. Harmless disposable paths and diagnostic role names remain to preserve invocation/hash identity. SQL column names such as PasswordHash refer to schema only, never account values. Source/input hashes identify excluded originals; they do not claim those originals are backed up by this branch.

The [transfer recovery runbook](library-transfer-runbook.md) records the verified transfer procedure and its limits. The previous restore proposal's flag-repair step is superseded by the owner's later preserve-original-flags instruction. Entity/Typed complete closure, package alignment, Windows readiness and full Alpha readiness remain unproven. No readiness score changes.

The [admin integration implementation](implementation-report.md) is complete with 49/49 admin and 56/56 setup mock checks. The earlier [integration proposal](next-stage-proposal.md) is now historical; its later Windows-route reference remains a limit, not an authorization.

**Single next step:** the source/metadata-only startup GameConfiguration read-closure proof defined in the implementation report. Complete Entity/Typed closure, package alignment and Windows readiness remain unproven.
