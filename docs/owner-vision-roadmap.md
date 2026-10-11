# Owner vision: MU Online product roadmap and operating principles

**Status:** Owner-approved long-term product direction, 2026-10-12. This document records strategy; it is **not** approval to execute deferred work, purchase services, publish assets, grant new access, deploy publicly, or modify production. Read alongside [product-vision.md](product-vision.md), [decisions.md](decisions.md), and [current-state.md](current-state.md).

## Non-negotiable purpose

This MU Online project is **not a disposable experiment, throwaway prototype, or merely a packaging exercise**. The owner intends to build and operate a complete, progressively customizable MU Online server, beginning with a stable local Season 6 Alpha and potentially evolving into a public game with live players and reusable proprietary tooling/modules. The existing OpenMU + MuMain + PostgreSQL baseline is the present implementation choice, not a promise to preserve any one client or season forever.

The near-term goal is the **shortest safe path to a playable local Alpha**, not exhaustive proof that every S6 feature works and not a polished commercial installer. The long-term goal must remain visible so that short-term shortcuts do not silently destroy maintainability, player data, administration, extensibility, and future upgrade possibilities.

## Product evolution (intended sequence, not authorized immediate tasks)

1. **Local Season 6 Alpha — current priority.** Reproduce a working client + server + database on the owner's Windows computer with straightforward startup/stop, login/character/world entry, progress persistence, diagnostics, preserved known-good state and a repeatable installation/update path. Distinguish file-integrity checks, builds, simulated tests, isolated runtime evidence and acceptance of the *new complete package*.
2. **Owner-led playable iteration.** The owner plays real MU, describes actual observed defects by text/screenshots/video/logs; agents localize and fix them, add targeted regression tests, and maintain an issue history. Do not spend hours proving individual mechanics without a risk-based reason. Keep automated safeguards for persistence, item duplication, transactions, migrations, security, and core economy even when no visible bug is reported.
3. **Controlled customization.** Introduce owner-selected balance, features, interfaces, events, graphics/audio, multi-window/AFK/FPS improvements, launcher/update and admin capabilities in tested, reversible increments. Preserve upgradeability and client/server/data contracts; do not overengineer a speculative future platform before a playable build.
4. **Public online Alpha with willing players.** Once owner-approved and after rights/operational/security prerequisites, publish the client and host a controlled public test. Real players can voluntarily help discover defects, usability problems and gameplay gaps; establish issue intake, reproducible reports, monitoring, backups, anti-abuse and clear expectations. Optional modest financial support/monetization requires separate legal/IP, payments, taxation and owner approval.
5. **Online Beta and operational hardening.** Validate load, player progression, persistent economy, anti-cheat/security, abuse handling, event operations, backup/restore, migrations, rollback, safe updates, incident response, communication and support.
6. **Sustainable live service and reusable product components.** Operate community/site/Discord/support, administrator/GM workflows and supervised automation. Explore newer seasons, client replacement, reusable modules, customized deployments, and possible commercialization of **work the project has rights to distribute**. This is an intended opportunity, not proof of present licensing rights, demand or profitability.

### Rights and distribution boundary

The ability to compile, play or technically customize MU does **not** grant redistribution or commercial rights to proprietary Webzen content, third-party source, client data, graphics or music. Before publishing clients, taking payments or selling builds, establish an acceptable legal/licensing and payment/tax model. Do not imply that calling a payment a 'donation' removes legal obligations. Keep provenance and permission records for assets/code.

## Dot and AI team: evolving operational roles

- **Owner:** product direction, scope, budgets, risk appetite and final approval of significant changes.
- **Dot (Дотик):** persistent coordinator/owner liaison now; intended later evolution toward supervised systems administration and AI Game Master. Summarize state, classify problems, identify inefficiencies, preserve project memory, suggest better workflows and teach the owner useful AI capabilities in plain Russian.
- **Work / investigation capability:** broad cross-system diagnosis, compatibility and runtime orchestration when justified.
- **Codex / coding capability:** localized source changes, validators, tests, reviews and PRs; can independently investigate within a focused repo task. Routing depends on *task and verified tool access*, not a rigid model-name ritual.
- **Independent strategic review (e.g. Astra):** selectively at costly architectural or product decisions, repeated blockers and conflicts of evidence; not after each routine test.

