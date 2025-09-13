# Radiological Emergency Route Optimization — A* on a Simulated Plume Grid
# Author: Asif Anwar
#
# Purpose
# -------
# Compute least-exposure evacuation routes across a 2D map under a hypothetical
# radiological release.
# • Simulate a ground-level dose-rate plume (µSv/h) as an oriented Gaussian field.
# • Optionally add obstacles (buildings/blocked cells) and hot spots.
# • Run A* to minimize integrated dose along the path (dose-rate × time).
# • Compare against the shortest-distance path to quantify risk reduction.
# • Visualize plume, obstacles, start/goal, and both routes.
#
# Notes
# -----
# - Pedagogical demo; not a CFD/atmospheric model.
# - Uses matplotlib only (no seaborn); each figure is a separate plot; no explicit colors set.
#
# You can tweak parameters in the CONFIG block below and re-run.
import math
import heapq
from typing import Tuple, List, Optional, Dict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from caas_jupyter_tools import display_dataframe_to_user

# ------------------- CONFIG -------------------
N = 70                       # grid size (N x N)
CELL_SIZE_M = 12.0           # meters per cell
SPEED_MPS = 1.25             # pedestrian speed (m/s)
ALLOW_DIAGONALS = True       # 4- or 8-connected grid
START = (6, 7)               # (row, col)
GOAL  = (62, 60)

# Plume: rotated anisotropic Gaussian (µSv/h)
PLUME_CENTER = (32.0, 30.0)  # (row, col) in grid coords
SIGMA_MAJOR = 12.0           # along rotated x' (in cells)
SIGMA_MINOR = 5.0            # along rotated y' (in cells)
WIND_DIR_DEG = 25.0          # rotation angle of major axis (deg)
PEAK_DOSE = 1500.0           # µSv/h peak at center

# Obstacles (rectangles) and hot-spots (extra Gaussians)
OBSTACLE_RECTS = [           # list of (r0, c0, r1, c1), inclusive bounds
    (18, 18, 26, 22),
    (40, 36, 50, 40),
]
HOTSPOTS = [                 # list of (row, col, sigma_cells, peak_uSv_h)
    (25, 45, 3.0, 2400.0),
]

# Heuristic lower bound for dose A* (if plume min is 0, set small >0 to stay admissible but informative)
HEUR_MIN_DOSE_RATE_EPS = 0.0

# ------------------------------------------------
def grid_coords(n: int):
    r = np.arange(n)
    c = np.arange(n)
    return np.meshgrid(r, c, indexing="ij")

def rotate(x, y, theta_deg: float):
    t = np.deg2rad(theta_deg)
    xr = x*np.cos(t) - y*np.sin(t)
    yr = x*np.sin(t) + y*np.cos(t)
    return xr, yr

def gaussian_plume(n: int,
                   center: Tuple[float, float],
                   sigma_major: float,
                   sigma_minor: float,
                   angle_deg: float,
                   peak: float) -> np.ndarray:
    R, C = grid_coords(n)
    x = C - center[1]
    y = R - center[0]
    xr, yr = rotate(x, y, angle_deg)
    z = np.exp(-0.5*((xr/sigma_major)**2 + (yr/sigma_minor)**2))
    return peak * z

def add_hotspots(field: np.ndarray, spots: List[Tuple[float, float, float, float]]):
    if not spots:
        return field
    R, C = grid_coords(field.shape[0])
    acc = field.copy()
    for (rr, cc, sigma, peak) in spots:
        x = C - cc
        y = R - rr
        z = np.exp(-0.5*((x/sigma)**2 + (y/sigma)**2))
        acc += peak * z
    return acc

def obstacle_mask(n: int, rects: List[Tuple[int, int, int, int]]) -> np.ndarray:
    mask = np.zeros((n, n), dtype=bool)
    for (r0, c0, r1, c1) in rects:
        r0, c0 = max(0, r0), max(0, c0)
        r1, c1 = min(n-1, r1), min(n-1, c1)
        mask[r0:r1+1, c0:c1+1] = True
    return mask

