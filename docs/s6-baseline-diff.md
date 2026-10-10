# S6 baseline diff and safe automation — 2026-10-10

**Follow-on checkpoint:** legacy binary mapping was subsequently completed in this Codex thread; all16Group0definitions match selected NPC/item/monster-count/Zen fields. See s6-legacy-quest-codex-handoff.md, updated s6-client-crosswalk.json and current-state.md. The original audit below is preserved history; its legacy-binary format limitation is superseded; native source-projection counts remain unchanged, and full quest/recipe requirements remain incomplete and readiness stays65.5.

Status: **audit complete; DRY RUN ONLY; no baseline mutation or external import**. Owner scope: Illusion Temple OUT OF SCOPE, Crywolf DEFERRED. Trade closed for this phase. Deferred client optimization is separately recorded in deferred-client-optimization.md and does not affect this audit or readiness.

## Owner result

1. **Required S6 content completeness cannot yet be assigned a trustworthy global percentage.** All 7,735 records admitted to the partial reference projection exist and their compared fields match (100%). Projection covers 84.86% of 9,115 selected current records; 1,380 records remain UNKNOWN. This is a source/configuration drift metric, not gameplay readiness or independent official S6 completeness. Spawn rows dominate the denominator, NPCs overlap monster definitions, and shop bindings overlap NPCs. Do not present 84.86% as required S6 completeness.
2. **Confirmed missing content: zero in the mapped projection.** Unknown/generated records and foreign/client-only IDs are not confirmed gaps. Source projection is incomplete for items, sets, drops and recipe semantics.
3. **Safe automatic fixes/imports admitted: zero.** The dry-run plan is empty. No new defect justifies changing the confirmed baseline.
4. Mapping work remains for 233 items, 399 set groups (not 399 ancient sets), 113 drop groups, 8 recipes, 44 monster definitions, 556 spawn rows, 7 expression-based exit gates, 16 legacy quests and 4 NPCs. These are adapter coverage gaps, not missing content. Client-only MixIDs 18/40/47 require dispatch/semantics review before any server-gap claim.
5. **New code-required gameplay gaps: none proven.** Complete handler/effect, quest/crafting requirements and event lifecycle evidence remains incomplete. Crywolf/IT findings retained outside current required baseline.
6. **New client blockers: none proven.** 282/288 skills have named metadata; six blank names require handling mapping, not automatic missing-resource classification. All 38 scoped recipe MixIDs and all Number/StartingNumber/RefuseNumber steps of 483 nonlegacy quests are present. Rendering, animations, words/reward chains and recipe ingredient/outcome equivalence are not established by these IDs.
7. **Expected readiness gain from currently admitted safe automated fixes: 0 points**, because no fix/import is admitted. Completing the existing quest/recipe IDs **and requirements** criterion could yield +2.5 points (68.0%) only after full evidence; decoding IDs alone earns zero. Do not promise 85% from data imports.
8. **Baseline Readiness: previous65.5% → current65.5%, change0, model1.1, MEDIUM, current critical RED0.** Fixed weights, owner scope and 85% customization gate preserved. Weighted automatically validated acceptance evidence remains27.5%; this is a different denominator from84.86% record projection.
9. **Exact next recommended action:** extend the reusable client/server semantic crosswalk for the 38 scoped recipes and 16 legacy quests: distinguish MixID from MixIndex, map category/NPC dispatch, ingredient item ranges/levels/options/counts, costs/rates and outcomes; decode legacy quest format with verified native layout. Compare saved baseline only, emit dry-run findings, and require owner approval for any external writes. This targets the existing +2.5 criterion without manual record-by-record gameplay. Then use only representative critical quest/crafting/event chains where static evidence is insufficient.

## Reference selection and admission

