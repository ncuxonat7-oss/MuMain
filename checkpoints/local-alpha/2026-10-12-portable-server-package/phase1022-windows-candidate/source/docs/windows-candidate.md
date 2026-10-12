# Disabled Windows server candidate

This is a private intermediate component, not a ready Alpha or installer.
The source-specific Python recipe reuses the existing reviewed checked-copy
helper and exact pinned overlay plan. It never installs or launches a program,
opens a database, changes credentials, rebuilds or fetches inputs.

From the existing workspace, verify the completed component:

    python phase1022-windows-candidate/source/scripts/package-windows-candidate.py verify --workspace ${WORKSPACE} --destination ${WORKSPACE}/phase1022-windows-candidate/control-server-candidate-20261012

The launch-check action checks integrity and then deliberately returns a nonzero
LAUNCH_DENIED result. It is not a launcher. No editable status flag enables it.
The stage action accepts only a new destination. Failed partial output remains
incomplete and is preserved; do not retry into it or delete it automatically.
Verification needs the pinned original local plans/manifests/helper; it is not
claimed to be a standalone transferable verification distribution.

Included: 183 server files and 12 unchanged disabled launcher/setup source files.
All 195 copied files have actually passed size/SHA256 verification. The previous
large client/Data/fonts/Windows-dependency control is referenced, not copied or
recertified here. Original controls, archives and source files are unchanged.
The 183-file set has 93 identities reused from the old Windows server and 90
replacements from the coherent candidate build plus the new EF DLL/PDB pair.
The three Linux apphosts and three obsolete Windows .exe entries are omitted only
from the new component. Invocation using dotnet Startup.dll remains untested here.

candidate-integrity.json records every exact source/target/identity, exclusions,
source-plan pins and original provenance. It does not forge a new old-runtime
archive or change the legacy launcher from 186 to 183 globally. Consequently,
legacy launcher runtime provenance is not aligned with this new payload and
remains a blocker. Both the local session contract and candidate status are
false/null; no approved launch manifest exists. Original first-setup grant fences
are included unchanged, including the separately pinned blocked policy.

Five staticwebassets.runtime.json files still contain Linux build paths. Their
bytes were copied unchanged and verified; portable Web UI is explicitly blocked.
Do not repair them or assume the admin-disabled switch proves them optional.
The known one-GameConfiguration-read evidence does not cover Typed reads, complete
runtime permissions, ordinary startup writes, Windows loading or gameplay.

Next necessary step: review the exact candidate and decide the narrowly scoped
Windows admission procedure before any execution. Runtime provenance alignment,
web-asset portability disposition and unresolved setup permissions must be
explicitly resolved or retained as blocking gates; do not bypass them. Actual
Windows/DB/security/setup/startup requires separate authorization. No normal
first-deployment command is currently ready.
