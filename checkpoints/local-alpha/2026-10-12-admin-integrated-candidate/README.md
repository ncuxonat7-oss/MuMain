# Admin-integrated disabled Alpha: local package evidence

This checkpoint adds the unique local assembly and package-admission evidence to the preceding source-integration checkpoint. It does not duplicate its admin procedure, SQL, role-profile source, or 82-case unit-test implementation.

## Verified result

- New candidate: `control-admin-integrated-disabled-20261012`.
- Payload: 24,422 files, 1,417,254,100 bytes; including four control documents: 24,426 files, 1,427,995,168 bytes.
- Independent payload-inventory SHA256: `37a88628e89530fd9da8e295d2a289f1563a4dea06653d2de161178e26e519cd`.
- Input source-bundle SHA256: `28a139de1113f47ef47d36972f70c2684e655887e82dd1180fe6bec76483994e`.
- Actual Linux PowerShell 7.4.20: full existing StartMU Verify PASS/exit 0; 82/82 mocked-boundary source tests rerun PASS; eight package integration checks PASS.
- Five payload additions and four modified existing files; exact identities are in candidate-identities.json. Original package retained unchanged.

## Evidence interpretation

`candidate-identities.json` is the immutable assembly-time identity record. Its NOT_YET_POWERSHELL_VERIFIED status records that earlier point; `integration-result.json` and the two small result files record the subsequently completed verification. No candidate bytes changed after full Verify.

`runtimeGrantStatus=DISPOSABLE_PROFILE_PREPARED` means prepared source/profile only. `launchEnabled=false`, `approvedLaunchManifestSha256=null`, `setupApplicationApprovalSha256=null`; Windows and live validation remain NOT_RUN. The source tests mock external boundaries. Package tests prove the application-approval and launch gates reject this package before credentials or DB operations; they do not execute admin SQL or grants.

The first negative package-test attempt expected a custom missing-file error. The real guard raised ObjectNotFound. Only the test expectation was corrected, then all eight checks passed. No package code was changed to accommodate the test.

## Reproduction boundary

`assemble.py` is the exact local builder, not a standalone downloadable package installer. It requires the privately retained phase1250 sanitized payload (inventory SHA256 `69f7a0700ef387a23c75e0427044674974a54c0a987e6a788ab5bbf3c9aa2d5f`), the source bundle above extracted into source/scripts/windows11, and the existing phase2104 packager helper (SHA256 `c700e0ed3a0fe2a6bbd77de0f0bd5c60f814ca4dd49852cf15734473a53459e7`). It refuses an existing output directory and copies/hash-checks actual bytes without hardlinks. Those large payloads are not included here.

No database, credential bundle, binary, archive, raw private diagnostic log, signed URL or owner personal data is included. The two .txt result files are bounded status-only outputs. Source-integration files belong to the preceding commit, not this payload.

## One next step

Obtain separate authorization for one target-bound disposable setup and secure credential handoff; then verify actual admin provisioning/grants and PostgreSQL lifecycle before any separately admitted Windows HTTP/game/login/movement/save smoke. This checkpoint does not authorize these actions or certify Windows readiness.

Only the explicit pending-backup sentences in docs/current-state.md are reconciled with this evidence link, based on the confirmed preceding commit. All other navigation and first-checkpoint content is preserved.
