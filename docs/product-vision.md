# Product vision and owner workflow

Build a playable standard MU S6E3 baseline on the existing OpenMU + MuMain + PostgreSQL stack, then introduce controlled custom gameplay. The owner is not a programmer and currently works from a phone; low-level setup should be handled by the agent.

Current priority: preserve verified gameplay, identify actual content/client gaps, prepare local alpha testing and efficient targeted fixes. No promise of full standard-event completeness or commercial redistribution rights has been made.

Future candidates, not current implementation tasks: Auto Reset, Offline EXP, VIP/subscriptions, Battle Pass, custom events/items/monsters, launcher/updater, website/account panel, marketplace, diagnostic/admin APIs, AI administration, PvP testing/bots and several customer instances. Keep configuration/resources replaceable; do not prematurely implement these features or replace the known-working stack.

Desired workflow: owner reports a bug/change → one agent finds the smallest affected scope → diagnoses with existing evidence → applies a scoped fix → targeted validation → GitHub checkpoint → owner tests/approves. GitHub is canonical; Work is disposable.

Development path: AI/Work → GitHub → local development → staging → owner approval → production. No VPS, domain, files, license, services, deployment or purchases without explicit owner approval. Production-changing operations require approval; diagnostics and reversible development within requested scope do not require repeated permission.

Owner preferences: minimize Work/CI usage, no broad competing-server/monetization research, no repeated successful builds/tests, no input-emulation side project. Warn before substantial new work; actual remaining Work balance is not visible. Do not promise automatic credit warnings. Do not add multi-agent infrastructure.

Approved Data is for the closed technical prototype. That approval is not a commercial license. Resolve source/asset rights before distribution. See resource-registry.md.
