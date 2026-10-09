# Navigation and lightweight bug reports

Start with current-state.md, then only the relevant row below. S paths are relative to pinned MUnique/OpenMU; C paths to the pinned MuMain source. Database rows come from preserved baseline-config-evidence, not a newly initialized game.

| Issue | Server source / exported configuration | Client source/resource |
|---|---|---|
| Map/NPC/monster at X:Y | S src/Persistence/Initialization/VersionSeasonSix/Maps; inherited Version075/Maps; config.GameMapDefinition→MonsterSpawnArea→MonsterDefinition→MerchantStoreId | C src/source/World/MapInfra/MapManager.cpp; World/GameMaps; Engine/Object/ZzzCharacter.cpp; Data/WorldN,ObjectN,Monster,Npc |
| Warp/gate | S VersionSeasonSix/Gates.cs, GameMapsInitializer.cs; EnterGate→ExitGate, WarpInfo→GateId | MapManager aliases; matching terrain triplets and warp UI |
| Shop stock | S VersionSeasonSix/MerchantStores.cs, inherited Version075/MerchantStores.cs; MonsterDefinition.MerchantStoreId→data.Item.ItemStorageId | C UI/NewUI/Inventory; Data/Items group metadata/model entries |
| Item/drop/set | S VersionSeasonSix/Items, GameLogic/DefaultDropGenerator.cs; ItemDefinition(Group,Number), DropItemGroup and join tables, sets/crafting | C Data/DataHandler/ItemData, Data/GameData/ItemData; Data/Items/GroupNN_*.json and Models; Local/Eng/itemset* |
| Skill/class/stat | S Initialization/CharacterClasses, VersionSeasonSix/SkillsInitializer.cs, GameLogic/PlayerActions/Skills | C WSclient.cpp, character/skill UI; Data/Local/Eng/skill_eng.bmd, Skill, Effect |
| Quest/crafting/event | S VersionSeasonSix/Quests.cs, ChaosMixes.cs, Events; GameLogic/PlayerActions/Quests/Craftings, MiniGames | C GameLogic/Quests/QuestMng.cpp, MixMgr.cpp, event UI; Data/Local/Eng/Quest*, Local/Mix.bmd |
| Persistence/connection | S Persistence/EntityFramework, Startup, DataModel; saved latest DB and logs | C ClientLibrary/network handlers; existing manual workflows |

## On-demand index instead of a huge catalog

```sh
python scripts/query-baseline.py --export baseline-config.jsonl --map-number 7 --x 100 --y 100
python scripts/query-baseline.py --export baseline-config.jsonl --npc 251
python scripts/query-baseline.py --export baseline-config.jsonl --item 6:0
python scripts/query-baseline.py --export baseline-config.jsonl --skill 6
python scripts/query-baseline.py --export baseline-config.jsonl --search Atlans
```

This generates a compact index directly from existing definitions, omitting terrain blobs and unrelated fields. Exact coordinate lookup intersects spawn rectangles, normalized for reversed endpoints; it does not find nearest NPC automatically. Query item results include referring drop/crafting/join rows; NPC results expose MerchantStoreId. Follow IDs into existing validators/export; search source by the object's Number and initializer/map name. No database/service/CI is needed.

Client-resource check usage and input provenance are in resource-registry.md. Full Monster/NPC/skill/quest binary mapping remains an unfinished task; do not fabricate paths. Read existing affected-subsystem tests before running a targeted check. Reuse previous valid runtime evidence.

## Owner bug report

Map/name or number; coordinates; character/class/level; NPC/monster/item/skill name if known; action; expected; actual; screenshot if available; approximate time. Agent appends exact build/Data version and relevant client/server logs. Never request or paste account passwords/tokens. Owner need not know IDs, source filenames or database internals.

Recommended triage: query preserved export → inspect exact referenced source/client resource → small reproducer if uncertainty remains → smallest fix → targeted verification → GitHub checkpoint/readiness update → owner tests. Avoid rebuilding or repeating known Lorencia/warp/shop/smoke tests without contradictory evidence.


## Broad baseline strategy — 2026-10-09

Read season6-reference-feasibility.md for exact OpenMU/MuMain/Data mappings and reference-source admission. Prefer native pinned config/update comparison + semantic/client bulk validation before selective foreign XML/TXT adapter. No import performed or authorized by the feasibility request. Trade baseline closed after37996918917; no additional trade edge cases unless a later defect. Static/bulk first; runtime only critical chains, real mismatches or gaps that bulk checks cannot resolve. Current continuation is stopped after audit, not a queued importer/job.

Owner2026-10-10 resumed bulk/local fixes after audit, with IT out of scope and Crywolf deferred. baseline-scope.md is authoritative; findings for these events are non-blocking, no fix/runtime work now.


Latest bulk checkpoint: docs/bulk-baseline-validation.md; scripts/validate-baseline-semantics.py --export <actual-export> --updates patches/openmu-update-manifest.json --out <report>. Client overlay is hash-guarded via scripts/apply-client-overlay.py. Newest DB run38005996341/artifact11651520969; prefer it over older runtime dumps. Binary crosswalk is next, no trade depth or IT/Crywolf work.