Future Dot capabilities envisioned: triage repeated player reports, detect unusual server metrics, propose bug fixes and safe events, coordinate tests/releases, surface partnership messages, and report critical incidents. **Do not assume those integrations, continuous availability, push alerts, computer control or direct task dispatch exist until demonstrated.** Sensitive administration, player-affecting actions, money, public announcements, bans and risky production changes have explicit owner approval gates.

## Decision rubric for every substantial recommendation

Assess **both horizons**, not just the next checkbox:

1. **Immediate product value:** Does this materially move the *new complete local package* toward the next playable checkpoint, or remove a proven blocker? What exact, testable artifact/result will appear?
2. **Long-term product health:** Does it preserve player data, future administration, client/season flexibility, maintainability, testability, stability, legal provenance and possible commercialization?
3. **Cost and reversibility:** What is the bounded time/agent/CI cost, smallest credible validation, risk and rollback? Is there a cheaper method already proven?
4. **Evidence:** Separate proven runtime, compiled/tested code, static analysis, mock, assertion, hypothesis and unknown. A readiness percentage is an internal metric, not total product completeness or a substitute for runnable release evidence.
5. **Role of a dependency:** Categorize the feature/issue as **required for next milestone**, **required before public release**, **future enhancement**, or **not needed**. 'Not required for local Alpha' must never silently mean 'delete forever.'

Whenever an agent recommends simplifying/removing a subsystem (e.g., admin panel), explain whether temporary disabling without losing future capability is feasible. Resist both endless preliminary audits and reckless changes that undermine future operations.

## Execution and knowledge preservation

- **GitHub is the technical source of truth.** `docs/current-state.md` identifies the actual verified next unfinished step; this document supplies *why* the project exists, not an alternative immediate task queue. Never silently overwrite a newer checkpoint, working artifacts or another agent's branch.
- Work from a proven checkpoint, one bounded objective at a time. Preserve working binaries/DB and provide safe rollback. Prefer a real owner-playable Alpha once core startup/data safety are sufficiently demonstrated, rather than pre-testing every skill/event.
- Owner approval for significant expenditure, new permissions/services, external messages/publications, dangerous edits, data migration, public releases and production actions. Within an approved bounded phase, do not micro-request approval for each safe, already-authorized action.
- Save reusable tests/tools, manifests/hashes, genuine root causes, failures, decisions, evidence limits and handoffs; distinguish **local only** from **externally persisted**.
- Agent activity and percent readiness are not outcomes. Report what changed in the user-visible product, what remains unknown, and the single next decision.
- Keep sensitive credentials/account data out of GitHub. External backups may contain encrypted archives under explicit owner-managed access; repository stores nonsecret references/hashes.

## Optional second archive

If the owner later chooses to use Google Drive, treat it as a **secondary, owner-readable, dated milestone archive** (approved owner-vision snapshots, release notes, test/decision summaries, emergency restoration instructions), not another canonical live branch of code or documents. Include repository URL, branch/commit SHA, snapshot date, and evidence links. Do not duplicate large licensed assets, private player data or secrets by default. Do not claim Drive delivery succeeded until bytes can be retrieved and verified. This section is guidance, **not** an instruction to upload or synchronize anything now.

## Owner-review requirement

When assessing Dot/Work/Codex status, distinguish:
- **Engineering quality:** Was the bounded work technically sound?
- **Milestone progress:** Did it actually bring the next playable release closer?
- **Product alignment:** Does it preserve the long-term public service and evolvable product objective?

Never treat a passing unit test, an inventory or a ZIP on its own as a complete game release. Never treat an Alpha-only deferral as a permanent cancellation of future platform capabilities. If a proposed near-term expedient has long-term cost, tell the owner in plain language **before** recommending it.
