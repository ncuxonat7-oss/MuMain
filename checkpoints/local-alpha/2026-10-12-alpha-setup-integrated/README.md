# Integrated Alpha setup source and diagnostic recovery checkpoint

This public checkpoint is based exactly on `74394bbb8570ae7183952ada7c18cae8af6838f4`. It preserves completed unique stages only. Public disclosure of sanitized scripts, role profiles, tests and technical reports was explicitly approved on 2026-10-12; no database, credential, personal data or binary is included.

## Passed evidence

- Bounded disposable PostgreSQL role preparation: 62 final SQL checks, five rollback updates, expected privilege denials; data hash unchanged. These are SQL probes, not Typed/Account application reads.
- Account runner: offline review caught missing two-column AccountCharacterClass access. The separately approved grant was followed by a diagnostic identity failure (42501 reading privileged data_directory), before application data reads. The runner-only correction removed that privileged lookup while its controller retained maintenance target checks. The separately authorized continuation performed one GameConfiguration dependency read, one real Account load and one EF PositionX save inside a rolled-back transaction. Before/after data hashes match; 2,227 prior files preserved; PostgreSQL stopped. Historical failure evidence is retained beside the success, not counted as an automatic retry.
- Activation inspection: restricted metadata read, then separately authorized maintenance-only server association read; no broader grant or custom configuration values published. Aggregate/scoped activation evidence informs the role profile.
- Prepared seven-role setup profile and official admin provisioning integration: actual PowerShell 82/82 unit tests PASS (previous 54/54 preserved), external operations stubbed, zero utilities/database operations. Restore -> admin provision -> grants -> flags; application approval remains null. Official SQL and exact migration guards retained; fixed candidate EF identity bound. See source/IMPLEMENTATION-RESULT.txt for stubs and precise limits.

No tests, SQL, builds, game/server starts or credential work were rerun for this publication.

## Recovery

`files-manifest.json` hashes this checkpoint's files (excluding itself). `recovery-references.json` maps four unchanged files to exact existing repository paths at the base commit; restore them to their listed `restoreAs` locations to compose the source/test tree. Newly retained source bytes are unchanged from the completed stage. The preserved tests expect scripts/windows11 beside tests under source. The Account runner/controller are historical diagnostic sources, not an authorized deployment command or portable standalone package.

`upstream-source-provenance.json` pins recoverable MUnique/OpenMU sources instead of copying them. Official SQL already backed up upstream is referenced, not duplicated. The earlier candidate DLL and one-read evidence remain at ../2026-10-12-binary-json-read/README.md; binaries are intentionally absent.

Historical result/proposal files contain their original next-step text. Those queues are superseded by this README and the newest docs/current-state.md; never replay them as authority. The earlier exact-column diagnostic profile differs intentionally from the later prepared table-level smoke profile. Preparation does not establish live closure of its broader privileges.

## Parent candidate evidence and backup gap

The parent reports phase1552 candidate **24,422 payload files / 1,417,254,100 bytes**, inventory SHA256 `37a88628e89530fd9da8e295d2a289f1563a4dea06653d2de161178e26e519cd`, actual complete PowerShell Verify and eight package checks PASS. The parent owns adding its local candidate evidence AFTER this first commit. Those candidate report/control-file backups are **not yet complete in this commit**. This is a reported result, not a rerun or independently verified parent payload here.

Large payloads, disposable clusters, original dump and private inputs stay in their existing local/Library retention, not GitHub. Raw logs, account/custom-configuration values, connection settings, tokens/passwords, transfer URLs/helpers, games/archives, compiled binaries and redundant transport bundles are excluded. A text checkpoint alone cannot recover excluded databases, binaries or private environment state. The original executor files remain under /workspace/openmu-runtime-role-prep-20261012/ and its setup-integration-preparation/admin-integration/ directory; earlier originals under /workspace/openmu-single-read-20261012/.

## Single next step and limits

After the parent's pending evidence backup, obtain separately scoped Windows deployment/credential-handoff authorization. No deployment or credential handling is authorized by publication. Windows ACL/SCRAM, real fresh-setup admin provisioning/grants, HTTP/admin authentication, startup/background behavior, login/movement, committed save/relog and Windows readiness remain untested. No workflow change, main merge or readiness promotion. Setup application remains gated and launch false/null.
