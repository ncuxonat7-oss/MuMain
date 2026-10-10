# S6 recipe semantic audit — 2026-10-10

## Latest: mix 38 option construction and configured Ancient correspondence

Pinned native CreateItem uses CreateItemExtended, then ParseItemData and CreateItemByParameters, then SetItemAttributes. The classic 12-byte ItemSerializer is not the native entry path. ItemSerializerExtended at OpenMU d067b3c encodes Option level/type as separate nibbles and HasAncient from nonzero set discriminator, independently of Ancient Bonus presence. Native parsing preserves these fields; CMixItem::SetItem sets SET from AncientDiscriminator > 0, not AncientBonusOption. Normal option values are group-specific: weapons/staff/armor level*4, shields level*5, ordinary regeneration level*4 after SetItem conversion; special accessory/wing option types need their own branches. Never globally assume Option presence equals native OptionMin>=4. Server RequiredItemMatches tests option type presence without a level threshold.

New dry-run scripts/audit-s6-ancient-options.py joins the preserved ItemOfItemSet, IncreasableItemOption, ItemOptionType and ItemDefinition tables. All 149 nonzero discriminator links classified: 148 BONUS_CAPABLE_SET, one SET_WITHOUT_BONUS (13,28). The bonusless definition has no item/level intersection with mix38 native ancient sources; it is NOT a current recipe counterexample. Bonus capability does not prove generated option presence or level. Six NEW targeted join/mutation tests PASS; prior 16 ordered tests not repeated. Source pins/blobs in patches/s6-option-source-provenance.json. Report docs/s6-ancient-options.json. Baseline SHA remains unchanged; no runtime, imports, fixes or score credit.

Run with --baseline <preserved-export> --client-tables patches/s6-client-table-projection.json --out <report>; tests: python3 scripts/test-s6-ancient-options.py.

EXACT NEXT (WORK): join all mix38 candidate item/level domains with configured set/normal-option definitions and generation level rules; trace remaining native wing/accessory OptionType branches. Determine valid persistent item-state invariants (set membership, bonus presence, positive normal level) before handing a full allocator/option validator to CODEX. Native/server ordered overlap, outcomes, NPC path and full legacy quest requirements remain UNKNOWN. Do not re-run plain/container/ordered projections or unrelated runtime/build/trade tests. Readiness65.5%, model1.1/MEDIUM/criticalRED0 unchanged.

GitHub persistence status: this ordered+option continuation is prepared locally and archived; it has NOT been committed. GitHub main remains checkpoint4e3e6ea. Git blob API returned integration403; automatic approval review rejected the subsequent direct default-branch create as lacking explicit authorization for these new files. Do not bypass the rejection. Owner approval is required for this prepared file batch.

## Latest: seven ordered simple-recipe ingredient crosswalk

Continuation of GitHub checkpoint4e3e6eaae86df9ace1cabcd858ba46973272c2f2. Routing WORK→CODEX PREFERRED: native/server predicate investigation followed by the localized validator in this Codex thread; no second agent or duplicate session. New scripts/map-s6-ordered-ingredients.py reuses the approved export and decoded projection, without changing the prior plain/container validators. Report docs/s6-ordered-ingredients.json covers all38scoped IDs, mapping seven simple-handler multi-variant recipes and34variants; custom handlers and prior scopes remain explicitly UNKNOWN here, without undoing prior findings.

