# Decisions and rationale

| Decision | Why / evidence | Revisit condition |
|---|---|---|
| Freeze exact OpenMU/MuMain/Data combination | Actual Lorencia and ordinary progression/equipment/relog work | Proven blocker requiring scoped change, not a newer-looking fork |
| Use latest saved DB, not fresh seeded demos | Preserves earned level/XP, purchase, drops and equipment | Intentional isolated fixture reset only |
| Prefer read-only exports and bulk validators | 47,417 rows checked without client/server launch or rebuild | Only use runtime when data cannot answer the question |
| Server presence != client support != runtime proof | Socket metadata gaps discovered despite server definitions | Never collapse evidence categories |
| Standard gameplay before custom systems | Owner wants usable MU, not elegant scaffolding | Owner-approved customization after readiness gate |
| Readiness model1.0 uses owner's ten weights | Comparable future acceptance milestones; existence earns zero | Proposed model/criteria change must preserve old scores and explain impact |
| Legacy63.3 is archived, not compared to new58 | Legacy14 equal S/C/A/R groups counted presence and excluded core | Never claim improvement/regression from this model migration |
| Closed prototype assets retained, no new packs | Exact runtime fit established; rights remain unresolved | Verified necessary replacement with explicit source/license and owner approval |
| Reference implementations are checklists only | Existing MuEmu/Babylon comparison already exposed event gaps | No code/resource imports without approval |
| Scoped content RED != stack dead end | Crywolf/Illusion and socket metadata gaps are localized | Stop substantive development if a fundamental core/progression/persistence dead end is demonstrated |
| CI manual and bounded, commits skip CI | Avoid useless full builds and long interactive emulation | A targeted failure or meaningful source change justifies new testing |
| Secrets and raw account backups are not source files | GitHub is canonical documentation, not a credentials vault | Keep authorized-user evidence separately; repository stores references/hashes only |

No purchases, public deployment, core refactor, resource replacement, custom gameplay or automatic production administration was performed for this checkpoint.


## 2026-10-09 — Fix cancellation on actual persisted storage

Confirmed normal cancellation lost offered Zen because ItemStorageAdapter forwarded Items only. Retain pinned OpenMU d067b3c and apply narrow Unwrap-based backup/refund patch. No DataModel/schema/resource/client change. Virtual Money candidate failed generated clone compilation CS0266; discard that approach rather than changing clone architecture. Revised run37959672391: build/1 regression/14 native relog assertionsPASS. Preserve compiled artifact+DB privately; cache miss restores verified binary, never silently rebuilds. Normal cancellation proof does not establish disconnect/concurrency/crash safety. Readiness model1.0 unchanged,60→60.5,MEDIUM; owner-defined event scope unchanged.

