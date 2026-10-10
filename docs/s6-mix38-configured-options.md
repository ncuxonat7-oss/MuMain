# Mix38 configured options — bounded stage closed, 2026-10-10

The owner closed this bounded mix38 configuration investigation. No gameplay defect or corrective change is established. Further source-invariant investigation is deferred unless a concrete gameplay risk is identified. The next direction is a small S6 gameplay milestone; this checkpoint does not authorize or start runtime work. Readiness remains **65.5%, model1.1, MEDIUM**, with no score credit.

This direction supersedes earlier mix38 next-action instructions in [current-state](current-state.md), [recipe audit](s6-recipe-audit.md) and the general priority paragraph in [work/Codex routing](work-codex-routing.md). The historical findings remain valid within their recorded limits. No coding handoff has been launched.

## Inputs and evidence

- Repository checkpoint: `6fdebbddb15e584a07ff9c18262a5ae78873683b`.
- Existing `baseline-data-final`: run `38005996341`, artifact `11651520969`; ZIP SHA256 `b40fbdbdb5c3bd9630331e0b9cb3bc7c1860db041a928bb976555635e03f79ea`.
- Existing `baseline-config.jsonl`: 23,386,759 bytes, 47,417 lines; SHA256 `8bc79da233fef2b91f703a8189423bbb573830b573b8657b4c7fd21c5467a54a`.
- [Ordered report](s6-ordered-ingredients.json): 286,829 bytes; Git blob SHA `6ba460754a3d9f5cd4e5995d2bff67e780b3812e` at the checkpoint above.
- Native pin: `8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5`; OpenMU pin: `d067b3c11c23c3145de6e2c76201ab9a93b267c8`. Source identities remain in [option provenance](../patches/s6-option-source-provenance.json) and [recipe provenance](../patches/s6-recipe-source-provenance.json).
- Complete compact extraction: [s6-mix38-configured-options.json](s6-mix38-configured-options.json), 2,555 bytes; saved JSON SHA256 `74d966e3e8d533ba4be25c804c3c98901ed7863626d1798180662381b02f8f07`. The extraction completed with exit 0; this was a read-only data extraction, not a test run. No missing references or omitted normal-rule details were reported.

Archive and export hashes were checked in the environment that successfully materialized the existing archive. Archive materialization failed in the saved executor but succeeded in the coordinator environment; the cause is unknown. Local paths are not portable between executors. Verify local byte availability before relying on a returned path; reuse the saved input rather than generating a new export. Recovery identifiers remain in [resource registry](resource-registry.md).

## Method and interpretation

Only `config` rows were used. Candidate item/level states come from the existing mix38 ordered report, intersected with each definition's `MaximumItemLevel`. Domain names in the JSON are `server_ancient`, `native_ancient`, `wing` and `server_only`; the last is the prior item/level union difference, not a new eligibility projection.

Normal capability follows `ItemDefinition` -> `ItemDefinitionItemOptionDefinition` -> `ItemOptionDefinition`, then the reverse child relation `IncreasableItemOption.ItemOptionDefinitionId`, then `ItemOptionOfLevel.IncreasableItemOptionId`. Option types resolve through `ItemOptionType`; normal means type name `Option` (before the `||` suffix). Ancient links use nonzero `ItemOfItemSet.AncientSetDiscriminator`; `BonusOptionId` resolves independently to its actual option type. Directly attached Ancient Bonus options are examined through the normal definition association, separately from set bonuses. `ItemSetGroup.OptionsId` effects are not substituted for an individual item's bonus.

For every candidate level, the extraction groups boolean capability signatures and counts item/level states. `RequiredItemLevel <= candidate level` is a numeric comparison only, not proof of generator semantics. Normal-rule profiles retain AddChance/AddsRandomly/MaximumOptionsPerItem, LevelType/Number/SubOptionType/Weight and distinct (Level, RequiredItemLevel) pairs. Profile usage counts item-option links, not unique items. Domain totals overlap and must not be added together. Range holes are not missing-content findings.

