# Lessons — do not repeat these costs

- Reuse validated client build37813650810 and cached pinned server. 423 tests already passed. A successful compile is not gameplay proof; conversely, do not recompile to reconfirm successful gameplay.
- Restore newest gameplay artifact37860870710. It contains STR31/two points/equipped shield. Restoring an older checkpoint and allocating three points again would invalidate the test.
- PostgreSQL dumps reference account/config/guild/friend roles. Create those roles before restore. Earlier run37845483038 failed with127 missing-role errors; original data was not corrupt.
- Local PG16 pg_restore cannot read PG17 dump format1.16. One targeted check established this. Solved by existing Windows PG17, database-only run37863153228. Reuse its export; don't reinstall PostgreSQL or rerun CI just to inspect definitions.
- Second native client requires complete shader directory. Missing basic_textured.vert.dxil was harness packaging, not proof of GPU incompatibility. Full existing client works; two real connections later verified.
- Short SendKeys events were lost; bounded physical key holds worked. Finite smoke run37860870710 replaced long interactive polling. Do not perfect SDL/input architecture or turn emulation into a product.
- GM positioning can attract monsters and distort combat targeting. Confirmed EXP/drop was earned by normal test0Dk, without XP/stat grants. Do not treat GM fixture inventory as normal equipment evidence: it has two pendants in slot9.
- Hanzo source/store places Gladius and Falchion at slot73. Don't suppress a failing duplicate-slot check or delete inventory items blindly. Fix only after footprint review in an isolated future scope.
- Item metadata omitted width/height means zero in pinned ItemJsonFormat.cpp, not inheritance. Requirements are formula inputs; do not compare raw client Strength70 to computed equip requirement31 as a bug.
- World aliases matter: BC→World12, CC→World19, Kalima→World25, IT→World47, DS map32→World10. Do not flag absent World33 as missing DS.
- Model mapping absence is UNKNOWN until hardcoded/shared alternatives are checked. File existence does not prove texture/action/rendering correctness. Old 200 AccessModel warnings mostly involved Object74/75 character/login scenes; don't import200 assets blindly.
- GitHub connector writes previously returned403. Owner approved signed-in browser writes; do not keep retrying failed connector mutation. Browser transport once disconnected; one recovery timed out. New sessions may need a fresh tab, not repeated environment resets.
- Some old scratch ZIPs are incomplete or older single-Main.exe bundles. Only use hash-verified validated native archive. Work scratch is disposable.
- CI artifacts expire (about90 days). Preserve exact build/db and audit inputs as authorized-user backups; put stable IDs/checksums/recovery instructions in GitHub. Never put expiring signed URLs, tokens or passwords in docs.
- Budget balance is unavailable. Warn before costly new operations, but do not claim automatic credit monitoring. Stop duplicate attempts after two similar failures and checkpoint the smallest atomic result.

- Native Command Window party/trade actions require RIGHT-click on the selected player; existing harness needed only this small operation. Do not build an input architecture.
- GM /move by name requires an online target: start second client BEFORE positioning it. First offline move returned character not found; corrected online move worked.
- Client outgoing trade minimum is level6 (NewUICommandWindow::CommandTrade). Use existing level300/400 fixtures; never alter verified level2 DK to unlock trade.
- GitHub editor modal hydration can lag a successful click. Inspect current DOM before one corrective click; do not resubmit workflow or erase content.

-15-minute live CI window was consumed by per-step artifact retrieval and GitHub commits. It completed normally, but trade-offer-06 was never consumed. Stage known UI actions as one finite plan before launching; add final-state assertions so CI success alone cannot masquerade as gameplay success. Do not replay the party stage in the trade-only continuation.

