# Baseline configuration

Key baseline parameters and configuration values used for the thesis runs.

---

## Baseline Parameters Table

| Parameter                | Value / Default      | Units         | Description                                      |
|-------------------------|---------------------|---------------|--------------------------------------------------|
| **Cell size**           | 40                  | m             | Side length of each grid cell                    |
| **Grid area (width)**   | 500                 | m             | Width of surveillance area (thesis baseline)     |
| **Grid area (length)**  | 500                 | m             | Length of surveillance area (thesis baseline)    |
| **Grid origin**         | (0, 0)              | m             | Bottom-left corner (depot location)              |
| **Depot to grid dist.** | 0 or 500            | m             | Distance from depot to grid edge                 |
| **Flight altitude**     | 50                  | m             | UAV cruise altitude (typical)                    |
| **Cruise speed**        | 4.0                 | m/s           | UAV cruise speed                                |
| **Endurance**           | 2100                | s             | Total battery endurance (35 min)                 |
| **Usable endurance**    | 1890                | s             | After SoC floor (31.5 min)                       |
| **SoC floor**           | 0.1                 | fraction      | Minimum battery reserve (10%)                    |
| **Revisit time (Θ)**    | 180                 | s             | Max time between cell observations (C1 proxy)    |
| **Spare floor (β)**     | 0.2                 | fraction      | Minimum fraction of fleet as spares              |
| **Cost coeff. (C_L)**   | 1.0                 | -             | Penalty for launch UAVs (dimensionless)          |
| **Cost coeff. (C_S)**   | 1.2                 | -             | Penalty for spare UAVs (dimensionless)           |
| **Scaling factor**      | 3.0                 | -             | Coverage→launch UAVs mapping                     |
| **Battery swap time**   | 60                  | s             | Hot swap time at depot                           |
| **Cell priority**       | 1.0                 | -             | Uniform for all cells in baseline                |
| **No-fly zones**        | None                | -             | Ignored in baseline                             |
| **Failures**            | Optional            | -             | Single‑UAV failure scenario available            |

---

## Explanatory Notes

- **All values are set in `configs/baseline_v2.json` or `uav_surveil/config/parameters.py` unless otherwise noted.**
- **Grid area** can be changed for scenario studies, but 400×400 m is the default.
- **Depot to grid distance** is 0 for most runs, but 500 m is used for ferry scenarios.
- **SoC floor** is enforced everywhere to ensure battery safety (C2 proxy).
- **Revisit time (Θ)** is the maximum allowed time between cell observations
  (C1 proxy).
- **Spare floor (β)** ensures operational resilience (C3 proxy).
- **Cost coefficients** are dimensionless and can be tuned for sensitivity
  analysis.
- **Failures, no-fly zones, and variable cell priorities** are not included
  in the baseline but can be added for advanced scenarios.

C1–C4 are policy monitors with STL-style intent, not formal STL robustness. 