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