- Finite trade attempts37881728154/37882579366: actual screenshots13/14 show empty trade grids/open UI despite Zen offer100. Item-cell/timing correction did not solve placement. An earlier empty-cell diagnosis was not established; do not repeat it. Source at validated8d18a2b has ProcessMyInvenItemAutoMove and rejects confirmation with a held item. Check the exact inventory caller, then prefer direct right-click auto-move over more drag emulation. Do not repeat plans07/08. Both terminal snapshots show donor-100Zen/recipient0 under interrupted teardown; refund/persistence root cause remains open. Restore clean37879360808; preserve failures as evidence only.

- 2026-10-09 resume: exact8d18a2b caller is NewUIInventoryActionController.cpp::HandleRightClick, not NewUIMyInventory.cpp. Trade+inventory visible delegates to ProcessMyInvenItemAutoMove. AutoMoveItemAtCursor picks an empty destination, hides held item and sends move directly. Verify offered item before adding Zen; no more coordinate drag plans. Source presence is not runtime proof.

- Resolved the test-only item placement blocker in37947724161 without source/build changes: right-click760:428 invokes the pinned inventory action-controller auto-move. Both trade grids showed the item before any Zen offer. Then100Zen + native confirmations + actual recipient restart/relog produced nine persisted assertionsPASS. Use direct native quick-move; do not replay drag plans07/08. Normal trade success does NOT clear the interrupted100Zen discrepancy.


### Cancellation evidence preflight (2026-10-09)
Pinned TradeTest cancellation tests verify state and view notifications, not nonzero Zen refund with PostgreSQL relog. Source restores BackupItemStorage.Money and awaits trade close before disconnect, but source presence is not runtime proof. Cancellation needs zero-delta ownership/items/stats/money assertions; do not reuse a successful-transfer validator. Restore newest successful trade snapshot37947724161, not older pre-trade fixture or failed interrupted snapshots. The targeted validator rejected money, slot and quantity mutations locally while retaining the previous completed-trade PASS; no gameplay/build changes.


Normal cancel37954653808 isolated the earlier100Zen discrepancy without another drag experiment: item returned, money did not. Inspect wrapper versus actual persisted storage before assuming a refund assignment is effective. Pinned ItemStorageAdapter forwards Items only; Money is non-virtual on the base and independent on the wrapper. Minimal prepared patch patches/openmu-trade-money.patch makes Money virtual and forwards it to ActualStorage; adds a real-player item+Zen cancellation regression. Patch applies cleanly to pinned source, but has not compiled/run. Preserve original cache and use a separate patched key; fix validation requires one server build, no client rebuild. Strict full-item durability/current-ability equality can flag normal wear/regeneration; preserve exact offered item and permanent progress while separating these unrelated changes.


### Failed first refund patch build —37957806468
Making DataModel.ItemStorage.Money virtual caused CloneableGenerator ItemStorage_Cloneable.cs CS0266(object to int); runtime/regression were not reached. Do not repeat this approach or modify the clone generator for this bug. Revised patch resolves actual storage only at Money snapshot/cancel/teardown, leaves DataModel unchanged. Preserve successful server compilation as an artifact before later tests so failed fixtures do not force another server build. Scoped cancellation validator still fails prior37954653808 precisely for100Zen loss while tolerating equipped wear/Current Ability, preserving exact offered item/core DK.

## Confirmed refund solution / avoid wasted rebuilds

Run37959672391 succeeded: unwrap ItemStorageAdapter to actual storage for backup/refund; do not virtualize DataModel.Money or alter generated clone architecture. New narrow1-test regression and native both-client relog/14 assertionsPASS. Keep interruption/crash UNKNOWN. Canonical patch LF SHA85d8428452a25fef598c19ef2cda8d0ab94b2d5c13296481445ae84b7fad197d; Windows CRLF checkout SHA52e385decd20a06efb4d84d71fe5ea6fab9f5d620c3eb045e4c89dfba95586b0. This known newline difference is not a source mismatch/rebuild reason. Reuse compiled artifact11630698202/private backup and newest DB11630634143. Future cache misses must download this verified artifact or restore exact private backup; no automatic build or repeated successful test.