| Source / pin | Season/version; provenance | Known customizations / formats | Risk / decision |
|---|---|---|---|
| **PRIMARY: MUnique/OpenMU d067b3c11c23c3145de6e2c76201ab9a93b267c8** | Documented S6 Episode3 ENG initialization; MIT source. VersionSeasonSix with inherited Version075/Version095d and explicit installed transformations. | C# initializers, EF configuration model, plugin updates; OpenMU fractional-stat conventions and current extended client combination. | Lowest mapping risk for this exact model. Comparison only; not independent official Webzen content oracle, not proof of full gameplay. |
| Yomalex/MuEmu 6b1e8af3e90155ca6fd1d003b9dae5c978f24186 | MIT emulator source; supplied game-data/assets provenance not established as independently redistributable. Repository targets multiple/later seasons. | XML/TXT; mixed later-season IDs, RuneWizard/custom stores and duplicate event-wave rows in previously inspected sample. | High contamination/mapping risk. Secondary candidate discovery only; **DO NOT IMPORT**. Existing sample reused, no new import. |

No clean independently authoritative redistributable official S6 dataset was established. A full independent completeness percentage would require such a dataset or an owner-approved finite standard-content checklist. Do not treat foreign-only records as a known-good missing list.

## Exact inputs and preservation

Server pin unchanged plus existing Money patch. Native client pin unchanged8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5. Newest working DB remains11651520969/run38005996341. Preserved export SHA256 **8bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a**. Exact Data tree **77f7830f542d106fc519c8821832d49a3dd8ae3a**, complete13,188-path manifest, reviewed socket metadata overlay retained. No DB connection, update replay, rebuild, gameplay, trade or defect re-investigation.

Read-only extraction run **38008949221**, head289310534c6f75719ff6043961007ef2038f2f5e, SUCCESS12s, artifact **11652516455 / s6-client-binary-inputs**. Sparse checkout four files from the exact native pin; verified Git blob IDs. Data content release tag is not a source commit. **src/bin/Data at the native pin has the exact approved Data tree**, allowing small read-only table extraction instead of downloading the436MB archive. See s6-client-input-provenance.json for four file hashes/sizes/blobs.

No previous47,417-row structural/bulk checks, all81 updates,690 item dimensions,22 shop grids,423 native tests or verified gameplay/trade were rerun. Prior accepted evidence is reused.

## Semantic coverage and gap / automation matrix

Counts refer to current owner-scoped definitions/records, with variant maps and multiset spawns preserved. MATCH covers only explicit projected fields. Confirmed missing content is zero in every mapped category; unknown counts below indicate unfinished mapping. Import gain0 throughout.

| Subsystem | Current / matched / unknown | Client dependency / result | Conversion feasibility / manual mapping | Code change / risk | Classification |
|---|---|---|---|---|---|
| Maps | 66 /66 /0 | World aliases and exact terrain inventory reused; Exile object remains UNKNOWN | Native Number+Discriminator keys; terrain/variant interpretation and walkability remain | No new code defect; medium resource/variant risk | AUTO WITH MAPPING; no import candidate |
| Gates / warps | Enter67/67/0; exit155/148/7; warps39/39/0 | Map aliases, coordinates, destination and UI handling | Semantic gate geometry/targets; resolve7 MapIdentity expressions | No code defect; medium coordinate/variant risk | AUTO WITH MAPPING |
| Monsters / stats | 483 /439 /44 | Explicit dispatch/model/animation mapping required; chest541/542 dispatch+Npc/DoppelgangerBox.bmd proved | Literal stats GUIDs, delays, ObjectKind; generated builders remain | No code defect; medium/high animation/AI risk | AUTO WITH MAPPING |
| Spawns | 6077 /5521 /556 | Referenced map+monster support; rectangular bounds are not walkability | Multiset natural key map/monster/rect/quantity/direction/trigger/wave; preserve duplicates | No code defect; medium generated/event-wave risk | AUTO WITH MAPPING |
| NPCs / shops | NPC103/99/4; bindings22/22/0 | Model/interaction mapping; prior585 stock rectangles/22 grids reused | Store binding mapped; stock contents/economy not regenerated from source | No code defect; medium dispatch/economy risk | AUTO WITH MAPPING |
| Items | 690 /457 /233 | Prior all690 ID/dimension proof reused; five special models still UNKNOWN | Natural key(Group,Number); helper-generated jewelry/socket/wings etc need adapter | No code defect; medium special handling risk | AUTO WITH MAPPING |
| Equipment / sets | 435 /36 /399 | itemset BMD/options/character compatibility not fully decoded |36 ancient sets projected by stable GUID.435 includes skill-bearing groups; not435 ancient sets | No code defect; high option/probability semantics risk | MANUAL REVIEW REQUIRED |
| Drops | 119 /6 /113 | Result item support needed, not foreign bag filenames | Drop joins, filters, probabilities and context/fallback generation unresolved | No code defect; high economy risk | MANUAL REVIEW REQUIRED |
| Skills | 288 /288 /0 selected server fields |650 client slots/checksum valid;282 named,6blank UNKNOWN | Master damage replacement chain and requirement joins mapped; full class/consume/effect behavior unresolved | No proven code gap; medium/high gameplay semantics risk | AUTO WITH MAPPING |
| Quests | 499 /483 /16 |915 QuestProgress entries; all3step roles present for483quests.16legacy need separate format; words/requirements/rewards not full proof | (Group << 16) OR Step; legacy item/monster requirements and reward semantics remain | No code defect; medium/high dialog/chain risk | AUTO WITH MAPPING |
| Events | 34 /34 /0 common fields | Dedicated UI/effects/resources/lifecycle require targeted chain evidence | Type:GameLevel/timings only; installed updates proof reused | No current code gap proven; lifecycle UNKNOWN. IT/CW excluded | MANUAL REVIEW REQUIRED |
| Chaos Machine / crafting | 38 /30 /8 source;38/38clientMixIDs |99clientrecords; MixID protocol≠UI MixIndex; ingredients/rates/outcomes pending | Read-only binary structs decoded; ranges/options/categories/handler mapping next | No proven code gap; high economy/outcome risk | AUTO WITH MAPPING |
| Other standard config | No independent comprehensive denominator | Exact installed81S6update proof reused | Helper definitions/options/classes/formulas outside partial projection are UNKNOWN | No source presence credit; unknown scope requires finite checklist | MANUAL REVIEW REQUIRED |
| Foreign mixed-season data | Secondary only; no admitted missing list | Later-season client support cannot be assumed | Source/license/season/semantic admission required before adapter | High contamination risk | DO NOT IMPORT |