| MixIDs | Field-scoped result | Remaining uncertainty |
|---|---|---|
|3,4,22,23,49,50 (+10…+15)|Five ordered variants each, masks1/4/2/16/0. Required flags are positive predicates; each later selection region excludes prior matches. Target count1 MATCH; other jewel/Chaos item-level/count predicates MATCH. Server wildcard target includes Box of Luck(14,11), clientID7179, at levels9…14 respectively; native source range ends7167.|Configured-state difference only. Native MixOptionE separately gates equipment/known wings. Real Box acquisition at these levels, native flag construction, actual requests/outcomes and persistence UNKNOWN. No gameplay defect or corrective change admitted.|
|38 (third wings stage1)|Four wing alternatives mapped in file order; union covers server wing IDs and counts. Server wildcard ancient+Option requirement has205additional configured item/level states relative to all native source unions. Server demands positive option types Ancient Bonus Option+Option; client requires native SET mask4 plus m_iOption>=4.|Server wildcard overlaps wing domains before option eligibility; allocation stays UNKNOWN. Native SET versus Ancient Bonus Option and native option value versus server Option presence are not declared equivalent. Unbounded server amount vs client255 remains unresolved; native flag/item eligibility must be established.|

All seven item/level UNION projections differ; this is NOT seven runtime bugs. Unions deliberately ignore option/flag eligibility only for this named dimension; the complete symbolic predicates remain in the report. Current-definition MaximumItemLevel is a configuration bound, not proof an item can be acquired at every level. Numeric holes imply no missing resources. Positive server option type checks require presence, not an option-level threshold; native SetItem derives m_iOption from Special values (life regeneration multiplied by4). No equivalence inferred without actual option construction/serialization evidence.

Native CheckRecipe iterates file order, resetting per-item counts for each attempt, and stops at the first fully accepted recipe. Report upgrade selection is a single target CheckItem predicate projection only; it is NOT a full CheckRecipeSub implementation. Native source allocation follows source order; server allocation is descendingMinimumAmount and removes all found items; tied order is unproved. Overlapping predicates fail closed. No new rate scenarios or deep flag combinations were evaluated. Existing36unproven combined-flag rate counterexamples remain unchanged.

Sixteen NEW targeted tests PASS: positive-mask behavior, missing/unknown flags, order reversal, file-order retention, option min/max, level/item/durability mutation, sparse domain compaction, amount mutation, overlap/customhandler exclusions, target counts and preserving required server options without equivalence. Synthetic predicate tests establish code behavior only, not real item eligibility. Deterministic replay byte-identical; export SHA256 remains8bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a. Reused source fingerprints patches/s6-recipe-source-provenance.json; no new remote source pins. Old passing bulk/plain/container/rate/runtime tests were not replayed.

```bash
python3 scripts/map-s6-ordered-ingredients.py --baseline <preserved-export.jsonl> --client-tables patches/s6-client-table-projection.json --out <ordered-report.json>
python3 scripts/test-s6-ordered-ingredients.py
```

Readiness65.5→65.5/change0/model1.1/MEDIUM/current criticalRED0. No whole-recipe MATCH, confirmed missing content, baseline writes, imports or fixes. FullIDs-and-requirements criterion remains0; partial projections do not earn the potential+2.5. Prior potion/Fenrir static findings retained without re-investigation.

EXACT NEXT (WORK): establish option/flag correspondence for mix38 from pinned native option construction and OpenMU item serialization/configuration, then decide whether full ordered allocation can be safely modeled. Focus on Option level/value and Ancient Bonus Option versus native AncientDiscriminator; do not expand synthetic combinations or guess from source presence. Once specified, a localized allocator/option validator is CODEX PREFERRED. Custom-handler ingredient rules, all outcome equivalence, NPC wire/submenu and legacy quest full requirements remain unfinished. No corrective change before intended behavior/runtime evidence; no build/trade/IT/Crywolf/client optimization.

## Latest: capacity and container policy audit

Continuation of 3fd4d41. Routing: cross-system static investigation completed in Work context; bounded repository validator implemented by the current Codex agent. No second session or duplicate task. New scripts/audit-s6-recipe-containers.py models only four disjoint plain recipes using the guarded confirmed export and pinned decoded client projection. Ten NEW boundary/mutation tests PASS; deterministic replay byte-identical; baseline SHA256 unchanged. Prior successful tests were not repeated. Sources/pins: patches/s6-container-source-provenance.json plus prior recipe provenance.