# Movement model
if ALLOW_DIAGONALS:
    NEIGH = [(-1, 0), (1, 0), (0, -1), (0, 1),
             (-1, -1), (-1, 1), (1, -1), (1, 1)]
    STEP_METERS = [CELL_SIZE_M, CELL_SIZE_M, CELL_SIZE_M, CELL_SIZE_M,
                   CELL_SIZE_M*math.sqrt(2), CELL_SIZE_M*math.sqrt(2),
                   CELL_SIZE_M*math.sqrt(2), CELL_SIZE_M*math.sqrt(2)]
else:
    NEIGH = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    STEP_METERS = [CELL_SIZE_M]*4

def in_bounds(r: int, c: int, n: int) -> bool:
    return 0 <= r < n and 0 <= c < n

def reconstruct_path(came_from: Dict[Tuple[int,int], Tuple[int,int]],
                     current: Tuple[int,int]) -> List[Tuple[int,int]]:
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path

def astar_path(n: int,
               start: Tuple[int,int],
               goal: Tuple[int,int],
               passable: np.ndarray,
               dose_rate_uSv_h: np.ndarray,
               metric: str = "dose") -> Tuple[Optional[List[Tuple[int,int]]], float, float]:
    """
    A* on a grid.
    metric: "dose" minimizes integrated dose (µSv), "distance" minimizes meters.
    Returns: (path, total_time_hours, total_dose_uSv).  If no path, path=None.
    """
    # straight-line distance heuristic (meters)
    def h_dist(a, b):
        dr = (a[0] - b[0]) * CELL_SIZE_M
        dc = (a[1] - b[1]) * CELL_SIZE_M
        return math.hypot(dr, dc)

    # admissible lower bound on remaining dose = min_dose_rate * (straight-line time)
    min_dose_rate = float(np.min(dose_rate_uSv_h[~passable == False])) if np.any(~(passable == False)) else 0.0
    if min_dose_rate <= 0.0:
        min_dose_rate = HEUR_MIN_DOSE_RATE_EPS

    def h_dose(a, b):
        dist_m = h_dist(a, b)
        time_h = (dist_m / SPEED_MPS) / 3600.0
        return min_dose_rate * time_h

    start_r, start_c = start
    goal_r, goal_c = goal
    if not in_bounds(*start, n) or not in_bounds(*goal, n):
        return None, float("inf"), float("inf")
    if passable[start_r, start_c] or passable[goal_r, goal_c]:
        # True = blocked in our mask; if either blocked, can't start/finish
        return None, float("inf"), float("inf")

    g_cost = {start: 0.0}
    came_from: Dict[Tuple[int,int], Tuple[int,int]] = {}
    f_cost = {}
    if metric == "dose":
        f_cost[start] = h_dose(start, goal)
    else:
        f_cost[start] = h_dist(start, goal)

    open_heap = [(f_cost[start], start)]
    visited = set()

    while open_heap:
        _, current = heapq.heappop(open_heap)
        if current in visited:
            continue
        visited.add(current)

        if current == goal:
            # Reconstruct and compute totals
            path = reconstruct_path(came_from, current)
            total_time_h, total_dose = path_totals(path, dose_rate_uSv_h)
            return path, total_time_h, total_dose

        cr, cc = current
        for k, (dr, dc) in enumerate(NEIGH):
            nr, nc = cr + dr, cc + dc
            if not in_bounds(nr, nc, n):
                continue
            if passable[nr, nc]:
                continue  # blocked
            step_m = STEP_METERS[k]
            step_time_h = (step_m / SPEED_MPS) / 3600.0
            edge_dose = 0.5*(dose_rate_uSv_h[cr, cc] + dose_rate_uSv_h[nr, nc]) * step_time_h

            if metric == "dose":
                step_cost = edge_dose
            else:  # distance
                step_cost = step_m

            tentative = g_cost[current] + step_cost
            neigh = (nr, nc)
            if tentative < g_cost.get(neigh, float("inf")):
                came_from[neigh] = current
                g_cost[neigh] = tentative
                if metric == "dose":
                    f = tentative + h_dose(neigh, goal)
                else:
                    f = tentative + h_dist(neigh, goal)
                f_cost[neigh] = f
                heapq.heappush(open_heap, (f, neigh))

    return None, float("inf"), float("inf")

