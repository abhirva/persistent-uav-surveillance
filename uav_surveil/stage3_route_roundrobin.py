"""Stage 3A: Round-Robin Route Generator

This module implements a balanced route generation algorithm that distributes
cells evenly across routes using round-robin assignment, addressing the 
imbalanced clustering issues found in K-means approaches.

Key advantages over KMNN:
- Guaranteed balanced routes (each route gets ≈same number of cells)
- No empty or micro-routes (< 5 cells)
- More predictable performance characteristics
- Better coverage consistency across multiple laps
"""

from typing import List, Sequence, Tuple
import numpy as np
from math import hypot

from .core.cell import Cell
from .core.route import Route

__all__ = ["generate_routes_roundrobin"]


def generate_routes_roundrobin(
    cells: Sequence[Cell], 
    n_launch: int, 
    cruise_speed: float, 
    depot: Tuple[float, float] = (0.0, 0.0),
    furthest_first: bool = False
) -> Tuple[List[Route], object]:
    """Generate routes using balanced round-robin assignment.
    
    Instead of clustering (which creates imbalanced groups), this method:
    1. Sorts cells by distance from depot (nearest or furthest first)
    2. Assigns cells to routes in round-robin fashion
    3. Orders cells within each route using nearest neighbor
    
    This guarantees each route gets ⌊n_cells/n_routes⌋ or ⌊n_cells/n_routes⌋+1 cells.
    
    Args:
        cells: List of surveillance cells to cover
        n_launch: Number of routes (UAVs) to generate  
        cruise_speed: UAV speed in m/s for time calculations
        depot: (x, y) depot coordinates
        furthest_first: If True, assign furthest cells first (supervisor's enhancement)
        
    Returns:
        Tuple of (route_list, summary_dict)
    """
    
    print(f"🔄 Round-Robin: Distributing {len(cells)} cells → {n_launch} routes (balanced)")
    
    if not cells:
        return [], {"algorithm": "roundrobin", "longest_loop_time": 0.0}
    
    if n_launch <= 0:
        raise ValueError("n_launch must be positive")
    
    # Calculate target cells per route
    target_cells_per_route = len(cells) // n_launch
    remainder = len(cells) % n_launch
    
    print(f"   Target: {target_cells_per_route} cells/route (+{remainder} routes get +1 cell)")
    
    # Sort cells by distance from depot 
    depot_coord = np.array([depot[0], depot[1]])
    cell_distances = []
    for cell in cells:
        dist = hypot(cell.x - depot[0], cell.y - depot[1])
        cell_distances.append((dist, cell))
    
    if furthest_first:
        # Supervisor's enhancement: send first wave to furthest cells to reduce ferry legs
        cell_distances.sort(key=lambda x: x[0], reverse=True)
        print(f"   🎯 Furthest-First: Starting with edge cells to minimize ferry times")
    else:
        # Standard: nearest first ensures balanced near/far distribution
        cell_distances.sort(key=lambda x: x[0])
        print(f"   📍 Nearest-First: Standard distance-based distribution")
    
    # Create routes using round-robin assignment
    routes = [[] for _ in range(n_launch)]
    
    for i, (_, cell) in enumerate(cell_distances):
        route_idx = i % n_launch
        routes[route_idx].append(cell)
    
    # Convert to Route objects
    route_objects = []
    for i, cell_list in enumerate(routes):
        if not cell_list:
            # Should not happen with round-robin, but handle gracefully
            route = Route(
                id=f"rr_{i:02d}",
                cell_sequence=[],
                loop_time=0.0
            )
        else:
            # Order cells within route for efficient traversal (nearest neighbor)
            ordered_cells = _order_nearest_neighbour(cell_list, depot_coord)
            
            # Calculate route time
            route_time = _calculate_route_time(ordered_cells, cruise_speed, depot_coord)
            
            route = Route(
                id=f"rr_{i:02d}",
                cell_sequence=[cell.id for cell in ordered_cells],
                loop_time=route_time
            )
        
        route_objects.append(route)
    
    # Verify balance and report
    route_lengths = [len(r.cell_sequence) for r in route_objects]
    min_length = min(route_lengths) if route_lengths else 0
    max_length = max(route_lengths) if route_lengths else 0
    avg_length = sum(route_lengths) / len(route_lengths) if route_lengths else 0
    
    print(f"   ✅ Route balance: {min_length}-{max_length} cells/route (avg: {avg_length:.1f})")
    
    # Summary
    longest_loop = max(route.loop_time or 0 for route in route_objects) if route_objects else 0
    summary = {
        "algorithm": "roundrobin",
        "longest_loop_time": longest_loop,
        "total_routes": len(route_objects),
        "min_route_length": min_length,
        "max_route_length": max_length,
        "avg_route_length": avg_length,
        "balance_variance": np.var(route_lengths) if route_lengths else 0,
    }
    
    return route_objects, summary


def _calculate_route_time(cells: List[Cell], cruise_speed: float, depot: Tuple[float, float]) -> float:
    """Calculate time to complete the route loop."""
    if not cells:
        return 0.0
    
    total_distance = 0.0
    
    # Distance from depot to first cell
    if cells:
        total_distance += hypot(cells[0].x - depot[0], cells[0].y - depot[1])
    
    # Distance between consecutive cells
    for i in range(1, len(cells)):
        prev_cell = cells[i-1]
        curr_cell = cells[i]
        total_distance += hypot(curr_cell.x - prev_cell.x, curr_cell.y - prev_cell.y)
    
    # Distance from last cell back to depot
    if cells:
        last_cell = cells[-1]
        total_distance += hypot(depot[0] - last_cell.x, depot[1] - last_cell.y)
    
    return total_distance / cruise_speed if cruise_speed > 0 else 0.0


def _order_nearest_neighbour(cells: List[Cell], depot: Tuple[float, float]) -> List[Cell]:
    """Order cells within a route for efficient traversal using nearest neighbor heuristic."""
    if len(cells) <= 2:
        return cells
    
    ordered = []
    remaining = list(cells)  # Use list to avoid hashing issues
    
    # Start from cell closest to depot
    distances_to_depot = [hypot(cell.x - depot[0], cell.y - depot[1]) for cell in remaining]
    closest_idx = min(range(len(distances_to_depot)), key=distances_to_depot.__getitem__)
    current = remaining.pop(closest_idx)
    ordered.append(current)
    
    # Greedy nearest neighbor
    while remaining:
        distances = [hypot(current.x - cell.x, current.y - cell.y) for cell in remaining]
        nearest_idx = min(range(len(distances)), key=distances.__getitem__)
        current = remaining.pop(nearest_idx)
        ordered.append(current)
    
    return ordered 