AUTO-FIX / AUTO-IMPORT SAFE, CODE REQUIRED and CLIENT BLOCKED have **no newly proven candidates**. The report preserves those outcomes as possible future classifications; never assign them to unresolved mappings merely to fill a table.

## Reusable tooling and dry-run contract

Scripts: s6_source.py (literal native reference projection), diff-baseline-s6.py (semantic multiset diff), decode-s6-client-tables.py (fail-closed pinned binary reader), crosscheck-s6-client-ids.py (read-only joins), test-s6-diff.py and test-s6-client-tables.py. Outputs: patches/s6-reference-projection.json, docs/s6-baseline-diff.json, docs/s6-client-crosswalk.json, patches/s6-client-table-projection.json, patches/s6-client-input-provenance.json. All are configuration metadata; no DB dumps/account inventories/secrets.

```sh
python scripts/diff-baseline-s6.py --baseline baseline-config.jsonl --reference patches/s6-reference-projection.json --client-manifest resource-manifest.json --client-evidence client-final.json --out audit-output
python scripts/decode-s6-client-tables.py --data exact-client-binary-inputs --out client-tables.json
python scripts/crosscheck-s6-client-ids.py --baseline baseline-config.jsonl --client-tables client-tables.json --out client-crosswalk.json
python scripts/test-s6-diff.py
python scripts/test-s6-client-tables.py
```

Reference → partial semantic transform → exact-ID/multiset validation → report. Never opens a DB or applies data. Every candidate mismatch/missing row gets client cross-check and safe_to_import=false; no candidate becomes admissible just because a path exists. Status vocabulary: MATCH, CURRENT EXTRA, REFERENCE EXTRA, VALUE MISMATCH, CLIENT RESOURCE MISSING, SERVER IMPLEMENTATION MISSING, FORMAT MAPPING REQUIRED, UNKNOWN. A partial projection cannot establish CURRENT EXTRA; unmapped current rows are UNKNOWN. Whole-category missing adapters are FORMAT MAPPING REQUIRED. Line numbers are explicitly EXTRACTED_CONTEXT, not claimed original C# line numbers.

