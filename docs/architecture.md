# Architecture

How the Ground-Station Scheduler (GSS) and the simulation run, with each
stage's method stated in concise math/pseudocode.

## 1) System at a glance
- Mission: persistent coverage of a rectangular grid (12×12 baseline) with
  ferry legs to/from a depot.
- Fleet: active rotation UAVs + rotation spares + one contingency spare
  (reserved for failures).
- Loop: 1 Hz GSS tick drives policy, motion, coverage aging, and metrics.
- Outputs: MP4/GIF animation and per-tick CSVs under `results/`, plus
  Stage-6 plots under `figures/`.

## 2) Ground Station Scheduler (GSS)
The GSS runs at 1 Hz and maintains a validated state (`uav_surveil/gss/state.py`). The orchestrator lives in `uav_surveil/gss/simulation.py`.

### 2.1 Tick order (pseudocode)
```text
for t in range(0, mission_duration):
  # A) Failure handling (Stage 5)
  if failure_enabled: maybe_trigger_failure();
  if bridging_active and t % bridge_tick_s == 0: bridge_tick();

  # B) Route following & motions
  for each UAV:
    if state == FAILED: continue  # frozen in place (visual + logic)
    if state == SWAPPING and swap_timer.done(): state <- IDLE at depot
    move_towards_next_waypoint();
    if arrived_cell: mark_observed(cell, t)

  # C) Stage 4 policy (battery/launch)
  for each active UAV: if SoC <= theta_return(distance_to_depot): plan_RTB()
  ETA_prelaunch_if_needed(); tail_extension_guard();

  # D) Launch/RTB/swap transitions
  issue_launches(); handle_arrivals_and_swaps();

  # E) Metrics & logs
  record_coverage_and_overdue();
  if t % coverage_snapshot_period == 0: write_coverage_snapshot()
  if soc_log_enabled and t % 5 == 0: write_soc_subset()
```

Default sampling: 1 s. Coverage snapshots every 600 s (thesis runs; can be 1200 s to reduce I/O). Bridging tick 30 s by config.

## 3) Mathematical problems by stage (recap)

Headline formulations (full derivations in Chapters 3–4 of the thesis):

- **Stage 0** (battery feasibility, LP/check): slack \(\xi\) s.t.
  \(2d_{ferry}+L_{loop} \le v_{max}B(1-\sigma_{floor}-\xi)\), \(\xi\ge 0\).
- **Stage 2** (fleet sizing, convex LP surrogate): minimise
  \(c_{act}n_{act} + c_{rot}n_{rot} + c_{cont}n_{cont}\) subject to
  \(n_{act}\ge m_{req}\), \(n_{rot}\ge \beta N\), \(N\le N_{max}\).
- **Stage 4** (dispatch policy): distance-aware return threshold
  \(\theta_{return}(d) = \theta_0 + \Delta\theta(d)\); ETA pre-launch when
  expected SoC at depot \(\le \theta_{return}+\epsilon\); tail-extension
  for short segments.
- **Coverage index** (monitor): \(J_{rev}(t)=\max_{c\in\mathcal C}(t - t_{last}(c))\),
  target \(J_{rev}(t) \le \Theta = 180\,s\).

## 4) Algorithms by stage (implementation detail)

### 4.1 Stage 3A – Route generation (Round‑Robin)
Goal: balanced loops for steady coverage with minimal variance in route length.

Method:
- Build a serpentine ordering of grid cells; seed routes with “furthest‑first” (start points farthest from depot).
- Distribute cells cyclically to route buckets to balance length/turns.
- Smooth each route by local swaps limited to a small neighborhood.
- Complexity: \(O(|\mathcal C|)\) with tiny local passes; deterministic and fast.
- Rationale vs ALNS: ALNS improved little under our constraints and increased runtime; RR is simpler and robust.

### 4.2 Stage 3B – Schedule packing (staggering)
Goal: avoid depot congestion and keep loops phase‑shifted.

