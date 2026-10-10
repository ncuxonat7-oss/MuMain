# Bounded skill-41 native proof — preparation and blocked launch

Latest status: the owner subsequently launched run #14; the overlay preparation
fix and evidence limits below supersede the historical no-run/dispatch handoff.
See [exact input hash correction](#exact-input-hash-correction--2026-10-10).

2026-10-10. Task branch starts at main `6fdebbddb15e584a07ff9c18262a5ae78873683b`. The owner authorized narrow evidence tooling and one finite Twisting Slash learn/use/relog session on an isolated disposable restored snapshot. This supersedes the earlier permission/preflight wording in [draft PR #1 plan](https://github.com/ncuxonat7-oss/MuMain/blob/72c4c9ea44d09b358428ec427f0380e75592b563/docs/s6-gameplay-input-readiness.md). That PR and the separate PvP research branch are unchanged and unmerged.

## Prepared scope

`standard-gameplay.yml` accepts `scenario=skill41`; omitted/default `trade` retains the existing actor, main-branch control polling and cancellation checks. Skill41 uses the existing ordinary actor, reads controls only from the dispatched task ref and runs a separate persistence assessment. No arbitrary SQL/control executor was added. The initial task control remains `idle`.

Each existing snapshot call in skill41 mode additionally reads only the fixed actor's SkillEntry rows in an explicit read-only transaction. The output includes actor identity/existence, count and an explicit empty skills array. The ready-stage guard stops before control batches if skill41 already exists; no replacement fixture or skill removal is allowed. Capture failure also stops. Final evidence remains uploaded by the existing always-run preservation step.

The separate evaluator requires ready, `skill41-relog` and final snapshots, including `final-database.jsonl`. It checks absence initially, exactly the target skill added after relog, its presence after client exit, and initial orb identity/quantity. Both relog and final database captures independently check actor identity, global orb absence, other actor item IDs, Money and untouched core DK state against ready. Final capture occurs after client exit, not a server/PostgreSQL restart; restart durability is not proved. It does not infer gameplay from filenames: native learning/relog sequence must be reviewed. Accepted use/effect/cost and the full proof remain UNKNOWN until independently demonstrated; a persistence-only success is not a full gameplay PASS. No existing trade validator was modified.

Review fix: the initial evaluator compared final learned skills but omitted final database state. That omission is corrected with one shared scoped comparison applied to both stages. A missing final database file must yield UNKNOWN/nonzero exit; contradictory final state must yield FAIL/nonzero exit even with unchanged final learned skills. These are synthetic validator checks only, not gameplay evidence. Launch and draft-PR blockers below remain unchanged; readiness remains65.5/MEDIUM.

Review-fix validation PASS: Python AST and diff whitespace checks; two temporary synthetic negative cases. Missing final-database.jsonl returned UNKNOWN/exit1. Contradictory final actor identity, orb, inventory IDs, Money and core-DK state returned all five final assertions FAIL/exit1 while relog assertions and final learned-skill equality remained PASS. No old baseline tests, runtime, dispatch or PR call was repeated.

## Reused preflight and identities

The supplied saved-data preflight is reused, not rerun: actor `test300Dk` is Blade Knight class 6, level300, and qualifies for the existing orb's level80/class requirements. Orb(12,7) at inventory slot56 links ordinary skill41. One orb is already present; no purchase/grant is needed. Saved mana/AG exceed the configured 10/10 costs; runtime resources and weapon restrictions still require observation. Blade's own skill22 is not proof of skill41 usability.

- Actor: `511da101-0000-7171-e6b7-6ed8654174ee`; skill definition: `00000400-0029-0000-0000-000000000000`.
- Orb instance: `511da101-0000-780d-d7a9-a661c1e70ec8`; definition: `00000080-000c-0007-0000-000000000000`.
- Native pin `8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5`; OpenMU pin `d067b3c11c23c3145de6e2c76201ab9a93b267c8` with the current actual-storage Money patch.
- Existing baseline-data-final run38005996341/artifact11651520969: archive SHA256 `b40fbdbdb5c3bd9630331e0b9cb3bc7c1860db041a928bb976555635e03f79ea`; export SHA256 `8bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a`.
- Existing client run37813650810/artifact11567737809 and patched runtime run37959672391/artifact11630698202; exact Data/fonts and inner hashes remain in [resource registry](resource-registry.md).
- The fixed query's schema/columns were checked against [pinned SkillEntry mapping](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/Persistence/EntityFramework/CompiledModels/AccountContext/SkillEntryEntityType.cs), blob `5836575f2e47a2c9ac594e01243090cbd7f3a1f3`.

## Launch blocker and honest result

The existing CLI access path returned `Get "https://api.github.com/repos/ncuxonat7-oss/MuMain/actions/workflows/standard-gameplay.yml": Forbidden` on a read-only workflow metadata request. No dispatch operation is exposed by the available GitHub connector. This does not establish whether the repository itself would accept branch dispatch; that was not exercised. No new credentials, security permissions, alternate credential route or main merge were attempted. No workflow was dispatched, no run URL exists, and the one authorized gameplay run has not been consumed.

| Dimension | Result |
|---|---|
| Supplied saved actor/orb/class/level preflight | PASS within saved-data scope; reused |
| Local YAML/Python/embedded-JS syntax, diff and scope checks | PASS: YAML parse/default/permissions/timeout; Python AST; JS syntax in the Actions async wrapper; unchanged trade validator/command; fixed read-only query/empty-array guards. Not runtime tests. |
| PowerShell execution / live query | UNKNOWN; not executed locally |
| Skill absence in restored DB | UNKNOWN |
| Native learning, accepted use/effect/cost, relog persistence | UNKNOWN; no gameplay FAIL inferred |
| Canonical baseline safety | Unchanged; no DB restored, edited or promoted |

Draft PR creation was also blocked by automatic approval review, which cited the earlier read-only/no-commit/push/PR restriction. The current task authorization explicitly permits the new task branch and draft PR. The rejected action was not retried or routed around; resolve this authorization mismatch before creating the draft. Preparation is published on `task/skill41-native-proof`, initial code commit `998d346f1a84ccb67fd430d3f97503c6914c7242`; no task PR URL exists. Main, documentation PR #1 and the separate research branch remain unchanged.

## Single remaining handoff

Use an already authorized, supported dispatch-capable Work environment; do not provision credentials or merge this branch to work around the blocker. After reviewing this narrow tooling, dispatch `standard-gameplay.yml` once on the task branch with `scenario=skill41`, within the existing 25-minute timeout. Reuse the recorded binaries/resources and isolated snapshot. Review ready evidence before any learning; if skill41 exists or a runtime prerequisite fails, stop. Otherwise consume the existing orb through native UI, distinguish one skill41 use from skill22/basic attack using actual accepted effect/cost evidence, then relog and issue a snapshot batch named `skill41-relog`. Review the consumed native control sequence, screenshots and DB captures together. Unknown cost/effect evidence must remain UNKNOWN. Finish and retain narrow evidence without promoting the disposable DB.

No builds, grants/removals, stat/config changes, other skills/events or expanded fixtures. Stop after two identical failures or any new access/cost boundary. Readiness remains65.5/model1.1/MEDIUM. Future runtime risk/cost MEDIUM; preparation alone earns no gameplay credit.

## Exact input hash correction — 2026-10-10

Owner-supplied run evidence: [Standard Gameplay Session #14, run38065540919](https://github.com/ncuxonat7-oss/MuMain/actions/runs/38065540919)
stopped at Stage matching resources, before server/DB startup. The exact guard
correctly refused Group12_Wing.json, but its expected input hash described the
reviewed audit copy with one extra trailing LF, rather than the authentic input.
The origin of that LF is not attributed to any tool. The actual runner-file SHA
was not saved; only its Data archive SHA256
`8c62a98aaabf13d80c24c0c688dbfafd4b23813966dd3a2f13c445c3a35e8d1d`
was reported to match the frozen registry. No runner-file identity is inferred.

Authentic source: sven-n/MuMain, tag `data-4b0ab29c58b27fc4`, path
`src/bin/Data/Items/Group12_Wing.json`, Git blob
`e2d19fa0bab76df8b3eeb9d146a6529ece26d544`, 47,299 bytes, SHA256
`1bb0997c516e00be4658fc7c08bfd4e387abd11a731f9827cc334c5082a240bc`.
Retrieved through GitHub connector `github_fetch_blob`, with no shell download.
This connector exposed decoded UTF-8 content rather than a base64 envelope;
encoding that exact string without adding a newline reproduced both the Git
blob SHA1 (including the blob header) and SHA256 above. Thus byte identity was
verified, but direct inspection of the API's base64 envelope was unavailable.

Only `before_sha256` changed in the overlay specification. Path, tree, group,
all 14 approved corrections and output SHA256
`1441360f93d80291659f63912022e0816125863acd0212ab4ec02fca33ebbb73`
remain unchanged. A mismatch now reports actual SHA256, both expected SHA256
values and byte count before correction or writes, without file contents.
There is no trimming, whitespace tolerance or additional accepted hash.

Focused temporary-copy checks PASS:

- Authentic input applied to the unchanged expected output hash; backup was
  byte-identical to authentic input; no temporary output remained.
- Repeat returned `ALREADY_APPLIED`; no write/replace calls occurred and file
  bytes and modification times stayed unchanged.
- Authentic input plus an unexpected space was refused before correction,
  backup, temporary or target writes. Write/replace calls were instrumented to
  fail; the directory snapshot was unchanged and no backup/temp appeared.
- Authentic input plus LF was likewise refused. This reconstructed fixture
  was 47,300 bytes with the old reviewed SHA256
  `257d80a8738d24cae83afc68077fc3cbbcfb39b5637ce61f1e68c30ca6549da5`.
  Its parsed JSON and `corrected_bytes` output matched authentic input exactly.
  Both refusal messages matched the complete expected metadata-only diagnostic.
- Specification comparison confirmed that only the input hash changed;
  `git diff --check` passed.

The reviewed ZIP was not downloaded again: its previously supplied identity is
SHA256 `c68b65f373f09ff0c2a7f01dcafc3f8e1766ff7bdf7d6d50de6e666869354da1`,
Library `libfile_7131d39798708191a06116bb1ca38305`. The original audit-copy
comparison is reused evidence; this task tested the hash-identical reconstructed
extra-LF fixture. No old audits/tests, mix38 work, builds, runtime, DB operations,
workflow dispatch, PR or merge were performed. This is a local preparation fix,
not proof that staging or native gameplay now succeeds. Stop here; readiness
remains **65.5%, model1.1, MEDIUM**, with no new gameplay credit.
