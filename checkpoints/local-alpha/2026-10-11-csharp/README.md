# Local Alpha checkpoint: actual C# proof, deployment still disabled

Checkpoint date: 2026-10-11. Separate preservation branch based on the existing
reviewed launcher commit 7f5b44a930a501dfc7ea4f522584cb59a22c9499. main, other
branches and workflow definitions are not changed. Commit uses [skip ci]; no
workflow dispatch, PR, merge, game/server start or test/build repeat is authorized.

## Current evidence

- Startup Release build with official SDK10.0.401: PASS, 0errors, 247warnings.
- Actual C# NUnit:14caller +15repository tests PASS,0failed,0skipped.
- Strict EF test doubles replace I/O only; the changed repository/service methods
  execute. No PostgreSQL was invoked; SQL/permissions and HTTP end-to-end remain
  unproven. Existing unsafe immediate-false regression was replaced, not skipped.
- Candidate EF/AdminPanel assemblies match executed test copies by SHA256.
- New compiled migration metadata retains63game +2admin identities.
- Candidate is framework-dependent net10.0 with Linux apphost, not Windows RID
  publish. The Startup application was never launched.

The [warning assessment](warning-assessment.md) separates247unique diagnostics
from duplicated log output and evaluates five ImageSharp advisories without an
unapproved upgrade or broad audit.

## Source layout and version boundaries

The22current MuMain packager/guard/setup/docs/test files live at their normal repo
paths. The [namespaced OpenMU patch](../../../../patches/openmu/preprovisioned-admin-20261011/README.md)
contains five server source files, the real C# tests and internal test seam.
Original Launcher/Money/local-bind/client/Data baseline identities are retained.

The active database-source-contract and package pins still describe the OLD
verified runtime11689365514, not the new unintegrated build. This is intentional.
New assembly hashes are evidence, not an automatic repin. The copied setup policy
and grant setter remain blocked; launchEnabled=false and
approvedLaunchManifestSha256=null. Current packager guard hashes may reject newer
unintegrated guard bytes; no false integrated-package readiness is claimed.

Earlier phase reports under history/ are historical evidence. Their NOT_RUN/
source-only statements do not erase the later29CSharpPASS; conversely, later tests
do not retroactively validate old binaries or actual PostgreSQL/Windows behavior.

## Publication hygiene

Only allowlisted UTF-8 source, small manifests and sanitized reports are included.
Private Library reference IDs and local account/workspace paths were redacted;
public artifact IDs and hashes remain. Synthetic unit-test placeholder strings
from the public pinned source are not real credentials. No DB rows/dumps, logs
containing private data, binaries, archives, SDK/NuGet caches, PFX/private keys,
private home or certificate path are published. The automatic SDK development
certificate side effect was reported privately, not exported, trusted or deleted.

See [unbacked inputs](unbacked-inputs.json) for exact provenance and gaps. This
checkpoint does NOT newly back up the large inputs or temporary build binary.
GitHub Actions artifact retention may expire; references are not a durability
claim. Existing upstream repository assets remain in branch ancestry; this commit
adds no large game payload.

See [next bounded stage](next-stage-proposal.md). It is a proposal only and requires
separate approval. No additional stage begins from this checkpoint.

Publication-only metadata redaction/status banners are listed in sanitization-map.json. No executable control flow was changed by sanitization; original test passes are recorded against their original hashes, and tests were not rerun for this publication-only transformation.
