# Isolated local bind Actions checkpoint

2026-10-11 00:44 UTC. Owner approved publishing reviewed patch/test files and replacing existing windows-client.yml ONLY in task/local-bind-isolated-check, then manually dispatching that branch. Main unchanged. Brand-new workflow_dispatch files require default-branch presence; reusing existing dispatch workflow avoids a main change.

Published reviewed source inputs head b317c70f11ef180786caf11c476124962680936e. Workflow first version 6c3f57410f61e1f0f5d196d7280fe1b3d1d7cbc3: one Windows job, 10-minute cap, read-only contents, no client/game/PG/Data, 12 standalone helper/socket checks. SDK 10.0.109 exists in official Microsoft metadata. No production integration proof intended.

Owner manual run https://github.com/ncuxonat7-oss/MuMain/actions/runs/38099276936 used correct branch/source at 00:41:19, ended startup_failure with jobs=[] before runner/test. Two job-level env expressions used forbidden runner.temp context. YAML/Python checks and static review missed GitHub context-availability validation. No tests/SDK execution occurred. Related push-validation failure 38098977391 is not a gameplay run.

Corrected branch commit 211dd945727554d9d93c01b317170684d6f7a2ce moves those values into initial Python step writing GITHUB_ENV. Exact remote read-back matched. Other expression locations audited against official GitHub context table. Server validation and runtime still pending.

Next: owner NEW Run workflow, branch task/local-bind-isolated-check, no inputs, from https://github.com/ncuxonat7-oss/MuMain/actions/workflows/windows-client.yml . Do not Re-run old failed run, which uses old commit. Parent did not dispatch or bypass the paused browser path. After run, inspect job and evidence logs, report 12-check results without upgrading full package readiness.
