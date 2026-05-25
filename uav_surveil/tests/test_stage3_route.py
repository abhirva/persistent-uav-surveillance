from uav_surveil.config import load_scenario
from uav_surveil.stage1_grid import build_grid_from_config
from uav_surveil.stage3_route import generate_routes_from_config


def test_route_generation_counts():
    cfg = load_scenario("baseline")
    cells = build_grid_from_config(cfg)
    n_launch = 4

    routes, summary = generate_routes_from_config(cfg, cells, n_launch)

    assert len(routes) == n_launch
    assert summary.n_routes == n_launch
    # Check that every cell appears exactly once across all routes
    cell_ids = {c.id for c in cells}
    routed_ids = {cid for r in routes for cid in r.cell_sequence}
    assert cell_ids == routed_ids 