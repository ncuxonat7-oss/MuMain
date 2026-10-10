# Skill41 use-only preparation and run17 result

Latest: owner authorized publication and manually launched run17, now terminal
SUCCESS. See the run17 result and deferred continuous-improvement decision below.
The original preparation-only scope in the historical sections is superseded
only by that one completed run; no further launch is authorized here.

2026-10-10. Owner authorized preparation only. Local branch
`task/skill41-use-only` starts from `393a232d4eceeab2043f0eeee7b7714ee0a5851c`
(the completed run16 control reset). No main changes, publication, PR or dispatch.
This document supersedes only the next-action wording for skill41; mix38 is closed.
Readiness remains **65.5%, MEDIUM**; no new gameplay credit.

## Proven result retained

Run [38078397211](https://github.com/ncuxonat7-oss/MuMain/actions/runs/38078397211)
completed successfully at source `5ea01c3c76322454069ab7078ce6df4eede83235`.
Native orb consumption and learned skill41 after client relog were confirmed;
Twisting Slash tooltip was identified. No cast was attempted: accepted
use/effect/cost remain UNKNOWN. A tooltip is not an effect screenshot.

Run16 `gameplay-final` artifact **11680250531**, 15,703,403 bytes, ZIP SHA256
`189ba4bf3e9715aef05d53517383d15abda4d1bbcb24e2b3579a8784ff7600f5`, contains
saved final evidence/DB. The workflow's persistence assessment succeeded; the
parent owns final ZIP inspection and durable private backup. No DB is copied
into this repository. Existing controls remain `idle`.

## Prepared harness

- New explicit `scenario=skill41-use`; `trade` remains default and the existing
  `skill41` learning scenario keeps its baseline restore and absent-skill guard.
- Use-only downloads only the fixed run16 artifact with existing workflow
  credentials/permissions. It checks artifact run/source/name, then the full ZIP
  hash before extracting only `gameplay-test-db.dump`. No old-base fallback,
  reseed, skill grant or repeated orb learning is allowed.
- Ready must contain the fixed actor and exactly the known skill41 entry
  `3a27a101-0000-72c9-8e81-6912c7b14844`, level0. Owner/skill/count/identity
  mismatches or any reappearance of the consumed orb stop before control polling.
- Both skill scenarios capture SkillEntry evidence and poll the dispatched
  task ref. Trade routing remains unchanged. No SQL/control executor was added.
- Final use-only assessment checks known skill identity, consumed-orb absence,
  actor identity/Money/other item IDs and untouched core DK. It reports
  `FIXTURE_PRESERVED`, never accepted-use PASS. No extra relog is required.
- New control operation `skill41-cast` is restricted to use-only and one attempt
  per session. After operator verification of selection/target it captures
  `skill41-use-before.png`, one right-click, `skill41-use-immediate.png`, then
  after100ms `skill41-use-followup.png`. UTC timing metadata is preserved.
  Existing click operations retain their2-second settle delay.

The click still holds its button for180ms. Immediate capture starts after
release without the old2-second settle, but capture latency and game scheduling
are unmeasured. The100ms pause follows completion of the first capture; it is
not a promise of an image exactly100ms after the cast. MP/AG regeneration can
hide cost even in these frames. Animation alone never establishes acceptance.
No Windows/PowerShell execution or artifact-download integration test was run.

## One candidate route, validated against matching client attributes

Only the small individual attribute blob was retrieved through the existing
GitHub connector; no Data archive/stack restore. Exact source:
[sven-n/MuMain, data-4b0ab29c58b27fc4, src/bin/Data/World1/EncTerrain1.att](https://github.com/sven-n/MuMain/blob/data-4b0ab29c58b27fc4/src/bin/Data/World1/EncTerrain1.att).
Git blob `34f0ee477c8f013ac01a41ee863cda6c2915d3fa`, 131,076 bytes, SHA256
`d294c19748c69ee6b0a1a3d2811329c410ecad1a380059474c9a769c38fe6306`.
Decoded using repository `MapFileDecrypt` + `BuxConvert`: header0/1/255/255,
65,536 little-endian16-bit attributes; native Lorencia sentinel(135,123)=5.
Start(118,140) has attribute1, confirming the safe-zone bit in this client data.

Recommended tile waypoints, moving along each axis-aligned segment:

`(118,140) → (115,140) → (115,139) → (114,139) → (114,129) → (97,129) → (97,128) → (90,128) → (90,129)`

41 single-tile steps. Every tile avoids static CHARACTER/NOMOVE/NOGROUND/
NOATTACKZONE flags and the known initializer NPC positions. First non-safe tile
on this route is **(95,128)**. The detour through y128 avoids NPC(96,129);
(90,129) is outside safe/no-attack flags. These are map coordinates, not screen
click coordinates. Dynamic occupancy, model collisions and server terrain are
not proven by this client attribute check. **Not native-walked.**

Pinned OpenMU `d067b3c11c23c3145de6e2c76201ab9a93b267c8` uses S6 Lorencia →
095d →075. The inherited [075 Lorencia initializer](https://github.com/MUnique/OpenMU/blob/d067b3c11c23c3145de6e2c76201ab9a93b267c8/src/Persistence/Initialization/Version075/Maps/Lorencia.cs)
(blob `afe02b6b11d681edbef9949887b5b62449763efe`) places Hound1 and Elite Bull
Fighter4 in x8..94/y11..244,45 each. Existing `s6-baseline-diff.json` records
these spawn projections as MATCH to the preserved baseline. The destination is
inside their configured area, not a guaranteed monster location. NPC guards
near the gate are not targets. Actual living hostile target must be identified
on screen before use; no target or failed prerequisite means stop.

## Minimal future run checklist (launch requires separate authorization)

1. Publish/review this preparation only when authorized. Keep controls idle;
   select `skill41-use`, never silently reuse the learning scenario/base.
2. Verify exact run16 restore, known skill ready guard, actual actor position,
   HP/resources/equipment and live prerequisites. Do not learn again.
3. Walk the candidate waypoints in small image-grounded native batches, checking
   map position and obstacles. Do not guess pixel coordinates from tile values.
   If blocked or no nearby legitimate hostile target, finish with use UNKNOWN.
4. Select **Twisting Slash** by tooltip, not Cyclone/skill22 or basic attack.
   Establish before MP/AG, selected skill and target state. Do not hold attack.
5. Send one `skill41-cast` with verified client-pixel target coordinates, optionally
   followed by `snapshot`. Review before/immediate/followup PNGs and UTC timing.
   Require coherent MP/AG cost accounting including regeneration plus target
   damage or appropriate server-side evidence. Current logs may not expose the
   needed accepted-hit record; missing evidence stays UNKNOWN, no repeat spam.
6. `finish` before timeout; inspect final snapshots, fixture assertions and logs.
   Preserve images as effect evidence only if their content supports that claim.
   Reset controls after terminal completion. No unnecessary relearn/relog test.

Example control structure only; X/Y must be supplied from the actual image:
`{"id":"unique-use-batch","steps":[{"op":"skill41-cast","x":X,"y":Y},{"op":"snapshot"}]}`.

## Offline validation and remaining limits

`PYTHONDONTWRITEBYTECODE=1 python scripts/test-skill41-use.py`: **8 tests PASS**
(including subcases): ready/final CLI retains UNKNOWN accepted use; missing,
wrong, duplicate and mismatched-owner skill entries rejected; actor/orb guards;
missing final evidence; changed Money/core; archive hash rejection before writes;
fixed-member-only extraction; scenario/control/timing source contracts.
YAML parse, Python AST, embedded Actions JavaScript syntax and diff whitespace
checks PASS. Timing/PowerShell checks are source-contract checks, not measured
Windows behavior. No previous learning/persistence/gameplay tests were repeated.

Remaining runtime limits: actual Windows execution, Octokit ZIP transfer,
server terrain equivalence/dynamic blockers, native route traversal, living target,
resource/accepted-hit observability and capture latency. No full accepted-use
PASS or guaranteed effect screenshot is claimed by this preparation.

## Run17 — completed, use not attempted

[Run38080436067](https://github.com/ncuxonat7-oss/MuMain/actions/runs/38080436067)
ran on `task/skill41-use-only`, source
`f40e3ba1c331f338cef386aa296c84e794f6c813`, 19:35:56Z–19:53:28Z on
2026-10-10, terminal **success**. Scenario was confirmed by the executed use-only
restore steps and skipped old-baseline restore. Exact run16 archive/fixture
guards succeeded; ready evidence confirmed the known skill41 entry and initial
Lorencia(118,140), HP110, Mana176, AG115. No relearning or orb action occurred.

The sole controller issued nine native batches, ending with `r17-finish`.
Parent inspected the actual screenshots. Observed route positions were
(118,140) → (117,138) → (117,135) → (114,135) → (114,131) →
(114,129) → (109,128) → **(101,127)**. This verifies only those observed native
navigation milestones, not the entire planned route or every intervening tile.
Two-second click settle was insufficient to assume full arrival; a settled
capture and longer waits were used. No blind world-to-pixel conversion was
treated as exact. Visible Guard/Phantom Soldier NPCs were not hostile targets.

A legitimate hostile target and completed safe-zone exit were not established
within the bounded command window. **Cast: NOT_ATTEMPTED (zero
`skill41-cast` and zero generic right-click use commands). Accepted
use/effect/cost: UNKNOWN.** This is not evidence of a skill defect and does not
add gameplay credit. No actual-effect screenshot exists for this run.

Live session, use-only fixture assessment and final preservation all succeeded.
Final artifact **11680249154**, `gameplay-final`, 19,553,117 bytes, ZIP digest
`sha256:f24fa559f55cea9274a715a71bd365ee0f51854e5b030f6d645325286af3d58e`,
expires2027-01-08T19:35:57Z. It preserves final snapshots/DB, assertions, logs and
`r17-final-position.png`. These artifact properties and assessment outcome were
verified through GitHub; this controller did not download/inspect final ZIP
contents. The parent must inspect final DB position and retain a private durable
copy before any future fixture decision. Last visually verified position101,127
is not independently claimed here as read-back from the final DB.

Useful artifact identities:
- Ready:11679748531, `gameplay-ready`.
- Route calibration:11680462203; second calibration:11680193105.
- Joined route:11680367932; turn:11680328138; settled:11680471654.
- Gate approach:11679759477; passage:11680288667; bridge:11680701717.
- Final:11680249154.

Finish command commit:`f22d194f41d4210426eccadcfdc81abc979ae229`.
After terminal completion controls were reset to `idle`:
`07a31ee9f18ec6168d46b2e8a4f44f2579409162`, blob
`99c959c6f162f82c1d532deb42fe60e1d90ef0a8`. No main changes,
new dispatch, game/source changes, grants or access changes were made during
the run. Readiness remains **65.5%, MEDIUM**.

Exact unfinished work: accepted skill41 use against a verified hostile target.
Before proposing another run, retain/review final evidence and prepare the narrow
isolated fixture described in the run17 lesson below; do not default to more
route calibration. The current
workflow remains pinned to run16; do not silently restore run17 or relaunch.

## Deferred owner decision — CONTINUOUS IMPROVEMENT

Owner explicitly requested saving this deferred task at19:49:57Z on2026-10-10.
It is a future architectural backlog item, **not current implementation scope**.
Wait until the test pipeline is stable. Do not build new orchestration,
automation, access paths or architecture while finishing the skill41 work.

When subsequently authorized, evaluate recurring patterns by frequency,
demonstrated root cause, time/credit cost and expected return on investment.
Choose one appropriate specialist for the localized task rather than expanding
agent orchestration. Define success criteria, a bounded budget, rollback and a
concrete GitHub result before implementation. Preserve all applicable approval
requirements, including separate authorization for publication, costly/runtime
work, access changes and new test launches. This backlog entry does not grant
standing permission for any of those actions and earns no readiness credit.

## Run17 lesson — simplify the next test fixture

The owner correctly challenged spending most of a skill-use test on native
navigation. Navigation was not the acceptance target; the observed workflow
spent its bounded window reaching101,127 without attempting the actual cast.
Further route calibration should not be the default next skill41 test.

Recommended next preparation: a narrowly reviewed, disposable isolated fixture
which positions the existing learned-skill actor beside a controlled legitimate
hostile target in a verified attack-permitted area. Preserve the already proven
learning result. Any injected positioning or target setup must be explicitly
recorded as **test setup**, separate from the subsequently observed native
selection/cast, resource accounting, damage/server evidence and screenshots.
Do not claim native travel, spawning, learning or full end-to-end gameplay from
injected state. Never mutate or promote this fixture into the production or
canonical baseline.

Prepare the exact allowed fixture delta, target identity, safety conditions,
before/after checks and teardown for review before implementation or launch.
This entry records the approach only: no character relocation, target creation,
DB modification, fixture implementation or new run occurred in this turn.
A future fixture must stop if its prerequisites or evidence fail; setup alone
does not establish accepted skill41 use.

This small test-fixture simplification is separate from the broad deferred
CONTINUOUS IMPROVEMENT architecture. That architectural backlog remains parked,
and existing approval requirements remain in force.

## Owner decision — normal-player validation on the owner's PC

2026-10-10 at19:56:24Z, the owner asked:
«Оставь как у обычного игрока на меня, когда запущу на ПК игру,так будет нормально?»
The agreed division of work is:

- The owner performs normal-player end-to-end usability/playthrough validation
  on his PC. Agents will provide a short, concrete owner checklist later.
- Agents remain responsible for isolated prepared mechanical tests,
  outcome/persistence checks, technical diagnosis and relevant security and
  integration checks. This does not transfer all technical bugs to the owner
  or exempt agents from investigating them.

Reason: avoid spending agent runtime on navigation when navigation is not the
mechanic under test. A fixture may prepare actor/target state, but injected
setup must remain explicitly separate from observed native actions/results.
Fixture PASS is never evidence that the complete ordinary-player journey passed.

Revisit this division if automated native end-to-end testing becomes
cost-effective or an integration regression warrants it. The broad CONTINUOUS
IMPROVEMENT architecture remains parked. This is a recorded ownership/testing
decision, not implementation or launch authorization; no new run, source change,
runtime action or baseline mutation accompanies this entry.

## Next preparation — guided player QA with digital evidence

Owner proposal,2026-10-10 at19:58:38Z: give prioritized “go here / check this”
tasks and collect digital reports/logs instead of relying only on verbal feedback.
This is the **next preparation before owner PC testing**, linked to
[the owner PC validation decision](#owner-decision--normal-player-validation-on-the-owners-pc).
It is not active implementation, an architecture selection or a launch request.

Platform is **UNCONFIRMED**: the owner said “APK client”, while surrounding
context concerns PC play. Clarification is pending; PC is provisional only.
Do not interpret this entry as authorization for an Android port.

Minimal proposal for later review:
- GitHub test IDs with priority, short steps and expected result; each report
  attaches to one test and the exact tested version.
- Simple owner start/stop and result choices: pass, fail or unclear.
- A bounded diagnostic bundle: timestamps, client/server versions or commits,
  relevant logs, and optional screenshots/video only with owner consent.
- Exclude credentials, tokens and personal data. No automatic unrestricted
  script execution, unrestricted uploads or third-party sharing.
- Prefer existing GitHub plus a small collector, if needed, over a new web
  platform, backend or subscription. This is a preference for evaluation,
  not a committed design or permission to install a collector.

Draft acceptance criteria:
1. An agent can reconstruct the test context from its bundle and tie each item
   of evidence to one test ID/version; missing evidence is explicitly flagged.
2. Secrets and personal data are filtered; a filtering failure prevents sharing.
3. Owner actions remain minimal, with clear start/stop and pass/fail/unclear.
4. Collection can be switched off, with a defined rollback/removal path.

No implementation, script installation, collection, upload of diagnostics or
test launch is authorized by this documentation entry. Any subsequent execution
or data transfer remains subject to the existing approval requirements.
The broader CONTINUOUS IMPROVEMENT architecture remains parked separately.
