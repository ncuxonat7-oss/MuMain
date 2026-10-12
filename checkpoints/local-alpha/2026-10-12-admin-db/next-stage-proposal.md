> Superseded as an execution queue: the [disabled admin integration](implementation-report.md) is now implemented and mock-tested. The historical proposal and Windows limits below remain evidence; follow only docs/current-state.md for the next step.

# Single next stage: integrate admin provisioning into disabled first setup

Prepared only; not executed by this checkpoint. Route: CODEX PREFERRED, localized installer change. Proposed cap: 30 active minutes, one executor, source and mock-only tests. Keep complete Entity/Typed closure and Windows readiness explicitly unproven.

## Finding from existing material

`FirstSetup.ps1` restores the baseline, then proceeds directly to grants/flags. The baseline has no admin schema/history; the successful new diagnostic supplies an official admin-only provisioning script that is not yet consumed by first setup. ExternallyProvisioned runtime mode validates existing history and cannot fill this gap. Copying the diagnostic role grants or changing a policy status is insufficient.

The setup policy is hash-pinned and not approved; `Set-MuSetupRuntimeGrants` also unconditionally throws `RUNTIME_GRANTS_UNRESOLVED`. Both fences must remain. Policy text about source-only patches describes the older packaged runtime, not the newer tested candidate. The existing C# checkpoint already explains this separation. Do not repin the package or relax guards merely to refresh wording.

## Bounded change and success criteria

Add a setup-only admin provisioning operation between restored-baseline validation and runtime grants, using a separately reviewed source/binary/SQL contract. Start from the exact saved official EF SQL and hashes; accept the BOM-free execution copy only when it equals the original after removal of exactly EF's three-byte UTF-8 BOM. Do not hand-author or regenerate migrations implicitly.

The implementation and mock tests must show:

- Independent expected identities are exactly the two admin migrations, with runtime-generated ProductVersion10.0.2 and the pinned candidate Persistence hash. A mismatch or absent reviewed contract fails before SQL execution.
- The operation belongs to setup authority only. It refuses an unexpected existing admin schema/history or a nonmatching target; it cannot run under mu_admin or grant runtime DDL/history writes.
- Only the reviewed admin SQL is accepted; no game migration, seed/account data, password generation, Startup, runtime Migrate, or flag repair is introduced.
- Execution errors stop the flow, retain sanitized failure evidence and invoke owned-process cleanup. No retry with broader grants or fallback SQL.
- Existing grant/policy fences and launchEnabled=false remain effective. Tests verify the new operation's order and its inability to enable deployment, using mocks only; no PostgreSQL start, restore or successful database-test replay.

Deliver one focused source diff, targeted mock results and contract/hash mapping. This yields an integrated but still disabled admin provisioning stage, not a runnable first deployment. Full Entity/Typed read/navigation/write closure, feature scope, package alignment and Windows acceptance stay separate unresolved blockers; do not expand into them during this stage.

## Already available, not rerun

Admin provisioning/ACL/rollback and 63/2 histories are saved in this checkpoint. The prior compiled migration metadata and 14-row observed lower-bound contract remain in the C# checkpoint. The lower bound is not a full grant allowlist; the 119-table model inventory is not authority for blanket grants. Original diagnostic flags are preserved, and the earlier proposal's automatic flag changes remain superseded.

## Later Windows route — reference only, not the next stage

Parent-supplied saved evidence identifies the manual Windows Client Build workflow `.github/workflows/windows-client.yml` at historical commit `3a9dff7a7304c5ca0ddbeaaa81e90ab6b1df32f8`. Run38108874540 reused old runtime11689365514 without a build, reported persistedState PASS, two graceful server exits and cleanup=true; its later checkpoint visually reviewed Lorencia/stat/relog screenshots. This used `windows-latest`, not proven Windows11. These results were not rerun or independently re-audited during this checkpoint. Any future acceptance must bind the NEW package binaries/config/manifest and obtain separate owner approval; an unchanged old workflow would retest old components. No new VPS or universal test platform is proposed. The single immediate next stage above is unchanged.
