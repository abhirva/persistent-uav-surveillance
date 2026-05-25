# UAV Surveillance Configuration System (thesis reference)

The configuration system provides centralized parameter management for the UAV surveillance system, enabling easy experimentation, scenario management, and reproducible research.

## Overview

The configuration system is built around **tunable parameters** organized into logical groups:

- **Mission Parameters**: Area size, ferry distances, mission duration
- **UAV Parameters**: Speed, field of view, platform specifications  
- **Battery Parameters**: Endurance, SoC thresholds, charging times
- **Grid Parameters**: Cell size, coverage overlap, priority zones
- **Optimization Parameters**: Algorithm limits, cost parameters, thresholds
- **STL Parameters**: Contract timing constraints, robustness thresholds
- **Simulation Parameters**: Time steps, Monte Carlo runs, random seeds

## Quick Start

### 1. Load a Predefined Scenario

```python
from uav_surveil.config import load_scenario

# Load baseline configuration (matches your thesis parameters)
config = load_scenario("baseline")
print(config.summary())

# Available scenarios: baseline, urban, rural, test, performance_test, battery_study
```

### 2. Use with Stage 0 Battery Analysis

```python
from uav_surveil.stage0_battery import optimize_battery_from_config

# Run battery optimization using configuration
l_grid = 2000.0  # Grid patrol distance from Stage 1
result = optimize_battery_from_config(config, l_grid)

print(f"Required battery reserve: {result.xi_optimal:.1%}")
print(f"Mission feasible: {result.is_feasible}")
```

### 3. Create Parameter Studies

```python
from uav_surveil.config import create_parameter_sweep

# Create SoC floor sensitivity study
soc_values = [0.10, 0.15, 0.20, 0.25]
configs = create_parameter_sweep(
    "baseline", 
    "battery.soc_floor", 
    soc_values,
    "soc_study"
)

# Run analysis for each configuration
for config in configs:
    result = optimize_battery_from_config(config, l_grid)
    print(f"SoC {config.battery.soc_floor:.1%}: ξ={result.xi_optimal:.3f}")
```

### 4. Custom Configuration Management

```python
from uav_surveil.config import ConfigManager

manager = ConfigManager()

# Load and modify configuration
config = manager.load_config("baseline")
config.mission.area_width = 750.0
config.mission.area_length = 600.0
config.battery.total_endurance = 2400.0

# Save custom configuration
saved_path = manager.save_config(filename="my_mission.json")

# Validate configuration
warnings = manager.validate_config()
if warnings:
    print("Configuration warnings:", warnings)
```

## Configuration Structure

### SystemParameters

The main configuration class containing all parameter groups:

```python
config = SystemParameters()

# Access parameter groups
config.mission.area_width = 500.0
config.mission.area_length = 500.0
config.uav.cruise_speed = 4.0
config.battery.total_endurance = 2100.0
config.grid.cell_size = 40.0
config.stl.max_revisit_gap = 180.0
```

### Parameter Extraction for Stages

Each stage can extract its required parameters:

```python
# Stage 0: Battery constraint parameters
battery_params = config.get_battery_constraint_params()
# Returns: {'d_ferry': 500.0, 'v_max': 4.0, 'endurance': 2100.0, ...}

# Stage 1: Grid generation parameters  
grid_params = config.get_grid_build_params()
# Returns: {'area_width': 500.0, 'area_length': 500.0, 'cell_size': 40.0, ...}

# Stage 2: Fleet optimization parameters
fleet_params = config.get_fleet_optimization_params()
# Returns: {'spare_floor_ratio': 0.2, 'max_budget': 1000000.0, ...}
```

## Predefined Scenarios

### Baseline
Your thesis reference configuration:
- 500m × 500m area
- 500m max ferry distance
- 4 m/s cruise speed
- 2100s battery endurance
- 10% SoC floor

### Urban
High-density urban surveillance:
- 300m × 300m area
- 25m cell size (higher resolution)
- Conservative battery management
- Tighter STL timing constraints
- Priority zones for infrastructure

### Rural
Extended rural surveillance:
- 1000m × 800m area  
- 60m cell size (coarser grid)
- Extended battery endurance
- Relaxed timing constraints
- Higher fleet budget

### Test
Fast testing configuration:
- 100m × 100m area
- 5-minute missions
- Accelerated simulation
- Minimal optimization limits

### Performance Test
Stress testing configuration:
- 2000m × 1500m area
- 30m cell size
- Tight constraints
- High fleet requirements

### Battery Study
Focus on battery constraint analysis:
- Standard area
- Conservative SoC management
- Extended reserve analysis

## Parameter Studies and Sensitivity Analysis

### Single Parameter Sweeps