| MixIDs | Static result | Disposition |
|---|---|---|
|15,16 Bless/Soul potions|Native and server temporary grid both8x4=32; jewels1x1 and nonstackable. IsMixSource has no aggregate CountMax check.25passes both;26..32fit and satisfy entry predicates, but client CheckRecipeSub rejects excess above25; server unbounded amount accepts ingredient totals.|Confirmed STATIC ingredient-policy difference, not runtime crafting defect. Capacity explanation rejected. MANUAL REVIEW REQUIRED before choosing intended upper bound.|
|25,26 Fenrir|Native checks durability20/10 per container and exactly one container; server checks sum20/10 without per-container durability constraint. Full containers pass both. Splitting one stack into two equal halves fits grid, passes server count/level/item predicates, fails native entry and mix predicates.|Confirmed STATIC packaging-policy difference. Normal native entry blocks fragments; modified-client behavior not tested. MANUAL REVIEW REQUIRED, no unsafe-import claim.|

Server MoveItemAction only merges stacks when both source and target are player.Inventory; no implicit merge inside temporary craft storage rescues packaging equivalence. RequiredItemMatches checks definition/level/options, not durability. Requirements consume all found items; Disappear removes the matched containers; no fractional craft allocation is assumed. Existing baseline contains no required options or overlapping domains for these four mixes. Native grouping of nonstackables includes durability; each Fenrir fragment remains ineligible regardless of grouping. This audit excludes charms and equipped item flags, custom handlers and overlapping sources.

Capacity is mix INPUT grid, not recipe Width/Height (space required in character inventory for result). Keep these separate. No instruction to cap potions or auto-merge stacks was implemented. Do not report33jewels as reachable: server ingredient predicate permits it but placement fails. Runtime remains UNKNOWN for actual requests, result counts/placement and persistence. Four recipe findings do not close overall crafting acceptance or quest requirements. Safe_import_plan=[], baseline_writes=0; readiness65.5→65.5/change0/model1.1/MEDIUM/current critical RED0. Admitted automated gain0; potential+2.5 only after the entire IDs-and-requirements criterion.

Reusable command (no service/build/export):

```bash
python3 scripts/audit-s6-recipe-containers.py --baseline <preserved-export.jsonl> --client-tables patches/s6-client-table-projection.json --out <report.json>
python3 scripts/test-s6-recipe-containers.py
```

Next: extend ingredient mapper for the seven ordered multi-variant recipes, preserving positive option predicates and first-match order; fail closed on custom handlers/overlap/unproven native flag eligibility. Do not silently convert the two static policy differences into MATCH or import/fix. Four boundary rules are now established and need no repeated investigation. Prepare focused Codex acceptance: use pinned inputs, enumerate current-definition domains, report per-variant coverage and explicit UNKNOWN for allocator/flag gaps, mutation tests for variant order and item/amount bounds. Existing outcome/custom-handler/NPC wire/quest prerequisite gaps remain; no further synthetic upgrade-flag combinations or broad runtime.

## Latest: ingredient dry-run checkpoint

Continuation of f484a8c. New `scripts/map-s6-recipe-ingredients.py` reuses the preserved export and decoded pinned crafting table. Run with `--baseline`, `--client-tables`, `--out`; result `docs/s6-recipe-ingredients.json`. No extraction, service, runtime, import or baseline write. Guards reject changed export/native/mix identity and canonical crafting contents. Original recipe projection/scenario tests were not repeated. Twelve new targeted mutation/boundary tests PASS (`scripts/test-s6-recipe-ingredients.py`).

All38scoped recipes classified;14plain single-variant recipes normalized. Ingredients only:10MATCH,2VALUE MISMATCH,2FORMAT MAPPING REQUIRED. Other24remain FORMAT MAPPING REQUIRED:16customhandlers,7ordered multi-variant recipes,1required-option recipe. Overall10MATCH/2VALUE MISMATCH/26FORMAT MAPPING REQUIRED. Never whole-recipe equivalence: UI eligibility, allocation, consumption and outcomes remain outside this comparison.

