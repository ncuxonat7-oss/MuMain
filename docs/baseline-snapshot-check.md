# Bulk baseline snapshot integrity check

Read-only verification of captured database records and frozen runtime packages. No game configuration changes, rebuilds or repeated GUI tests.

| Check | Result | Records | Scope |
|---|---|---:|---|
| Items unique IDs | PASS | 4602 | all captured rows |
| ItemStorage unique IDs | PASS | 118 | all captured rows |
| StatAttribute unique IDs | PASS | 1117 | all captured rows |
| AttributeDefinition unique IDs | PASS | 326 | all captured rows |
| Item storage references | PASS | 4602 | all captured items; unowned items excluded |
| Unique occupied anchor slots | FAIL | 4602 | anchor slots only; multi-cell geometry not captured |
| Nonnegative item durability | PASS | 4602 | all captured items |
| Attribute definition references | PASS | 1117 | all captured stat attributes |
| Unique attributes per owner | PASS | 1117 | all captured account/character-owned attributes |
| Captured character inventories | PASS | 5 | only characters selected by snapshot SQL |
| Main.exe SHA256 | PASS | 1 | runtime package provenance; not every asset rendering |
| Client library SHA256 | PASS | 1 | runtime package provenance; not every asset rendering |
| Approved resource archive SHA256 | PASS | 1 | runtime package provenance; not every asset rendering |
| Real-client persisted gameplay smoke | PASS | 7 | existing runtime assertions plus authentic screenshots |

## Explicitly not checked

- Maps/gates/spawn/shop/item-definition/drop/skill/quest configuration references: not exported by this snapshot; retain existing baseline audit.
- Client BMD tables, all models/textures/animations and item footprint overlap: this checker does not inspect or render them.
- Party/trade/guild/events/crafting and load: not exercised by these integrity checks.
- A PASS here is not a percentage of total MU content completion. Existing 423 tests were not rerun.

## Reuse

```sh
python3 scripts/check-baseline-snapshot.py --evidence PATH_TO_EXTRACTED_GAMEPLAY_ARTIFACT --out docs/generated-baseline-check
```

Keep genuine client screenshots and the database backup as runtime evidence. Do not substitute these static checks for feature-level runtime proof.

## Captured run and findings

Run 37860870710; artifact 11585339277. Native core smoke passed all seven persistence assertions. 13/14 bulk checks passed. Duplicate anchor slots: `00001000-00fb-0000-0000-000000000000:73` (two shop-like weapon records) and `511da101-0000-7ce5-cdf0-9a7bbb02e86e:9` (two accessory records). Context and slot semantics remain unresolved; neither store is test0Dk inventory. No data was changed. Exact IDs are preserved in evidence and the JSON report. This is a triage finding, not proof that the playable character is corrupt.
