# Results

Headline metrics from the thesis (Chapter 4, Table 4.2). All runs use the
baseline 12×12 grid (500×500 m, Δ=40 m), v=4 m/s, B=2100 s, SoC floor 10%,
depot offset 500 m, deterministic Round-Robin routing with batch-stagger
phasing, and Θ=180 s as the revisit-gap analysis bound.

| Run | Description | Avg cov. % | Peak % | Time ≥ 90% (s) | Final overdue |
|---|---|---:|---:|---:|---:|
| `sim_020` | Steady-state baseline (N=21, 4800 s) | 85.2 | 99.3 | 2282 | 11 |
| `sim_024` | Under-provisioned (N=11) | 67.6 | 85.4 | 0 | 29 |
| `sim_025` | Over-provisioned (N=31) | 88.5 | 99.3 | 3485 | 7 |
| `sim_026` | Long-run stability (N=21, 9600 s) | 84.3 | 99.3 | 2610 | 18 |
| `sim_023` | Single-UAV failure at t=1800 s | 84.9 | 99.3 | 2233 | 13 |

C2 (battery-floor) and C3 (spare-latency) monitors stay at zero across all
steady-state runs.

## Baseline vs failure (Table 4.3)

|  | Avg cov. % | Time ≥ 90% (s) | Peak % | Avg overdue | Avg deployed |
|---|---:|---:|---:|---:|---:|
| `sim_020` baseline | 85.18 | 2282 | 99.3 | 21.34 | 16.80 |
| `sim_023` failure  | 84.85 | 2233 | 99.3 | 21.82 | 16.88 |
| Δ (fail − base)    | −0.33 pp | −49 | 0.0 | +0.48 | +0.08 |

Contingency promotion plus bridging absorb a single-UAV failure without
materially changing mission-level behaviour: the 240 s rolling coverage
never falls below 90% after the event, and deployed capacity stays within
0.5% of baseline.

## Takeaways

1. **Steady cadence.** A simple, deterministic Round-Robin router with
   fixed batch-stagger phasing sustains mid-80s coverage and clean C2/C3
   monitors on the baseline geometry.
2. **Provisioning is non-linear.** Moving from 11 → 21 UAVs is a
   qualitative step (never sustaining 90 % → spending nearly half the
   mission above it); 21 → 31 mainly narrows oscillations with
   diminishing returns on the peak.
3. **No long-horizon drift.** The 9600 s repeat (`sim_026`) preserves
   the baseline envelope; no slow drift is observed.
4. **Single-failure resilience.** With one UAV lost at t=1800 s,
   contingency promotion plus capped bridging keep deployed capacity
   essentially unchanged and constrain overdue growth.

## Reproducing these numbers

Each run is fully self-contained:

| Asset | Location |
|---|---|
| Per-tick metrics CSVs | `results/sim_NNN_*.csv` |
| Final figures (8 per run) | `figures/sim_NNN_*.png` |
| Zipped per-run pack | `sim_packs/sim_NNN_*.zip` |
| Pack index | `sim_packs/index.json` |

Comparison plots across the three provisioning levels are in
`figures/compare_*`.

Configuration files for the baseline and the other four scenarios live in
`configs/`; the failure timing for `sim_023` (UAV 03 at t=1800 s) is set
on the command line when launching `examples/visualize_simulation.py`.