|Recipes|Finding|Disposition|
|---|---|---|
|6,14,17,27,30,31,32,33,41,46|Configured legal item/level domains and normalized amount predicates MATCH|No fix/import; preserve baseline|
|15 Potion of Bless,16 Potion of Soul|Server MaximumAmount0=unbounded; client Count1..25|MANUAL REVIEW REQUIRED: prove actual mix-grid capacity/entry constraints before admitting a gameplay defect|
|25 Fenrir1,26Fenrir2|Totals MATCH after converting one full container to20/10server units; native requires fixed durability per container|AUTO WITH MAPPING: packaging/allocation proof needed; fragmented stacks are not equivalent|
|Other24|Custom handlers, ordered variants or required options|AUTO WITH MAPPING after the missing rule is localized; no guessed match/import|

Native CMixItem::SetItem counts durability only for(14,3),(14,38),(14,39),(14,53),(14,88),(14,89),(14,90),(14,100); others count containers. Server DataModel.ItemExtensions.IsStackable uses ItemSlotId=null and definition.Durability>1. Fixed container durability is converted to total units while preserving packaging constraints; unknown/mixed unit conversions fail closed. Source fingerprints already live in patches/s6-recipe-source-provenance.json. Do not count all native consumables by durability.

Levels are intersected with each current definition's MaximumItemLevel and lowerbound0. Thus client255 vs server0 can match on configured legal states; malformed or externally introduced levels remain unproved. Range padding is not missing content/resources. Empty/overlapping domains stay unmapped because allocator order is not implemented. Unbounded server vs finite client upper amounts stay explicitly different until a capacity proof establishes reachable equivalence. Optional minimum0 is preserved.

Investigation retained: cached native Data/DataHandler/ItemData/ItemDataLoader.cpp reads binary records but does not itself establish JSON requirements.level→runtime RequireLevel. Do not repeat that loader-only search or claim BoneBlade option reachability from metadata alone. UI/NewUI/Dialogs/NewUICustomMessageBox.cpp sets seed extraction/sphere and attach/detach categories; full wire→submenu path is still unproved. These observations earn no credit.

Readiness65.5→65.5, change0, model1.1/MEDIUM/RED0. Overall required S6 completeness UNKNOWN. Ingredient normalization14/38=36.84%; boundedMATCH10/38=26.32%; neither is overall S6 completeness. No confirmed missing content/resources/implementation, safe import candidate or admitted automated readiness gain. Potential+2.5 requires the entire IDs-and-requirements criterion including quest/recipe gaps, not this partial mapper.

Next WORK action: statically prove capacity/entry constraints for15/16 and full-container/allocation behavior for25/26, then map ordered variants/options in bulk. Focused mapper extension is CODEX PREFERRED once acceptance is clear. Preserve combined-flag candidates without deeper synthetic tests. Client outcomes/custom handlers and inherited quest requirements/rewards remain unfinished. No deeper trade checks; IT excluded; Crywolf/client optimization deferred.

Read-only continuation of checkpoint8548ab2. Routing: WORK investigates native/server semantics; focused validator implementation is CODEX PREFERRED and was performed in this Codex thread. No second agent/session or duplicate implementation was launched. Frozen OpenMU d067b3c + existing runtime patch, MuMain8d18a2b, exact Data77f783 and preserved export SHA2568bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a remain unchanged.

## Prior projection milestone: result and limits

All38owner-scoped recipes and their86client variants now have a reusable semantic projection: protocol MixID, client category/order, source item ranges/known current IDs, levels, option/durability/count bounds, special flags, rate tokens, cost modes, server settings/required items/option types, result references and custom handler. IT37 omitted. Crywolf not investigated. No whole-recipe equivalence or resource-rendering proof is claimed.

