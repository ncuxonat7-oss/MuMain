> Current external checkpoint: [actual C# build/test evidence](../checkpoints/local-alpha/2026-10-11-csharp/README.md).
> Earlier phase-specific NOT_RUN statements below are historical; the current packaged baseline still remains disabled and unintegrated.

# Admin availability caller: source-only concurrency correction

This candidate continues the exact local phase2049 server patch and pinned OpenMU
source d067b3c11c23c3145de6e2c76201ab9a93b267c8. It changes only the caller's
pending-check/cache behavior. No grants, schemas, real DB, credentials, binary,
Windows configuration or deployment changes are included.

## Required behavior

A concurrent first authorization request cannot receive initial cached false
before the repository has validated the external schema and counted users.
Pending callers wait with cancellation rather than entering unverified bootstrap.
External history mismatch, permissions failure and other repository exceptions
must propagate and must not publish a fresh false cache. Invalidating a cache
while an operation is in flight must prevent that older operation from publishing
or returning a stale result as authoritative. Semaphore ownership must be released
on all acquired paths, not on a canceled acquisition.

A genuinely completed zero-user check may still return false under the existing
initial-setup contract. A configured bootstrap user returns true (authorization
required); that existing shortcut is not rewritten. Legacy repository handling of
unavailable fresh installs is not broadened into a new authentication architecture.

## Evidence limits and gates

Local static checks and Python behavioral models cannot execute C# or prove CLR
concurrency, serialization, provider behavior or whole-panel integration. A source
review narrows the known race; actual C# compilation/tests and an approved new
binary remain mandatory before treating this as runtime evidence.

The source policy stays hash-pinned and blocked before mutations. Full Entity/
Typed grants still stop explicitly because read/navigation and emitted-write
closure have not been established. No broader grants are inferred here.
launchEnabled=false; approvedLaunchManifestSha256=null. Prior binary inventories,
compiled migration evidence and successful game tests remain about their original
bytes, and are not relabeled as proof of this source patch.

## Next bounded deployment path

First establish the exact Entity/Typed permission profile or obtain an explicit
owner decision on a narrower supported feature profile. Then separately approve a
build/C# test of the pinned source with Money/local-bind and these local patches.
Record the new source/binary identities; update disabled packaging contracts only
after they agree. A real isolated Windows PostgreSQL restore, restricted-role and
authorization acceptance requires its own approval. No installation or launch is
automatically authorized by this document.
