# Skill41 use-only preparation — local, not published or launched

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
