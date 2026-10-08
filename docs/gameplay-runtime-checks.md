# Standard gameplay runtime checks

Updated 2026-10-08. This supplements `baseline-content-audit.md` with actual runtime evidence. Frozen application source/build/assets remain those in `current-state.md`; no client or server rebuild/tests repeat in this stage. Harness-only fixes restore the previous test database and send physical key presses.

| Feature | Result | Runtime evidence | Fixture / limit | Next action |
|---|---|---|---|---|
| Existing MuMain + OpenMU + PostgreSQL | GREEN | Restored run 37846640006: actual client login and map window | Ephemeral Windows CI; localhost server; exact existing binaries | Preserve final database dump |
| Normal map warp | GREEN for Lorencia ↔ Noria | Artifact 11579958340; screenshots `11-normal-warp-noria.png` Noria (171,114), `12-normal-warp-return.png` Lorencia (142,132), welcome messages | Ordinary seeded normal character test300Dk; not GM; does not validate every map | No repeat needed |
| Inventory + character UI | GREEN for display | Artifact 11578424712; `06-character-key.png` shows test1Dk level 11, XP 19000/24200, 50 unused points, seeded inventory | Display proof; not purchase/equip/XP gain | Test actual item changes |
| NPC shop / purchase | GREEN | Run 37846640006, artifact 11581801498; screenshots 24/25 plus final SQL confirm Small Shield bought for 230 Zen (10,000,000 → 9,999,770), item ID 801da101-0000-760d-a605-a410efe9185d, slot 47 | Normal test0Dk walked to Hanzo (117,140); no GM positioning succeeded | No repeat needed |
| Monster kill / XP / drop / pickup | YELLOW pending | None yet | Only positioning fixture permitted; no XP/stat grants or fabricated drops | Actual low-level combat |
| Equip item / level up / allocate stats | YELLOW pending | Purchased Small Shield requires STR 31; actual test0Dk level 1, XP 0/100, STR 28 | Existing level 300 is seeded, not a leveling result; no XP/stat grants | Naturally level, allocate three STR, equip shield |
| Re-login with saved gameplay | YELLOW pending | Database dump restored; initial account reconnect verified, but changed gameplay not yet tested | Same preserved PostgreSQL database | Reconnect after item/XP changes |
| Two real clients / party / trade / guild | YELLOW pending | Setup batch submitted | Existing seeded accounts; no server/client code changes | Actual two-client interactions after gameplay loop |

## Evidence and failed harness attempts

Run 37843108952 reached Lorencia and confirmed character/inventory UI. Final artifact 11580160294 contains the preserved PostgreSQL dump (1,366,613 bytes), ZIP SHA256 `0908bda3fcfed47f1529e292ff7579ae0f2ce3bfb806a04a176df8205647ad5d`. Short SendKeys Enter left `/move Noria` unsubmitted; no warp success was claimed. Fixed by 250 ms physical key holds.

Run 37845483038 stopped before gameplay because its fresh PostgreSQL lacked the four standard OpenMU roles referenced in the dump. Artifact 11579298825 records 127 missing-role restore errors and no other restore errors. It was canceled after failed bootstrap left PostgreSQL alive. Commit 6a4a287055abfd6d5e2491a6c3998b5a94d616b9 restores the standard roles before their original grants, stops bootstrap processes on failure, and writes child output to a file.

Run 37846640006 (https://github.com/ncuxonat7-oss/MuMain/actions/runs/37846640006) restored the original database and verified normal map transitions. Both earlier attempts remain in history and are not represented as gameplay passes. Final suite is in progress; no blanket completeness claim.

## Session 3 final checkpoint

Normal map warps and normal Hanzo shop purchase are verified. Final artifact **11581801498**, ZIP SHA256 `bbd677d82a858bf72a3fbf259a163fd482c54a34f53988c750d75e72745130f9`, preserves PostgreSQL after the purchase. Test0 position (117,140), XP 0, Zen 9,999,770, Small Shield item 801da101-0000-760d-a605-a410efe9185d in slot 47/durability 22. Test300 persisted Zen 9,996,000 after the two ordinary warps.

The attempted second client hit an actual shader-loading error: `client-two\shaders\basic_textured.vert.dxil` was absent. Artifact 11580531299 captures its native error dialog and log. GM movement failed with “Character test0Dk not found”; no two-client/GM placement success is claimed. First full client then logged into test0 and walked normally to Hanzo. Corrected continuation stages the complete existing shader folder, preserves current client process tracking/readiness failures, and restores the latest run-3 dump. No driver update, game rebuild or new asset package is needed. Remaining gameplay and social tests are still pending.
