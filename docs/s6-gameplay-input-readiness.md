# S6 gameplay inputs and one bounded scenario — 2026-10-10 UTC

**Result:** the frozen client, patched server, newest database archive and Data/fonts release are currently listed by their official metadata endpoints with expected sizes/digests. Restoration inputs are identifiable; executable readiness and character eligibility are **not verified by a new launch**. No large packages were downloaded for this inventory. Baseline readiness stays **65.5%, model1.1, MEDIUM**.

Reviewed main checkpoint: `6fdebbddb15e584a07ff9c18262a5ae78873683b`; preceding documentation checkpoint: `e289ce9dd1f40b604cd87eb779dc69e23e72afc2`. [Mix38 closeout](s6-mix38-configured-options.md) remains closed; no source-invariant investigation is reopened.

## Historical evidence versus current availability

| Input | Historical identity/evidence | Current metadata observation | Not checked now |
|---|---|---|---|
| Native Windows client | MuMain `8d18a2bbf29b4e3c91d3f9bb3b645f68aadc3fc5`; prior native validation/gameplay | [Run 37813650810 artifacts](https://api.github.com/repos/ncuxonat7-oss/MuMain/actions/runs/37813650810/artifacts): artifact `11567737809`, `mu-client-windows-native-x64-release-editor-off-no-data-main`, 258,057,783 bytes, expired=false, expiry 2027-01-06T17:03:54Z; digest matches below | Download/extraction, executable hash and launch on a new host |
| Patched server runtime | OpenMU `d067b3c11c23c3145de6e2c76201ab9a93b267c8` plus actual-storage Money patch; successful cancel/disconnect history | [Run 37959672391 artifacts](https://api.github.com/repos/ncuxonat7-oss/MuMain/actions/runs/37959672391/artifacts): artifact `11630698202`, `patched-openmu-runtime`, 23,227,170 bytes, expired=false, expiry 2027-01-07T16:30:57Z; digest matches | New-host restore, dependency resolution, cache availability or service startup |
| Newest working database | Hanzo-corrected baseline-data-final; older gameplay-final is fallback only | [Run 38005996341 artifacts](https://api.github.com/repos/ncuxonat7-oss/MuMain/actions/runs/38005996341/artifacts): artifact `11651520969`, 2,091,291 bytes, expired=false, expiry 2026-11-08T23:46:32Z; digest matches | PostgreSQL restore and current character/skill state |
| Data/fonts | Exact prototype pack `data-4b0ab29c58b27fc4`; original tree `77f7830f542d106fc519c8821832d49a3dd8ae3a` | [Official release metadata](https://api.github.com/repos/sven-n/MuMain/releases/tags/data-4b0ab29c58b27fc4): asset `610711720`, `MuMain-data-4b0ab29c58b27fc4.tar.gz`, 457,104,401 bytes, state=uploaded, digest matches. Release is not immutable. Checksum sidecar also listed. | Transfer, unpacking and runtime resources on target host |

All three workflow-run GETs currently report completed/success at the registered heads. This reconfirms historical run status, not a new successful run. Exact-name Library metadata also resolves the existing client, patched-runtime and newest DB backup IDs/names/sizes recorded in [resource registry](resource-registry.md); archive bytes were not downloaded for this check. A Library listing does not prove future materialization will succeed. Prior verified archive/export bytes from the mix38 stage remain separate evidence.

SHA256 anchors (metadata matched to registry, not newly downloaded packages):

- Client ZIP: `eefe0a710518bc6536dd47cde45fb8605ae4ef5c7f4faca4095e8abb5f23297e`.
- Patched runtime ZIP: `090f13fec4974c5d3e155ec98e65e4834df5420b4978f1312e728976b9098f44`.
- Latest DB/evidence ZIP: `b40fbdbdb5c3bd9630331e0b9cb3bc7c1860db041a928bb976555635e03f79ea`; registered inner dump SHA256 `0a4b0744cb9be77c8f53a6f4a73e729402d17382069ba93261d394cbadf19478`.
- Data/fonts tar: `8c62a98aaabf13d80c24c0c688dbfafd4b23813966dd3a2f13c445c3a35e8d1d`.

Local read-only hashes match the expected Money patch: `85d8428452a25fef598c19ef2cda8d0ab94b2d5c13296481445ae84b7fad197d`. Reviewed overlay file [client-socket-metadata.json](../patches/client-socket-metadata.json) currently hashes to `2da3da147ebdfc09392499adfa964cce5c6b193a7ee51b8c1be6c28df064c2d8`; its before/after guards must still be applied to the exact resources during an authorized restore. No overlay execution occurred now. Client executable, restored server runtime and DB dump are not staged in this executor's workflow paths.

## Practical coverage and next decision

[Baseline coverage](baseline-content-audit.md), [test history](test-history.md) and newest [current state](current-state.md) establish the following; current-state supersedes stale historical trade/event statuses.

| Required area | Durable gameplay evidence / practical gap |
|---|---|
| Entry/save | Native login, DK world entry, progression/equipment relog proved; do not repeat standalone. |
| Classes/basic skills | DK basic attack only; ordinary learned-skill use/persistence unproved. **Selected next gap.** |
| Progression/items/craft | Basic DK level/stat/drop/equipment and scoped trade persistence proved; promotion/crafting outcomes unproved. Mix38 static stage closed. |
| BC/DS/CC | No entry/lifecycle/reward gameplay proof. Retain gap; no event task launched. |
| Stability | Finite sessions and one trade disconnect recovery proved; long-session/load/hard-crash behavior unproved. |

A learned combat skill checks an essential playing action and survival of newly acquired progress together, using one actor and one relog. This is the shortest bounded next result proposed with existing DK fixtures, **conditional on prerequisites**, not completion of all classes/S6. The exact task is ordinary **Twisting Slash, skill 41**; [client crosswalk](s6-client-crosswalk.json) confirms the name/ID only. Master variants are excluded.

**Concrete launch blocker:** existing actor eligibility, skill absence/acquisition and a supported read-only learned-skill evidence path have not been established. Resolve these from preserved evidence before spending a runtime session. Runtime permission is also still required. No new static audit or source-invariant investigation is proposed.

## One task, prepared only

**Executor/access:** WORK, one operator on the existing authorized Windows native-session workflow; no new agent. Needs Actions dispatch/artifact access, existing disposable-account access and scoped read-only state evidence. No credentials or runtime access were exercised here. Use the four frozen inputs above, current Money patch/overlay and latest saved snapshot/config, restored only into an isolated disposable copy after authorization.

1. Preflight the existing ordinary `test300Dk` against actual saved class/stats/skills; its name does not prove level or eligibility. Confirm skill 41 is absent, exact learning-item/weapon/prerequisites and inventory availability or one normal purchase. Do not infer server requirements from client Level=0. If unresolved or unmet, stop with the missing facts: no grants, grinding, imports, fixture changes or alternative scenario. Establish read-only learned-skill capture before launch.
2. After authorization, verify downloaded archive/inner binary/dump hashes, reuse binaries and restore the isolated snapshot. Capture initial skills, relevant item/Money/stats/resources. Acquire at most one learning item if needed; learn skill 41 through native UI and capture skill/item state.
3. Select skill 41 and use it once on one ordinary eligible monster. Capture native selection/effect plus authoritative resource/combat evidence distinguishing it from a basic attack. Compare with configured costs/rules while accounting for regeneration. If existing evidence cannot distinguish the action, report UNKNOWN; do not add instrumentation during the run.
4. Relog once. Confirm skill 41 in native UI and read-only learned-skill records; the consumed learning item must not reappear. Preserve narrow before/after evidence and stop the session. Do not automatically promote its DB.

**Success:** one learn/use/relog proof, correct configured consumption/cost and no unexplained changes outside expected gameplay. Animation alone is insufficient. No automatic readiness credit.

**Existing path and limits:** [standard-gameplay.yml](../.github/workflows/standard-gameplay.yml) references the same client/server/DB runs, applies the overlay, pins OpenMU and guards server DLL hashes; cache miss falls back to the saved runtime, not a rebuild. It uses Windows/.NET10/PostgreSQL17, native control batches/screenshots and a 25-minute job timeout. Its routine snapshots do not explicitly select learned-skill records, so evidence capture is a real gate, not an implemented capability. Its resource check uses the release sidecar; also require the frozen digest above at restoration. No workflow changes or dispatch occurred.

**Cost/risk:** metadata/planning LOW; future finite runtime MEDIUM, one session within the existing timeout, conditional on gates. Stop after two identical failures or before a new risky step. If new binaries, broader tooling or prerequisite modifications are required, return a concrete handoff. New-host restoration, dependencies and control-batch delivery are not proven by this metadata check. No precise credit balance is known. Trade sufficient; IT excluded; Crywolf/FPS deferred.
