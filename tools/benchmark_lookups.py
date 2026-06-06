import timeit

def benchmark():
    setup = """
from ev_grid_oracle.city_graph import _BY_ID, _BY_SLUG, get_station_by_id, get_station_by_slug
stations = list(_BY_ID.values())
target_slug = stations[-1].neighborhood_slug
target_id = stations[-1].station_id
"""
    baseline = """
src = next((x for x in stations if x.neighborhood_slug == target_slug), None)
dst = next((x for x in stations if x.station_id == target_id), None)
"""
    optimized = """
try:
    src = get_station_by_slug(target_slug)
except KeyError:
    src = None
try:
    dst = get_station_by_id(target_id)
except KeyError:
    dst = None
"""
    n = 100000
    t_base = timeit.timeit(baseline, setup=setup, number=n)
    t_opt = timeit.timeit(optimized, setup=setup, number=n)

    print(f"Baseline (O(N)): {t_base/n*1e6:.2f} us / loop")
    print(f"Optimized (O(1)): {t_opt/n*1e6:.2f} us / loop")
    print(f"Improvement: {t_base/t_opt:.2f}x")

if __name__ == "__main__":
    benchmark()