```python
# Battery SoC floor study
soc_configs = create_parameter_sweep(
    "baseline", "battery.soc_floor", [0.1, 0.15, 0.2, 0.25]
)

# Grid cell size study
cell_configs = create_parameter_sweep(
    "baseline", "grid.cell_size", [25, 30, 40, 50, 60]
)

# Ferry distance study
ferry_configs = create_parameter_sweep(
    "baseline", "mission.max_ferry_distance", [300, 400, 500, 600, 700]
)
```

### Multi-Parameter Studies

```python
manager = ConfigManager()

studies = {
    "battery.soc_floor": [0.1, 0.15, 0.2],
    "grid.cell_size": [30, 40, 50],
    "mission.max_ferry_distance": [400, 500, 600]
}

all_configs = manager.create_study_configs("baseline", studies, "full_study")
# Creates 9 configurations (3×3×3) 
```

### Batch Analysis

```python
scenarios = ["baseline", "urban", "rural"]
l_grid = 1500.0

for scenario_name in scenarios:
    config = load_scenario(scenario_name)
    result = optimize_battery_from_config(config, l_grid)
    
    print(f"{scenario_name}: ξ={result.xi_optimal:.3f}, "
          f"feasible={result.is_feasible}")
```

## Configuration File Format

Configurations are saved as JSON files with full metadata:

```json
{
  "config_name": "baseline",
  "description": "Baseline configuration from thesis reference",
  "created_at": "2024-06-26T07:35:03.425014",
  "version": "1.0",
  "mission": {
    "area_width": 500.0,
    "area_length": 500.0,
    "max_ferry_distance": 500.0,
    "mission_duration": 4800.0
  },
  "uav": {
    "cruise_speed": 4.0,
    "max_speed": 6.0,
    "flight_altitude": 50.0
  },
  "battery": {
    "total_endurance": 2100.0,
    "usable_endurance": 1890.0,
    "soc_floor": 0.1
  }
}
```

## Validation and Consistency Checking

The system automatically validates:

- **Parameter ranges**: All values within realistic bounds
- **Relationships**: max_speed ≥ cruise_speed, usable_endurance ≤ total_endurance
- **Consistency**: Battery capacity vs mission requirements
- **Physical feasibility**: Grid size vs coverage time limits

```python
config = load_scenario("baseline")
warnings = config.validate_consistency()

if warnings:
    print("⚠️ Configuration Issues:")
    for warning in warnings:
        print(f"  • {warning}")
```

## Integration with Existing Code

### Stage 0 Integration

```python
from uav_surveil.stage0_battery import (
    optimize_battery_from_config,
    validate_mission_feasibility,
    get_max_grid_from_config
)

config = load_scenario("baseline")
l_grid = 2000.0

# Use config-based functions instead of raw parameters
result = optimize_battery_from_config(config, l_grid)
feasible = validate_mission_feasibility(config, l_grid)
max_grid = get_max_grid_from_config(config)
```

### Future Stage Integration

```python
# Stage 1: Grid generation (future)
from uav_surveil.stage1_grid import build_grid_from_config
grid = build_grid_from_config(config)

# Stage 2: Fleet optimization (future)  
from uav_surveil.stage2_fleet import optimize_fleet_from_config
fleet_result = optimize_fleet_from_config(config, grid)
```

## Best Practices

### 1. Version Control Configurations
Save important configurations to files and include in version control:

```bash
git add configs/baseline_v1.json
git add configs/urban_scenario_v2.json
git commit -m "Add validated mission configurations"
```

### 2. Reproducible Research
Always specify configuration versions and random seeds:

```python
config = load_scenario("baseline")
config.simulation.random_seed = 42
config.version = "thesis_v1.0"
config.save_to_file("configs/thesis_baseline_v1.json")
```

### 3. Parameter Studies Documentation
Document parameter studies with clear naming:

```python
# Good: descriptive names
soc_study_configs = create_parameter_sweep(
    "baseline", "battery.soc_floor", [0.1, 0.15, 0.2], "soc_sensitivity_study"
)

# Good: save study configurations
for i, config in enumerate(soc_study_configs):
    config.save_to_file(f"studies/soc_study_{i:02d}.json")
```

### 4. Validation Before Experiments
Always validate configurations before running experiments:

```python
config = load_scenario("custom")
warnings = config.validate_consistency()

if warnings:
    print("⚠️ Fix these issues before running:")
    for warning in warnings:
        print(f"  • {warning}")
    exit(1)

# Proceed with experiments...
```

## Examples

See `examples/config_usage_examples.py` for comprehensive usage examples demonstrating all features of the configuration system.

## Testing

Run configuration tests:

```bash
python -m pytest uav_surveil/tests/test_config.py -v
```

The test suite covers:
- Parameter validation
- Scenario loading
- Configuration consistency
- File I/O operations
- Parameter sweep generation
- Integration with existing modules 