def path_totals(path: List[Tuple[int,int]], dose_rate_uSv_h: np.ndarray) -> Tuple[float, float]:
    """Compute travel time (h) and integrated dose (µSv) along a path."""
    if path is None or len(path) < 2:
        return float("inf"), float("inf")
    total_time_h = 0.0
    total_dose = 0.0
    for (r0, c0), (r1, c1) in zip(path[:-1], path[1:]):
        dr = abs(r1 - r0)
        dc = abs(c1 - c0)
        dist_m = CELL_SIZE_M * (math.sqrt(2) if dr == 1 and dc == 1 else 1.0)
        step_time_h = (dist_m / SPEED_MPS) / 3600.0
        edge_dose = 0.5*(dose_rate_uSv_h[r0, c0] + dose_rate_uSv_h[r1, c1]) * step_time_h
        total_time_h += step_time_h
        total_dose += edge_dose
    return total_time_h, total_dose

# ---------- Build scene ----------
dose = gaussian_plume(N, PLUME_CENTER, SIGMA_MAJOR, SIGMA_MINOR, WIND_DIR_DEG, PEAK_DOSE)
dose = add_hotspots(dose, HOTSPOTS)
blocks = obstacle_mask(N, OBSTACLE_RECTS)

# Ensure start/goal are not blocked
blocks[START] = False
blocks[GOAL] = False

# ---------- Routes ----------
path_dose, time_dose_h, dose_uSv = astar_path(N, START, GOAL, blocks, dose, metric="dose")
path_dist, time_dist_h, dose_dist_uSv = astar_path(N, START, GOAL, blocks, dose, metric="distance")

# ---------- Plotting ----------
# Figure 1: Plume + routes + obstacles
plt.figure()
plt.title("Dose-rate field (µSv/h), obstacles, and routes")
plt.imshow(dose, origin="lower", interpolation="nearest")
# obstacles overlay (semi-opaque)
obst = np.where(blocks, 1.0, np.nan)
plt.imshow(obst, origin="lower", interpolation="nearest", alpha=0.25)
# plot routes
def plot_path(p):
    if p and len(p) > 1:
        ys, xs = zip(*p)
        plt.plot(xs, ys)
if path_dist: plot_path(path_dist)
if path_dose: plot_path(path_dose)
# start/goal
plt.scatter([START[1]], [START[0]])
plt.scatter([GOAL[1]], [GOAL[0]])
plt.xlabel("Column")
plt.ylabel("Row")
plt.tight_layout()
plt.show()

# Figure 2: Binary passability map (for clarity)
plt.figure()
plt.title("Passability (0=free, 1=blocked)")
plt.imshow(blocks.astype(int), origin="lower", interpolation="nearest")
plt.xlabel("Column")
plt.ylabel("Row")
plt.tight_layout()
plt.show()

# ---------- Summary table ----------
summary = pd.DataFrame([
    {"Route": "Shortest distance (A*)",
     "Travel time (min)": time_dist_h*60.0,
     "Dose (µSv)": dose_dist_uSv,
     "Steps": (len(path_dist)-1) if path_dist else None},
    {"Route": "Least exposure (A*)",
     "Travel time (min)": time_dose_h*60.0,
     "Dose (µSv)": dose_uSv,
     "Steps": (len(path_dose)-1) if path_dose else None},
]).round({"Travel time (min)": 2, "Dose (µSv)": 1})
display_dataframe_to_user("Route comparison (distance vs. exposure)", summary)


if __name__ == "__main__":
    main()
'''
with open(script_path, "w", encoding="utf-8") as f:
    f.write(f.write(template.substitute(
        N=N,
        CELL_SIZE_M=CELL_SIZE_M,
        SPEED_MPS=SPEED_MPS,
        ALLOW_DIAGONALS=str(ALLOW_DIAGONALS),
        START=str(START),
        GOAL=str(GOAL),
        PLUME_CENTER=str(PLUME_CENTER),
        SIGMA_MAJOR=SIGMA_MAJOR,
        SIGMA_MINOR=SIGMA_MINOR,
        WIND_DIR_DEG=WIND_DIR_DEG,
        PEAK_DOSE=PEAK_DOSE,
        OBSTACLE_RECTS=str(OBSTACLE_RECTS),
        HOTSPOTS=str(HOTSPOTS),
        HEUR_MIN_DOSE_RATE_EPS=HEUR_MIN_DOSE_RATE_EPS,
    ))

script_path
'''