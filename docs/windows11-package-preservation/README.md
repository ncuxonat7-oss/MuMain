# Packaging preservation checkpoint — 2026-10-11

Owner authorized separate-branch preservation at 17:42:48 UTC. This branch
preserves source and sanitized historical evidence; it is not a runnable package,
activation approval or the authoritative owner-strategy branch.

## Exact chronology

- Published launcher baseline: 7f5b44a930a501dfc7ea4f522584cb59a22c9499.
- ebebc705793c4f13193c785485871018fe97fa6c: packaging recipe, five tests and initial evidence.
- a803f34ebba25308c35c605875c17a8c65c62672: archive identities and Library output failure.
- 33eda238e0234f257d8d1e880feb50b4ce9b1205: pinned client source requirements and then-known blockers.
- This documentation-only commit retains those commits unchanged and copies four
  small historical records. Their test output is a previous run, not a new run.

Read current owner decisions on docs/s6-owner-strategy-2026-10-10, observed at
effe8a16b51fe2558c4fda39e09cd1ce6d1e5033 before preservation. Historical statements
that packaging was unpublished describe their original dates. Likewise, the
old migration notes are incomplete: the independent 09:21 source checkpoint
identifies EntityDataContext and AdminPanelContext separately. No source or
runtime migration audit is performed or claimed by this preservation commit.

## Recovery inputs

Use scripts/package-windows11-local.py and tests/windows11/test_packaging.py.
The recipe requires an existing checkout with exact launcher baseline7f5b44a9
files. It reads pinned Data tree77f7830f542d106fc519c8821832d49a3dd8ae3a and
fonts tree149f928e2547aa6658977c3f41c63abccfa471ed, copies eight launcher files,
and reuses scripts/apply-client-overlay.py plus patches/client-socket-metadata.json.
Expected Group12 output SHA256:
1441360f93d80291659f63912022e0816125863acd0212ab4ec02fca33ebbb73.
Read-only provenance comparison covered all13,209 inventory source-blob references
and found zero unmatched entries. No asset bytes were rehashed for this review.

The recipe generates an available-input inventory, draft manifest and incomplete
status in a fresh destination. It does not retrieve missing dependencies or
provision a database. Keep launchEnabled=false and approved manifest digest null.
Database/endpoints remain null in the archived draft. There is no unique prepared
DB, secret or laptop configuration to recover from this candidate.

## Limits and original artifact identities

The complete ZIP assembly procedure and all hand-authored archive evidence are
not encoded in the recipe. Exact byte-for-byte ZIP reconstruction is UNPROVEN.
The ZIPs, large inventories, Data/font binaries and original asset backup are not
added by this preservation change. Existing inherited Git assets remain unchanged.

Historical full ZIP: 470974707 bytes, SHA256
fb1f389a640bb83b9bfedbf14526655647031600e48402358e94f9a1d55b3f28.
Historical review ZIP: 2138966 bytes, SHA256
0e51834cfec24be6b93241d5416d9e6b14af2aee955406623c853abb2306eafe.
Inventory SHA256: 14f6ff7096579cca0b1eac0a4336a8ea91af349e1d2bd9d446439a0a9fe3f00f.
Draft SHA256: 30e7a94ef5e801447767a8d4053cbcbcdcb006501ba070ded0eda37fb04c826f.
Historical readback: 13223 payload members plus checksum catalog. Previously
verified archive hashes were not recomputed for this publication.

Server/client binaries and Windows dependencies were absent from that candidate.
Server expected archive SHA256:
505d1053d235417876c59f31e2dbb0338bad955dee31c193ccf167da28355f8c.
Client expected archive SHA256:
eefe0a710518bc6536dd47cde45fb8605ae4ef5c7f4faca4095e8abb5f23297e.
Parent-host server verification does not establish consumer-local availability.
Latest documented consumer transfer still failed with
`library file transfer failed: download failed`; hosted helper discovery also
previously returned `hosted apps tools/list request failed: network`.
No new Library identity exists for either package output. No credential or
permission cause is inferred from these errors.

## Publication safeguards and validation scope

All preserved packaging commits and this commit use [skip ci]. Read-only workflow
review found push CI, main-only data publishing, manual workflows and PR/issue
handlers. GitHub documents [skip ci] for push workflows:
https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs
No workflow files change; no PR, dispatch or main update is part of preservation.

New verification is limited to small-file/history review, secret/private-URL and
binary screening, whitespace validation and publication readback. No tests,
builds, package regeneration, Windows execution or installation are performed.