Validation:14 targeted tool tests PASS (7semantic,7binary/ID). Exact skill checksum and file lengths accepted. Binary readers reject wrong approved Git blob, checksum corruption, negative mix counts, truncated records and duplicate quest keys. Deterministic saved-reference replay is verified separately. No import mode exists; safe_import_plan=[] and baseline_writes=0.

## Knowledge / false positives / failed approaches

- Source regex over all Skill initializer methods falsely counts98 unused next-season master skills. Admit only selected Initialize body/inheritance; current S6count288, not386.
- 69 master AttackDamage apparent mismatches resolve through AddMasterSkillDefinition copying replaced-skill damage. Apply replacement chains in source order. Never zero or overwrite verified master damage from raw creation arguments.
- AttributeRequirement.SkillId1 maps **Requirements**; SkillId maps **ConsumeRequirements**, verified EF mapping. Wrong join created184false mismatches.
- Doppelganger rewardchests541/542 change ObjectKind passive1→destructible7 and drops2/5 through configured AddDoppelgangerData/ConfigureRewardChests. Installed update key8E4D2B17-6A3F-4C95-9D02-B7E15A6C3F48 reused, not replayed. MuMain constants/dispatch use MODEL_DOPPELGANGER_NPC_BOX/GOLDENBOX and both AccessModel("Data\\Npc\\", "DoppelgangerBox"). Model existence is not animation/runtime proof.
- Elvenland map51 uses static readonly Number; parsing constants only falsely marks it extra. Direction Undefined0/west1..NW8; Wandering SpawnTrigger6; use pinned enums, not guesses.
- Skill BMD current layout is108bytes (50byte UTF8name),650records+4byte checksum key0x5A18. Windows fixed-width aligned structs, not Linux wchar_t. BuxConvert XOR FC/CF/AB resets per record. QuestProgress is packed DWORDkey+BYTEUI+nine int32=41bytes. Mix header14int32; struct656bytes,8sources,32rate tokens; header and each recipe decode separately.
- Skill58 Nova(Start) has an explicit AT_SKILL_NOVA_BEGIN constant but blank name; skill150 generic monster and250–253Selupan also blank. Treat all six as UNKNOWN handling, not proven client blockers. Client-only named slots are not admitted server-gap candidates.
- Nonlegacy quest packet F6:0B uses little-endian Step then Group; native WSclient.cpp forms (Group<<16)|Step. All Number/StartingNumber/RefuseNumber keys present for483currentdefinitions. Group0legacy uses different Quest_eng format; no false missing QuestProgress claim.
- 99 client mixrecords represent42uniqueMixIDs;38requiredcurrentIDs allpresent (IT37excluded).18/40/47client-only IDs are **MANUAL REVIEW**, not SERVER IMPLEMENTATION MISSING. Other plugin handlers/category behavior may supply them; no import until traced.
- GitHub blob reader attempts UTF8 decode binary BMD and fails. Generic binary blob fetch has same limitation. Git tree77f783... is not a commit, so blob URL with it404does not prove missingData. Full release436MB download and raw BMD browser download timed out; do not repeat. Sparse read-only pinned CI extraction completed12s and avoids resource replacement.
- Foreign MuEmu item encoding group*512+number is useful for candidate joins; mixed later-season IDs/custom stores/duplicate waves/provenance gaps prevent safe import. Native GUIDs and probability/option semantics cannot be copied from XML filenames.

## Readiness evidence update

The existing quest/recipe binary IDs **and requirements** criterion stays0: ID lookup is stronger now, but complete legacy quest and recipe requirement/outcome equivalence remains unresolved. No other acceptance criterion completed or verified local defect fixed in this phase. Therefore65.5→65.5,MEDIUM,0currentcriticalRED. Current absence of RED is owner-scope-aware and does not remove representative gameplay/stability unknowns. Future client optimization backlog changes no criterion, weight, gate or current priority.


## Recipe follow-on checkpoint

See s6-recipe-audit.md/json:38recipes/86variants normalized; partial cost/rate/category checks plus96boundedupgrade scenarios and13newtests. Combined-condition counterexamples require real-item eligibility proof before defect admission. Ingredients/outcomes remain mapping/UNKNOWN;source-diff7735/1380 and readiness65.5 unchanged. No newly admittedimport/fix.
