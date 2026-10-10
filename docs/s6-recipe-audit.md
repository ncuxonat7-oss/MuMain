# S6 recipe semantic audit — 2026-10-10

Read-only continuation of checkpoint8548ab2. Routing: WORK investigates native/server semantics; focused validator implementation is CODEX PREFERRED and was performed in this Codex thread. No second agent/session or duplicate implementation was launched. Frozen OpenMU d067b3c + existing runtime patch, MuMain8d18a2b, exact Data77f783 and preserved export SHA2568bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a remain unchanged.

## Result and limits

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

## Readiness and exact next step

Previous65.5%; current65.5%; change0; confidenceMEDIUM; current critical RED0. Full quest/recipe requirements criterion stays0. Expected gain from currently admitted fixes/imports0. Possible+2.5 applies only after the existing fullIDs-and-requirements criterion is actually satisfied; partial projections/scenario models do not qualify.

Next WORK step: verify NPC wire/submenu mapping and actual native item metadata/flag eligibility for representative combined-condition candidates; localize a correction only if confirmed. Next CODEX PREFERRED implementation: bulk ingredient predicate/stack-unit mapper for all38recipes with explicit custom-handler exclusions and named UNKNOWN outcome limits. Do not deepen synthetic combination tests; do not replay old bulk/ID/legacy decoder tests. Remaining16legacyquest full prerequisites/levels/generation/itemlevels/rewards are retained in the backlog. No broad import, baseline mutation, native build, trade test, IT/Crywolf work or client optimization.

## Focused Codex handoff for the next mapper

Status: handoff prepared in project memory, not delivered to a separate Codex session. Current audit tool was implemented in this Codex thread.

- Goal: compare recipe ingredient predicates in bulk with stack/container units and stable semantic IDs.
- Files: audit-s6-recipes.py, test-s6-recipes.py; existing decoded client projection and preserved export; s6-recipe-audit.md/json.
- Current state/findings:38recipes/86variants projected;35simple settings and16custom handlers overlap. Client/source ordered predicates differ from server descendingMinimumAmount allocation. MaximumAmount0 is unbounded; optional sources, flags, item options and stack durability must be preserved.
- Acceptance: exact pinned inputs, deterministic dryrun/no baseline writes; field-scoped MATCH only for proven predicates; unsupported handler/overlap/stack rules remain explicit mapping/UNKNOWN; mutation of one required item/count/level/option must be detected; no missing-resource claim from range gaps; no whole-recipe or safeimport claim from partial matches.
- Tests: representative exact-item, wildcard/range, optional source, stack-unit, changedcount/level/item, overlap order and unsupported custom-handler cases. Existing13tests only rerun if affected by mapper changes; no oldbulk/runtime/native/trade tests.
- Constraints/memory: AGENTS.md,work-codex-routing.md,current-state.md,s6-recipe-audit.md,baseline-scope.md,deferred-client-optimization.md. IT excluded/Crywolf deferred. No baselinefix/import/build/clientoptimization or score from format presence.
- Tried/do not repeat: legacy binary decoder and allMixIDs already closed;raw-rate/NpcWindow/count comparisons created false positives;36pairedconditioncounterexamples need realeligibility rather than deeper synthetic tests. Failed raw/fullBMD downloads and binaryUTF8fetch remain retired;reuse approved artifacts.