Method (thesis values):
- Batch size = 4 UAVs; intra‑batch stagger = 5 s; batch period = 150 s.
- Assign each route an initial phase offset; keep this phase across swaps.
- Rationale: fixed offsets produce stable phasing and low depot contention without solving a full temporal packing problem.

### 4.3 Stage 4 – Threshold policy (battery & launch)
- Distance‑aware return threshold: \(\theta_{return}(d) = \theta_0 + \Delta\theta(d)\), with \(\Delta\theta\in\{-0.05,0,+0.05\}\) for <200 m, 200–400 m, >400 m.
- ETA pre‑launch: compute expected SoC at depot for the returning UAV; if \(\le \theta_{return}+\varepsilon\) and a rotation spare is at depot, pre‑launch it so hand‑offs are smooth.
- Tail‑extension: if a spare would fly a trivially short segment, extend the assignment tail to amortize a swap/launch.

### 4.4 Stage 5 – Failure quick‑patch & contingency
States: `ON_MISSION`, `RTB`, `SWAPPING`, `IDLE`, `FAILED`. When a UAV fails:
- Freeze its state (`FAILED`) visually and logically; record `failed_id`.
- Launch the contingency UAV (reserved) to take over the failed route’s remainder.

Bridging (temporary reallocation to neighbors):
- Every `bridge_tick_s`, compute urgent set \(\mathcal Q\): failed route cells with ages near \(\Theta\) (oldest‑first).
- Candidates: active neighbors not failed.
- Guards per UAV: per‑UAV insert cap, min hold‑time hysteresis, SoC and geometry feasibility.
- Choose up to \(K\) cell–UAV insertions (nearest‑feasible detours) and insert a waypoint at the best index.
- Track `temp_assignments[failed_id]` for each neighbor to cap load.

Handover and promotion:
- When contingency completes takeover, Stage‑5 is disabled; the contingency’s `is_contingency` flag is cleared so it rejoins rotation thereafter.

### 4.5 Stage 6 – Verification & figures
- Coverage % over time (global and rolling), overdue counts, revisit percentiles (P50/P90/P99/P100), fleet state stacked area, SoC traces (contingency + neighbors), cost index (UAV‑hours × rate).
- C2/C3 monitor definitions: see README and Codebase Guide. They are policy monitors, not formal STL.

## 5) Simulation configuration & runtime
- Mission duration: historical runs 4800 s; long run sim_026 used 9600 s.
- Typical wall‑time (baseline PC): steady runs finish in minutes; failure runs can be longer due to bridging + I/O.
- Key runtime levers: coverage snapshot cadence (600→1200 s), SoC sampling (5 s), bridging tick (30 s) and caps (urgent slice, per‑UAV inserts), quiet logging.

## 6) Outputs & file naming
- `results/<tag>_metrics.csv`: 1 s metrics (coverage, counts, SoC stats, C2/C3).
- `results/<tag>_coverage_gaps_*.csv`: periodic snapshots (ages, overdue flags).
- `results/<tag>_uav_routes_*.csv`: waypoints per UAV at snapshot.
- `results/<tag>_soc_timeseries.csv`: optional SoC traces (subset in failure runs).
- `figures/<tag>_*.png`: Stage-6 plots, plus `compare_*` overlays and summary tables.

## 7) Justification summary
- Round-Robin chosen for reliability and speed; ALNS underperformed within
  our limits.
- Distance-aware RTB + ETA pre-launch reduce idle gaps and depot thrash.
- Bridging limits (K, per-UAV caps, hysteresis) bound worst-case runtime
  while restoring urgent cells.
- C2/C3 monitors provide auditable evidence of safety/availability
  without a formal STL tool.

## 8) How to run

```bash
# macOS/Linux
source .venv/bin/activate

# Windows (PowerShell)
. .venv\Scripts\Activate.ps1

# Produce animation + CSVs (reads `mission_duration` from config)
python examples/visualize_simulation.py

# Generate Stage-6 figures from existing CSVs
python -X utf8 examples/plot_stage6_figures.py --steady-tag <sim_tag> --suffix v
```
