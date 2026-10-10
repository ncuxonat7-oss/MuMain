# DEFERRED CLIENT OPTIMIZATION — owner decisions, 2026-10-10

Status: **DEFERRED**, future client optimization backlog. Do not execute during the current S6 baseline diff/audit. No current blocker, acceptance criterion, priority change or Baseline Readiness penalty/credit. Illusion Temple remains OUT OF SCOPE; Crywolf remains DEFERRED. Trade baseline remains closed for this phase.

| Future task | Owner intent / acceptance constraint |
|---|---|
| Active-window FPS cap | Target around 60 FPS unless measurements establish a better value. |
| Inactive/background FPS | Roughly 15–30 FPS; active client runs normally, background clients enter a lower-load mode. Values are provisional, not hard requirements. |
| Minimized-window rendering | Reduce CPU/GPU load while preserving AFK and gameplay behavior. |
| Multi-client optimization | Several MU windows should remain comfortable during long AFK sessions without unnecessary laptop overheating. |
| CPU/GPU/temperature profiling | Measure MuMain load and identify unnecessary work before selecting optimizations. |
| Optional effects reduction | Allow expensive visual effects to be reduced or disabled for AFK / low-power use. |
| Dedicated AFK / Low Power mode | Evaluate a dedicated mode if practical; preserve normal foreground behavior. |
| Gameplay invariance | Verify that FPS/rendering changes do not alter attack speed, movement timing, skill timing, networking, synchronization or gameplay logic. Rendering cadence must not silently change simulation behavior. |
| MU Dream reference | Product/UX reference only for the desired comfortable multi-window AFK experience. Do not copy proprietary code or resources. |

## Mandatory input to the future Client Modifiability / Extensibility Audit

Explicitly evaluate whether the pinned MuMain architecture allows each optimization cleanly and estimate its difficulty. Inspect separation of rendering and gameplay clocks, frame-dependent attack/movement/skill logic, network and synchronization scheduling, window focus/minimize handling, effect toggles and multi-instance resource costs. Record code locations, coupling, feasible extension points, required changes, risks and representative validation needed to prove gameplay invariance. Do not assume a frame cap is safe before tracing timing dependencies.

The future audit should propose an evidence-based implementation order and distinguish rendering-only savings from changes that require timing/simulation separation. Profiling and implementation are **not authorized for execution in the current S6 audit**. No fixed FPS promise or readiness change follows from this backlog.

Current work resumes from docs/current-state.md: pinned S6 semantic diff, exact client cross-check, gap/automation matrix and dry-run-only tooling. No broad external import without owner approval.
