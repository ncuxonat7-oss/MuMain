# Portable server component checkpoint — 2026-10-12

This preserves two completed local packaging stages, not a runnable Alpha or Windows acceptance. Owner approved public source/evidence preservation on a separate checkpoint branch; no main merge, workflow dispatch or new execution is included.

## Results

- Phase1022: 183 server files (93 prior identities + 90 replacements), plus 12 unchanged blocked launcher/setup source snapshots. All 195 copied files / 132,594,731 bytes verified. Twenty new small-fixture Python integrity tests passed. Actual launch denial and overwrite refusal passed.
- Phase1042: exactly one existing-SDK `dotnet publish --no-build --no-restore` attempt, framework-dependent, `UseAppHost=false`, no project rebuild. An MSBuild guard rejects compilation or restore. Exit 0 in 31.891 seconds. All 110 DLL and 25 PDB outputs matched the saved phase2129 build. Five known ImageSharp 2.1.11 security advisory warnings remain unresolved.
- The raw publish output had the known old EF DLL. The final component explicitly retains corrected EF SHA256 `67adf087ec8f0d3de395740f0ce09e8040777698085747fdb23d89fee4f393a1` and matching PDB `3a9a9fd0e8d0d0047383ed721e389f7b576b6f95c13d3ca55b3a43ff57c41e71` through the already accepted overlay identities.
- Final published component: 8,440 server/web files + 12 unchanged source snapshots, 134,967,375 payload bytes. 16,681 Publish endpoints reference exactly 8,267 existing relative web asset files. Build runtime manifests and native apphosts are absent. Active top-level JSON/config and endpoint references contain no Linux build paths. Actual full copy/readback, launch denial, overwrite refusal and old-candidate preservation checks passed.

This closes the build-path packaging defect for the published layout. HTTP rendering, authentication, Windows loading and gameplay were NOT_RUN. It does not establish that the panel is optional. Client/Data/fonts/Windows dependencies remain in the prior retained control; this is a server component, not a new full client package.

## Preserved material and recovery

The phase directories below mirror the original relative workspace paths and contain unchanged unique scripts/tests, input pins, exact text inventories and sanitized result records. To recover the original layout, place them under a chosen workspace root. Scripts remain deliberately tied to their pinned earlier local inputs; this repository checkpoint alone is not a standalone replay environment and contains no runtime binaries. Do not silently bypass missing input pins.

The complete 8,440-file raw publish inventory and 183-file overlay plan are preserved. Large derived final control manifests are reproducible from those rows and the included exact assembly recipe; their original identities are recorded in derived-control-identities.json rather than duplicating multi-megabyte rows. Published manifests contain paths, sizes and hashes only, not asset contents. The accepted DLL/PDB identity is separate from the raw publish inventory's stale EF entry.

Absolute workspace identifiers in reports/command records are replaced with `${WORKSPACE}`; source scripts/tests are unchanged. sanitization-map.json records before/after identities. Raw publish.log, binaries, archives, DB/dumps, configuration contents, credentials, personal data and signed URLs are excluded. Existing upstream/helper sources are not duplicated unnecessarily.

## Remaining gates and single next step

Launch remains false/null; no approved launch manifest exists. Full runtime grants are unresolved; the old launcher runtime archive/count contract is not aligned with the new published payload; first-setup fences remain. Windows/HTTP/runtime acceptance is unproven. Baseline and readiness are unchanged.

**Single next step:** review and scope the narrow candidate-to-launcher admission alignment, pending separate owner approval before implementation. Do not activate setup, expand grants, run Windows/game/DB tests, rebuild or repeat completed audits under this checkpoint authorization.