|Dimension|Field-scoped MATCH|Unresolved|Meaning|
|---|---:|---:|---|
|NPC-window/category binding|38|38 wire/submenu paths still unproved|Maps distinct enums; does not compare their raw integer values|
|Base cost formula|22|16 custom handlers|Fixed/per-rate prices before tax/discounts; handlers may override settings|
|Constant success rate|14|8 inventory formulas +16custom handlers|Eligible standard ingredients, no charms; not full ingredient acceptance|
|Ingredient predicates|0|38|All projected, exact inventory matcher not yet implemented|
|Outcome equivalence|0|38|Server data projected; mix.bmd does not contain result-item tables|

No missing scoped MixID, missing client resource or missing server implementation was newly confirmed. No import or fix admitted; safe_import_plan=[], baseline_writes=0. This is a crosswalk against the pinned native configuration/client, not an independent official S6 content oracle. The prior7735/1380 source-diff totals and84.86% selected-record adapter coverage stay unchanged. Overall required S6 completeness remains UNKNOWN.

## Reusable tooling

Run from the repository with the preserved export and previously decoded projection; no service, DB, new extraction or full client download:

```bash
python3 scripts/audit-s6-recipes.py --baseline <preserved-baseline-config.jsonl> --client-tables <decoded-client-tables.json> --out <recipe-audit.json>
python3 scripts/test-s6-recipes.py
```

Canonical result: s6-recipe-audit.json. Source fingerprints: patches/s6-recipe-source-provenance.json. Exact decoded inputs remain patches/s6-client-table-projection.json (compact serialization is supported). The CLI rejects wrong baseline SHA, native pin, mix blob identity or changed canonical mix-table projection. It has no import/baseline-write mode. 13focused tests PASS: item ID stride, normal/luck/single-condition rates, first-variant selection, changed-rate/cost detection, cap behavior, fail-closed unsupported formula, custom-handler and combined-price boundaries.

## Rate scenarios and candidate mismatches

For six upgradeMixIDs3/4/22/23/49/50, test8flag masks ×2Luck states =96source-model scenarios.60MATCH;36VALUE MISMATCH, all combined-flag cases. These are semantic counterexamples with UNPROVEN reachability, not confirmed local gameplay defects. No further individual-record runtime testing performed.

Example+10, excellent+380-eligible item, noLuck: client selects first excellent recipe (50%); server applies bothExcellent-10 andGuardian-10 to60%, yielding40%. WithLuck client75% versus server65%. Ordinary and individualcondition cases match. Client first-match positive-mask behavior comes from MixMgr.cpp CheckItem/CheckRecipe, not a guessed priority. Server SimpleItemCraftingHandler sums each enabled item modifier with explicit byte casts. Source item.IsGuardian tests the definition's possible Guardian options, not an already installed380option.

Saved export permits bothExcellent andGuardian option families for definitions includingBoneBlade(0,22), GrandViperStaff(5,12), DragonKnightHelm(7,29); this narrows candidates but does not prove the exact native item metadata/flag generation and real item eligibility. Native SetItem toggles ADD380 with XOR for socket items; do not substitute logical flags directly for full item-state construction. Combined ancient/excellent/socket cases likewise need eligibility proof before a fix. No current critical RED added from these unproved scenarios.

## Rules and false positives to retain

