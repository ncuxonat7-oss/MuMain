# OpenMU source preservation, not MuMain client code

Base: MUnique/OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8.
Apply the existing pinned Money and local-bind patches first, then
openmu-admin-preprovisioned.patch. This eight-file patch supersedes the earlier
phase2049/phase2104 admin patches: five server C# files plus three C# test files.
It includes the minimal internal test seam used in the successful C# run.
Do not apply both old and new cumulative admin patches.

The source/ tree is a namespaced preservation copy; do not copy it into MuMain/src.
All eight after-files match the tested source manifest in the checkpoint evidence.
No binary, database, credential or SDK cache is included. Upstream MIT LICENSE
and per-file copyright notices are retained.

Default valid server settings retain runtime migrations. Only the explicit admin
connection AdminSchemaManagement=ExternallyProvisioned uses the new read-only
history-validation path. Staged launcher requires that exact value. Nothing here
activates the default build output or completes first setup.
