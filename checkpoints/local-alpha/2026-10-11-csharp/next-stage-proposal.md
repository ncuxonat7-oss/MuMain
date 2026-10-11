# One next bounded stage — proposal only

A MEDIUM disposable PostgreSQL17 restore-and-permission acceptance, on the current
host in a new isolated directory, would close the largest deployment gap. It
requires separate approval for the exact PG17 distribution/dependencies, local
listener, temporary roles and protected credential handoff; none is installed,
created, connected or run by this checkpoint. If a suitable official user-local
PG17 distribution is unavailable within the approved cap, stop rather than adding
system services, Docker or changing architecture.

Proposed cap:30minutes, one pinned baseline restore, no game/server launch,
no public/network exposure, no real user account data import beyond the already
approved test snapshot, and no broad source audit. Input archive11651520969 and
its dump must match the recorded hashes. Use a fresh disposable target; refuse
existing directories/databases and keep the original dump read-only.

Tasks within that one stage:
1. Verify PG17/source/baseline identity, loopback-only isolation and ownership.
2. Restore explicitly into the new target under setup-only authority; do not grant
   runtime CREATE, ownership, superuser or broad default privileges.
3. Reconcile the exact source-derived table/read/write closure for the selected
   Alpha features against the restored catalog. Validate both independently pinned
   migration histories, config IDs and expected endpoints. The restored database
   must never be its own source of expected migration identities.
4. Exercise the required context queries and narrow transaction-rolled-back write
   probes under each restricted runtime role; verify admin external-history
   mismatch fails and no migration/create/lock path is invoked. At a missing grant,
   record the precise source/query need; no blanket GRANT ALL fallback.
5. On that copy only, apply the reviewed ReadConsoleInput=true and
   AutoUpdateSchema=false transaction with exact before/after guards. Preserve
   sanitized results, explicit grants and ownership/stop/retention state. Stop on
   unsupported privilege assumptions or insufficient time; no claim of full pass.

Success yields a reviewed actual-PG grant/restore contract, not a running Alpha.
The subsequent Windows candidate is a separately approved step: integrate the
newly tested server identities and strict mode into a fresh disabled package,
retain old controls, and verify Windows loader/ACL/process/config acceptance.
No repeat C# build/tests without a concrete source or binary change.