## Confirmed configuration facts

| Domain | Evidence | Limit |
|---|---|---|
| 205 server-only states | 92 lack configured normal option; 113 have it. All lack Ancient set links and directly attached Ancient Bonus Option. | Does not prove these states cannot be generated with a bonus. |
| 49 wing states | All have configured normal option; none has an Ancient set link or directly attached Ancient Bonus Option. | Item/level overlap alone does not establish option-aware overlap. |
| Native and server Ancient domains | Each has 882 states with normal capability plus an Ancient set link whose bonus type is Ancient Bonus Option. | Equal counts do not prove full recipe acceptance or allocation equivalence. |
| All candidate normal options | No level-0 row and no normal option without level rows; levels are 1..4 or 2..4, all RequiredItemLevel=0. | Configured levels do not prove actual presence or positive generated level. |
| Four normal-rule profiles | AddChance=.25, AddsRandomly=true, MaximumOptionsPerItem=1, LevelType=0, SubOptionType=0, Weight=0; Number is 0, 2 or 3. | No assumed runtime probability or native OptionType equivalence. |

There are 19 candidate item definitions without configured normal option; examples (4,7) and (4,15). The JSON retains all aggregate rows, including states without set links; no eligible-inventory claim is made. Prior 149-link/148-bonus-capable findings in [Ancient audit](s6-ancient-options.json) and ordered/container results remain intact; do not repeat their extraction or successful tests.

## Explicit UNKNOWN and deferred handoff

- Whether every permitted generation/modification path respects these configured associations; whether Ancient membership guarantees a bonus or a bonus requires membership.
- Whether every such path produces a positive normal option level; the meanings of the generation controls and PowerUpDefinition values.
- Remaining wing/accessory OptionType -> Special -> native m_iOption branches and correspondence to native option >=4.
- Reachability of overlapping ingredient states, full allocation/consumption, server equal-MinimumAmount order, runtime acceptance, outcomes and persistence.

If a concrete gameplay risk later warrants a localized allocator task, preserve native first-accepted variant order, source order and counter reset; server descending MinimumAmount and removal of all matches; no double consumption; unresolved tie order and reachability remain UNKNOWN. Synthetic examples prove model behavior only. No whole-recipe MATCH, runtime defect or readiness credit follows from capability alone. Do not implement this deferred handoff now.

## Next small gameplay proposal — not executed

The subsequent [input inventory and exact skill-41 task](s6-gameplay-input-readiness.md) records current metadata availability, execution gates and the single-scenario acceptance criteria.

Propose one ordinary Dark Knight skill milestone: learn **Twisting Slash**, use it against one eligible monster, then relog and verify learned-skill persistence. First confirm from the preserved snapshot/config that the skill is absent and its exact acquisition and character prerequisites can be met without changing baseline configuration; otherwise stop and return the missing prerequisite, without substitutes or broader testing.

Inputs: newest working baseline-data-final snapshot, validated native client/Data overlay, preserved OpenMU d067b3c runtime with the current Money patch, and the existing skill/item definitions. See [current-state inputs](current-state.md#files--artifacts-to-reuse) and [resource registry](resource-registry.md). Use an isolated copy of the saved baseline only after runtime authorization; preserve the canonical snapshot. No rebuild, import, fixture injection or prerequisite bypass is implied.

Acceptance for that future milestone: native learning evidence, server-confirmed skill use/cost/effect, and post-relog persistence for that one skill; preserve unrelated character state except expected gameplay changes. Stop on a concrete failure and capture narrow evidence. Estimated risk/cost **MEDIUM** because it needs a finite runtime session and eligible character state; documentation persistence is **LOW**. No exact credit balance is known. Trade remains sufficient; IT excluded; Crywolf and client/FPS optimization deferred.