- Item ID = group*512+number. Range gaps or absent current definitions inside a broad client range do not imply missing models or safely importable content.
- OpenMU NpcWindow is its own enum; its5=ChaosMachine is not clientMix category5=Osbourne nor wire talk value3. Native ReceiveTalk maps dialogs; trainer/Elpis/Osbourne/seed NPCs use submenu message boxes. Full submenu path verification remains separate from enum/category compatibility.
- Native rate tokens are formulas; SuccessRate is the cap. Client flags are positive requirements; recipe order is first match, not mutually exclusive masks. Do not flatten five upgrade variants into one raw rate comparison.
- Server MaximumAmount0 means unbounded; client Count/stack Durability can be different units. DataModel.ItemExtensions IsStackable = !IsWearable && definition.Durability>1; do not report20stack units versus1stack container as a defect.
- Client ZenA/C displays fixed base price;B multiplies final success rate;D looks up the item's Harmony option table. Server custom GetPrice can override simple Money. Tax/discounts were not evaluated.
- RefineStone server SuccessPercent100 is outer dispatch success; handler performs per-output50%higher/20%lower creation. Client50/20 is not a raw100-vs50 defect. RestoreItem custom Harmony price similarly cannot be compared to raw Money0.
- BC/DS handler rules are implemented in BaseEventTicketCrafting plus subclasses, not persisted SimpleSettings. NativeDSlevel0 variant displays60%, while subclass uses80% forlevel<5; this is a separate candidate needing baseline eligibility/level0 semantics, not a confirmed missing record. Crywolf commentary inDSsource adds no current task.
- Charm/chaos-charm handling, item valuation functions, order of overlapping requirements, result selection/distribution and custom overrides remain unresolved. Their source presence earns no readiness credit.

## Prior checkpoint: readiness and next step (superseded above)

Previous65.5%; current65.5%; change0; confidenceMEDIUM; current critical RED0. Full quest/recipe requirements criterion stays0. Expected gain from currently admitted fixes/imports0. Possible+2.5 applies only after the existing fullIDs-and-requirements criterion is actually satisfied; partial projections/scenario models do not qualify.

Next WORK step: verify NPC wire/submenu mapping and actual native item metadata/flag eligibility for representative combined-condition candidates; localize a correction only if confirmed. Next CODEX PREFERRED implementation: bulk ingredient predicate/stack-unit mapper for all38recipes with explicit custom-handler exclusions and named UNKNOWN outcome limits. Do not deepen synthetic combination tests; do not replay old bulk/ID/legacy decoder tests. Remaining16legacyquest full prerequisites/levels/generation/itemlevels/rewards are retained in the backlog. No broad import, baseline mutation, native build, trade test, IT/Crywolf work or client optimization.

## Historical Codex handoff (plain ingredient scope now implemented)

Status: bounded plain-ingredient scope now implemented in this Codex thread; latest section is authoritative for remaining work. No separate Codex session was launched. The original handoff is preserved below for constraints and deferred extensions.

- Goal: compare recipe ingredient predicates in bulk with stack/container units and stable semantic IDs.
- Files: audit-s6-recipes.py, test-s6-recipes.py; existing decoded client projection and preserved export; s6-recipe-audit.md/json.
- Current state/findings:38recipes/86variants projected;35simple settings and16custom handlers overlap. Client/source ordered predicates differ from server descendingMinimumAmount allocation. MaximumAmount0 is unbounded; optional sources, flags, item options and stack durability must be preserved.
- Acceptance: exact pinned inputs, deterministic dryrun/no baseline writes; field-scoped MATCH only for proven predicates; unsupported handler/overlap/stack rules remain explicit mapping/UNKNOWN; mutation of one required item/count/level/option must be detected; no missing-resource claim from range gaps; no whole-recipe or safeimport claim from partial matches.
- Tests: representative exact-item, wildcard/range, optional source, stack-unit, changedcount/level/item, overlap order and unsupported custom-handler cases. Existing13tests only rerun if affected by mapper changes; no oldbulk/runtime/native/trade tests.
- Constraints/memory: AGENTS.md,work-codex-routing.md,current-state.md,s6-recipe-audit.md,baseline-scope.md,deferred-client-optimization.md. IT excluded/Crywolf deferred. No baselinefix/import/build/clientoptimization or score from format presence.
- Tried/do not repeat: legacy binary decoder and allMixIDs already closed;raw-rate/NpcWindow/count comparisons created false positives;36pairedconditioncounterexamples need realeligibility rather than deeper synthetic tests. Failed raw/fullBMD downloads and binaryUTF8fetch remain retired;reuse approved artifacts.
