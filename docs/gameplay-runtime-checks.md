# Standard gameplay runtime checks

Updated 2026-10-08. This supplements `baseline-content-audit.md` with actual runtime evidence. Frozen application source/build/assets remain those in `current-state.md`; no client or server rebuild/tests repeat in this stage. Harness-only fixes restore the previous test database and send physical key presses.

| Feature | Result | Runtime evidence | Fixture / limit | Next action |
|---|---|---|---|---|
| Existing MuMain + OpenMU + PostgreSQL | GREEN | Restored run 37846640006: actual client login and map window | Ephemeral Windows CI; localhost server; exact existing binaries | Preserve final database dump |
| Normal map warp | GREEN for Lorencia ↔ Noria | Artifact 11579958340; screenshots `11-normal-warp-noria.png` Noria (171,114), `12-normal-warp-return.png` Lorencia (142,132), welcome messages | Ordinary seeded normal character test300Dk; not GM; does not validate every map | No repeat needed |
| Inventory + character UI | GREEN for display | Artifact 11578424712; `06-character-key.png` shows test1Dk level 11, XP 19000/24200, 50 unused points, seeded inventory | Display proof; not purchase/equip/XP gain | Test actual item changes |
| NPC shop / purchase | YELLOW pending | None yet | Named GM fixture may place normal test0Dk near Hanzo | Buy a standard item and compare inventory/Zen |
| Monster kill / XP / drop / pickup | YELLOW pending | None yet | Only positioning fixture permitted; no XP/stat grants or fabricated drops | Actual low-level combat |
| Equip item / level up / allocate stats | YELLOW pending | None yet | Existing level 300 is seeded, not a leveling result | Use low-level test0Dk and record actual changes |
| Re-login with saved gameplay | YELLOW pending | Database dump restored; initial account reconnect verified, but changed gameplay not yet tested | Same preserved PostgreSQL database | Reconnect after item/XP changes |
| Two real clients / party / trade / guild | YELLOW pending | Setup batch submitted | Existing seeded accounts; no server/client code changes | Actual two-client interactions after gameplay loop |

## Evidence and failed harness attempts

Run 37843108952 reached Lorencia and confirmed character/inventory UI. Final artifact 11580160294 contains the preserved PostgreSQL dump (1,366,613 bytes), ZIP SHA256 `0908bda3fcfed47f1529e292ff7579ae0f2ce3bfb806a04a176df8205647ad5d`. Short SendKeys Enter left `/move Noria` unsubmitted; no warp success was claimed. Fixed by 250 ms physical key holds.

Run 37845483038 stopped before gameplay because its fresh PostgreSQL lacked the four standard OpenMU roles referenced in the dump. Artifact 11579298825 records 127 missing-role restore errors and no other restore errors. It was canceled after failed bootstrap left PostgreSQL alive. Commit 6a4a287055abfd6d5e2491a6c3998b5a94d616b9 restores the standard roles before their original grants, stops bootstrap processes on failure, and writes child output to a file.

Run 37846640006 (https://github.com/ncuxonat7-oss/MuMain/actions/runs/37846640006) restored the original database and verified normal map transitions. Both earlier attempts remain in history and are not represented as gameplay passes. Final suite is in progress; no blanket completeness claim.
