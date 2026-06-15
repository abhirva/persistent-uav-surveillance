# Build timeline

How the end-to-end architecture was designed and implemented from scratch,
leading to the steady-state baseline and the single-UAV failure demo.

## 0) Paper foundation
- Wrote the staged architecture and math: Stage 0–6 (Battery, Grid, Fleet, Routing/Schedule, Policy, Failure, V&V).
- Drafted STL clause intentions (C1–C4) and clarified they would be monitored as proxies in this thesis (not formal robustness tooling in‑repo).
- Baseline/scenario fixed: 500×500 m, 12×12 grid, v=6 m/s (v_max=9 m/s), B=2100 s, SoC floor 10%, depot offset 500 m, Θ=180 s for analysis.

## 1) Repo bootstrap
- Created package skeleton (`uav_surveil/`), configuration system, core models (`UAV`, `Cell`, `Route`).
- Added visualizer and metrics CSV export to validate the loop early.
- Implemented Stage‑0 feasibility check from the battery inequality.

## 2) Routing exploration (Stage‑3A)
- Greedy serpentine: functional but unbalanced loops and depot bursts.
- KMNN/K‑cluster + NN: better locality, still uneven durations and phasing.
- ALNS (time‑limited): on the uniform 500×500 baseline and moderate fleets, showed no consistent improvement over simple baselines while increasing runtime.
- Round‑Robin (final): furthest‑first seeding + light local smoothing → balanced loop lengths, predictable phasing, best coverage/runtime. Selected as steady‑state baseline.

## 3) Schedule & policy (Stage‑3B/4)
- Schedule packing: batch size 4, stagger 5 s, batch period 150 s to keep depot contention low.
- Policies: distance‑aware RTB, ETA pre‑launch, tail‑extension to eliminate wasteful short flights.

## 4) Steady‑state stabilization (sim_014–017)
- Patches: tail‑extension; claim expiry on observation; ETA pre‑launch restored; furthest‑first seeding.
- Achieved peak ≈99% and stable loops at Θ=180 s → steady‑state baseline frozen for thesis.

## 5) Failure handling (Stage‑5 quick‑patch)
- Added `FAILED` state (freeze visually + logically) and failure triggers.
- Bridging: periodic urgent‑cell insertion to nearby UAVs with caps and hysteresis.
- Contingency UAV: reserved spare for takeover; after handover the contingency is promoted back into rotation.
- Fixes across runs: first true freeze (sim_021), promotion to avoid depot‑stuck (sim_022→sim_023).

## 6) Runtime/I/O hardening
- SoC sampling reduced to 5 s and limited to contingency + bridging neighbors.
- Global throttle for repeated console warnings; capped bridging work per tick; option to reduce coverage snapshot cadence.

## 7) Verification & figures (Stage‑6)
- Built figure generator to produce: coverage vs time, violations, revisit percentiles, fleet state, SoC traces, cost index, and comparison overlays from existing CSVs.
- Clarified monitors: **C2** (battery safety policy) and **C3 a/b miss** (spare availability). Proxies, not formal STL.

## 8) Comparative studies & long‑run
- sim_020 (21 UAVs): avg 85.2%, peak 99.3%, time≥90% 2282 s.
- sim_024 (11 UAVs): under‑provisioned; avg 67.6%, time≥90% 0 s.
- sim_025 (31 UAVs): stronger compliance; avg 88.5%, time≥90% 3485 s; diminishing returns vs 21.
- sim_026 (21 UAVs, 9600 s): long‑horizon; percentiles healthy; a few chronic hotspots reveal route omissions to refine (not capacity‑limited).

## 9) Documentation consolidation
- Stage math, algorithms, GSS flow, monitors, outputs and how-to are in
  `docs/architecture.md`; canonical baseline numbers in
  `docs/baseline_config.md`; headline results in `RESULTS.md`.

---

## Definitions
- **Steady‑state scenario**: failure disabled; Round‑Robin routing + staggered schedule + Stage‑4 policies; objective is sustained high coverage with max revisit ≤ Θ=180 s for almost all cells.
- **Failure scenario**: single UAV failure at configured time/ID; FAILED UAV frozen; bridging covers urgent orphans; contingency takes over and is promoted to rotation; Stage‑5 disabled post‑handover; recovery metrics tracked.

## Earlier methods vs final choice
- Greedy/serpentine and KMNN/NN gave uneven loop durations and depot bursts.
- ALNS showed limited benefit on the uniform baseline; future gains expected with non‑uniform priorities, multi‑depot, heterogeneous fleets, time windows, wind/energy models, or multi‑failure resilience.
- Round‑Robin with furthest‑first provided the best coverage/runtime trade‑off for the thesis baseline and was adopted as default.

## Future scope (post‑thesis)
- Formal STL robustness + Monte‑Carlo validation; dynamic reallocation (Stage‑5b) and local merge optimizer; advanced ALNS/VRP in richer scenarios; hardware integration via GSS adapters.
