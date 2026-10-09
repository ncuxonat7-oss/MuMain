# Minimal runtime checklist — checkpoint2026-10-09

|Scenario|Status|Evidence / limits|
|---|---|---|
|Auth/character selection/DK/Lorencia|VERIFIED; do not repeat|run37830707804, native client + PostgreSQL17.11|
|Warp Lorencia↔Noria|VERIFIED; do not repeat|run37846640006, actual saved Zen debit|
|Shop purchase Small Shield|VERIFIED; do not repeat|same run,230Zen; inventory47 before equip|
|Normal kill/EXP/drop/pickup/level-up|VERIFIED; do not repeat|run37851961862,EXP115,level2,5points;Small Axe/Vine Gloves|
|STR allocation/equip Small Shield|VERIFIED; do not repeat|run37860870710,three UI allocations STR28→31,2points;offhand1|
|Relog/persisted progress|VERIFIED; do not repeat|same run,seven assertions PASS,44 same item UUIDs retained|
|Two native client connections|VERIFIED prerequisite only|run37851961862; no membership/transfer proof|
|Party membership|VERIFIED invite/accept/member lists|run37879360808/artifact11593403578; shared EXP/leave untested|
|Trade + recipient persistence|VERIFIED normal transfer/relog;9PASS|37947724161/artifact11624674487; same itemUUID/quantity3,+100/-100Zen; cancellation/disconnect/refund remainsUNKNOWN|
|Guild,all quests/events/skills/Chaos Machine|UNKNOWN or scoped static only|See baseline-content-audit.md; no exhaustive runtime plan|

No builds were rerun. Subsequent party/finite trade CI reused validated binaries. Fixture account/character seeded, new-character UI not proven. Screenshots are genuine; see test-history.md and resource-registry.md for exact evidence. Fail a check honestly; source code/UI availability is not a PASS. Checkpoint after each new confirmed milestone and update existing model1.0 ledger.
