# mc_shielding.py — all figures show at once
# -------------------------------------------------------------------
# What this script does:
# - Runs a simple Monte Carlo (random sampling) simulation for photons
#   moving through a flat slab of material (lead, concrete, water, poly).
# - Tallies how much “dose” or energy is deposited as particles travel,
#   and whether they transmit, reflect, or get absorbed.
# - Produces 3 kinds of plots:
#     (1) sample particle trajectories,
#     (2) depth–dose curve (dose vs. depth),
#     (3) 2D dose heatmap.
# - Also includes:
#     (4) a comparison plot across materials,
#     (5) an uncertainty plot (mean ± SE for transmission),
#     (6) a Beer–Lambert validation figure.
# - Figures are auto-saved to ./figs and shown all together at the end.
# -------------------------------------------------------------------

from dataclasses import dataclass
from typing import Optional
import os, datetime as _dt

import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Auto-save helpers
# ----------------------------
def _ensure_dir(d: Optional[str]) -> None:
    """
    Create the output folder if it doesn't exist (safe to call multiple times).
    """
    if d:
        os.makedirs(d, exist_ok=True)

def _save(fig, save_dir: Optional[str], name: str) -> None:
    """
    Save a figure as a PNG with a timestamped filename.
    If save_dir is None or empty, do nothing.
    """
    if not save_dir:
        return
    _ensure_dir(save_dir)
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    fig.savefig(os.path.join(save_dir, f"{name}-{ts}.png"), dpi=300, bbox_inches="tight")

# ----------------------------
# Model & materials
# ----------------------------
# Fix the global seed so runs look the same each time to help debugging/demos
np.random.seed(42)

@dataclass
class Material:
    """
    Simple material with macroscopic cross sections:
      sigma_t: total [1/cm]   → how often any interaction happens
      sigma_a: absorption [1/cm] → chance the particle is absorbed
    We derive sigma_s (scattering) = sigma_t - sigma_a (never negative).
    """
    name: str
    sigma_t: float  # [1/cm]
    sigma_a: float  # [1/cm]
    @property
    def sigma_s(self) -> float:
        return max(self.sigma_t - self.sigma_a, 0.0)

# A few “toy” materials with made-up but reasonable relative numbers
MATERIALS = {
    "lead":     Material("Lead",     1.0,   0.3),
    "concrete": Material("Concrete", 0.12,  0.02),
    "poly":     Material("Poly",     0.10,  0.01),
    "water":    Material("Water",    0.095, 0.005),
}

# Defaults (feel free to tweak for experiments)
E0_MEV = 0.662       # starting photon energy (MeV), e.g., Cs-137 line
E_MIN  = 0.05        # stop tracking if energy drops below this (MeV)
F_LOSS = 0.15        # fraction of energy lost on each scatter (toy model)
N_HIST = 20_000      # number of particle histories to simulate
THICKNESS_CM = 10.0  # slab thickness in x-direction [cm]
HEIGHT_CM    = 10.0  # slab height in y-direction [cm]
Y0_SPREAD    = 0.2   # initial beam half-width in y [cm] (small spread around y=0)
MAX_STEPS    = 10_000# safety cap on steps per particle (avoid infinite loops)
NX, NY = 200, 120    # grid size for tallies (x bins, y bins)
PLOT_N_TRAJ = 200    # how many particle paths to draw in the trajectories plot

# ----------------------------
# Core MC utilities
# ----------------------------
def sample_free_path(sig_t, rng):
    """
    Sample the random travel distance before the next interaction.
    Formula: s = -ln(xi)/sigma_t  (standard exponential distribution).
    """
    xi = rng.random()
    return -np.log(xi) / sig_t

def sample_isotropic_direction_2d(rng):
    """
    Pick a random direction in 2D (angle uniformly in [-pi, pi]).
    Returns a unit vector [cos(theta), sin(theta)].
    """
    theta = (rng.random() * 2.0 - 1.0) * np.pi
    return np.array([np.cos(theta), np.sin(theta)])

def run_mc(material: Material,
           n_hist: int = N_HIST,
           thickness_cm: float = THICKNESS_CM,
           height_cm: float = HEIGHT_CM,
           e0_mev: float = E0_MEV,
           e_min: float = E_MIN,
           f_loss: float = F_LOSS,
           nx: int = NX,
           ny: int = NY,
           plot_n_traj: int = PLOT_N_TRAJ,
           rng_seed: int = 123):
    """
    Run the Monte Carlo for a single slab/material and return tallies + metadata.

      1) Start at x=0 (left face), y near 0 (small spread), small angular spread.
      2) While energy > cutoff:
          a) Sample random free path s until next interaction.
          b) Check if we hit a boundary (exit/reflect) before s; if so, handle it.
          c) If we interact inside:
             - With prob p_abs, deposit all remaining energy and stop.
             - Else scatter: deposit a fraction of energy (toy), reduce E, and pick a new direction.
      3) Accumulate dose into a 2D grid (ny x nx).
      4) Track transmitted/reflected/absorbed counts.

    Returns with:
      - 2D dose map, 1D depth–dose, x-bin centers, counts, sample trajectories, and config.
    """
    rng = np.random.default_rng(rng_seed)

    # Bin sizes for the dose grid
    dx = thickness_cm / nx
    dy = height_cm / ny

    # Initializing tallies
    dose_map = np.zeros((ny, nx))  # energy deposited per cell (arbitrary units)
    transmitted = reflected = absorbed = 0
    trajs = []  # a few sample paths for plotting

    # Loop over particle histories
    for n in range(n_hist):
        # Start at left boundary, near y=0, with a tiny angle spread
        x = 0.0
        y = (rng.random() * 2 - 1) * Y0_SPREAD
        theta0 = (rng.random() - 0.5) * (np.pi / 36)  # small angular spread
        dir_vec = np.array([np.cos(theta0), np.sin(theta0)])
        E = e0_mev  # current energy (MeV)
        if n < plot_n_traj:
            traj = [(x, y)]  # record points for the trajectories plot

        # Walk until we stop (absorbed, too low energy, or leaked out)
        for _ in range(MAX_STEPS):
            # Stop if energy is very low → deposit the last bit and count as absorbed
            if E < e_min:
                i = min(int((y + 0.5 * height_cm) / dy), ny - 1)
                j = min(int(x / dx), nx - 1)
                if 0 <= i < ny and 0 <= j < nx:
                    dose_map[i, j] += E  # dump remaining energy into the current cell
                absorbed += 1
                break

            # How far to next interaction in this material?
            s = np.inf if material.sigma_t <= 0 else sample_free_path(material.sigma_t, rng)

            # Distances to the nearest boundaries (x exit, y top/bottom reflect)
            # If y-boundary is closer than interaction, we "bounce" (reflect in y).
            s_exit_x = (thickness_cm - x) / dir_vec[0] if dir_vec[0] > 0 else (-x / dir_vec[0] if dir_vec[0] < 0 else np.inf)
            s_y = ((+0.5 * height_cm - y) / dir_vec[1] if dir_vec[1] > 0
                   else ((-0.5 * height_cm - y) / dir_vec[1] if dir_vec[1] < 0 else np.inf))

            # Case 1: hit the horizontal boundary first → reflect in y
            if s_y < s and s_y < s_exit_x:
                x += s_y * dir_vec[0]
                y += s_y * dir_vec[1]
                if n < plot_n_traj:
                    traj.append((x, y))
                dir_vec[1] *= -1  # flip vertical component
                continue

            # Case 2: hit the exit (right or left x-face) before interacting
            if s_exit_x < s:
                x += s_exit_x * dir_vec[0]
                y += s_exit_x * dir_vec[1]
                if n < plot_n_traj:
                    traj.append((x, y))
                if x >= thickness_cm - 1e-9:
                    transmitted += 1  # made it through the slab
                else:
                    reflected += 1    # leaked out the entrance side
                break

            # Case 3: interact inside the material
            x += s * dir_vec[0]
            y += s * dir_vec[1]
            if n < plot_n_traj:
                traj.append((x, y))

            # Probability of absorption at the interaction point
            p_abs = material.sigma_a / material.sigma_t if material.sigma_t > 0 else 0.0

            # Which grid cell are we in now? (i=row=y, j=col=x)
            i = min(int((y + 0.5 * height_cm) / dy), ny - 1)
            j = min(int(x / dx), nx - 1)

            # Roulette: absorb or scatter
            if np.random.random() < p_abs:
                # Absorb: deposit all remaining energy and stop
                if 0 <= i < ny and 0 <= j < nx:
                    dose_map[i, j] += E
                absorbed += 1
                break
            else:
                # Scatter: deposit a fraction of energy (toy), reduce E, pick new direction
                dE = f_loss * E
                if 0 <= i < ny and 0 <= j < nx:
                    dose_map[i, j] += dE
                E -= dE
                dir_vec = sample_isotropic_direction_2d(rng)
                continue

        # Save this trajectory (only for the first few particles to avoid huge memory)
        if n < plot_n_traj:
            trajs.append(np.array(traj))

    # Turn 2D map into a 1D depth–dose curve by summing over y
    depth_dose = dose_map.sum(axis=0)
    # x-coordinate for the center of each x-bin (for plotting)
    x_centers = (np.arange(nx) + 0.5) * (thickness_cm / nx)

    # Package results for the plotting functions
    return {
        "dose_map": dose_map,
        "depth_dose": depth_dose,
        "x_centers": x_centers,
        "transmitted": transmitted,
        "reflected": reflected,
        "absorbed": absorbed,
        "trajs": trajs,
        "config": {
            "material": material.name,
            "n_hist": n_hist,
            "thickness_cm": thickness_cm,
            "height_cm": height_cm,
            "e0_mev": e0_mev,
            "f_loss": f_loss,
            "nx": nx,
            "ny": ny,
        },
    }

# ----------------------------
# Plotters 
# ----------------------------
def visualize(results: dict, title_suffix: str = "", save_dir: Optional[str] = None):
    """
    Make the 3 main plots: trajectories, depth–dose, and 2D dose heatmap.
    We also save them to disk (if save_dir is set).
    """
    dose_map = results["dose_map"]
    depth_dose = results["depth_dose"]
    x_centers = results["x_centers"]
    trajs = results["trajs"]
    cfg = results["config"]

    # 1) Trajectories (just a subset to keep the plot readable)
    fig1, ax1 = plt.subplots(figsize=(7, 4))
    for t in trajs:
        ax1.plot(t[:, 0], t[:, 1], lw=0.6, alpha=0.5)
    ax1.set_title(f"Sample Trajectories — {cfg['material']} {title_suffix}")
    ax1.set_xlabel("x (cm)")
    ax1.set_ylabel("y (cm)")
    ax1.set_xlim(0, cfg["thickness_cm"])
    ax1.set_ylim(-0.5 * cfg["height_cm"], 0.5 * cfg["height_cm"])
    ax1.grid(True, alpha=0.2)
    _save(fig1, save_dir, f"traj_{cfg['material']}")
    plt.tight_layout(); plt.show(block=False)  # non-blocking show

    # 2) Depth–dose curve (sum of dose in y for each x bin)
    fig2, ax2 = plt.subplots(figsize=(7, 3.5))
    ax2.plot(x_centers, depth_dose)
    ax2.set_title(f"Depth-Dose — {cfg['material']} {title_suffix}")
    ax2.set_xlabel("Depth x (cm)")
    ax2.set_ylabel("Dose tally (a.u.)")
    ax2.grid(True, alpha=0.3)
    _save(fig2, save_dir, f"depthdose_{cfg['material']}")
    plt.tight_layout(); plt.show(block=False)

    # 3) 2D dose map (heatmap of dose deposition across x–y)
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    im = ax3.imshow(dose_map, origin='lower',
                    extent=[0, cfg["thickness_cm"], -0.5 * cfg["height_cm"], 0.5 * cfg["height_cm"]],
                    aspect='auto')
    ax3.set_title(f"2D Dose Map — {cfg['material']} {title_suffix}")
    ax3.set_xlabel("x (cm)")
    ax3.set_ylabel("y (cm)")
    cbar = plt.colorbar(im, ax=ax3)
    cbar.set_label("Dose tally (a.u.)")
    _save(fig3, save_dir, f"dosemap_{cfg['material']}")
    plt.tight_layout(); plt.show(block=False)

def compare_materials(material_keys=("lead", "concrete", "poly", "water"),
                      thickness_cm=THICKNESS_CM, n_hist=N_HIST//2, rng_seed=7,
                      save_dir: Optional[str] = None):
    """
    Run the simulation for several materials and overlay their depth–dose curves.
    Also print the transmission fraction for each material.
    """
    fig, ax = plt.subplots(figsize=(7, 3.5))
    trans = {}
    for k in material_keys:
        mat = MATERIALS[k]
        res = run_mc(mat, n_hist=n_hist, thickness_cm=thickness_cm, rng_seed=rng_seed)
        ax.plot(res["x_centers"], res["depth_dose"], label=mat.name)
        trans[mat.name] = res["transmitted"] / n_hist
    ax.set_title(f"Depth-Dose vs Material (L={thickness_cm} cm)")
    ax.set_xlabel("Depth x (cm)")
    ax.set_ylabel("Dose tally (a.u.)")
    ax.grid(True, alpha=0.3)
    ax.legend()
    _save(fig, save_dir, f"depthdose_vs_material_L{thickness_cm}cm")
    plt.tight_layout(); plt.show(block=False)

    # Print out transmission fractions to the console for quick comparison
    print("Transmission fraction:")
    for name, frac in trans.items():
        print(f"  {name:10s}: {frac:.4f}")

# ----------------------------
# Validation & Uncertainty
# ----------------------------
def beer_lambert_expected(sigma_t: float, thickness_cm: float) -> float:
    """
    Analytical transmission if everything is absorbed (no scattering):
      T = exp(-sigma_t * thickness)
    used to check that our Monte Carlo matches the simple theory
    in the pure-absorption limit.
    """
    return float(np.exp(-sigma_t * thickness_cm))

def transmission_stats(material: Material, thickness_cm: float,
                       n_hist: int = 5000, n_reps: int = 20, rng_seed: int = 99):
    """
    Run multiple replicate batches to estimate mean and standard deviation
    of the transmission fraction to draw error bars.
    """
    rng = np.random.default_rng(rng_seed)
    fracs = []
    for _ in range(n_reps):
        seed = int(rng.integers(0, 1_000_000))  # different seed per replicate
        res = run_mc(material, n_hist=n_hist, thickness_cm=thickness_cm, rng_seed=seed)
        fracs.append(res["transmitted"] / n_hist)
    fracs = np.array(fracs)
    return fracs.mean(), fracs.std(ddof=1), fracs

def validate_beer_lambert(thickness_list=(2.0, 4.0, 6.0, 8.0, 10.0), n_hist=10_000,
                          save_dir: Optional[str] = None):
    """
    Compare Monte Carlo transmission (points) against Beer–Lambert theory (line)
    in the pure absorption limit (sigma_a = sigma_t, i.e., no scatter).
    """
    # Build a special “no-scatter” material by setting sigma_a = sigma_t
    mat = Material("No-Scatter Test", sigma_t=0.2, sigma_a=0.2)
    sims, theory = [], []
    for L in thickness_list:
        res = run_mc(mat, n_hist=n_hist, thickness_cm=L)
        sims.append(res["transmitted"] / n_hist)
        theory.append(beer_lambert_expected(mat.sigma_t, L))
    sims = np.array(sims); theory = np.array(theory)

    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.plot(thickness_list, theory, label="Beer–Lambert (theory)")
    ax.plot(thickness_list, sims, 'o--', label="Monte Carlo (toy)")
    ax.set_xlabel("Thickness (cm)")
    ax.set_ylabel("Transmission fraction")
    ax.set_title("Validation: Pure absorption limit")
    ax.grid(True, alpha=0.3)
    ax.legend()
    _save(fig, save_dir, "beer_lambert_validation")
    plt.tight_layout(); plt.show(block=False)

def compare_materials_with_uncertainty(material_keys=("lead", "concrete", "poly", "water"),
                                       thickness_cm=10.0, n_hist=4000, n_reps=12, rng_seed=7,
                                       save_dir: Optional[str] = None):
    """
    Draw a transmission bar/point plot (mean and standard error) across materials
    by running several replicate batches per material.
    """
    fig, ax = plt.subplots(figsize=(7, 3.6))
    labels, means, ses = [], [], []
    for k in material_keys:
        mat = MATERIALS[k]
        mu, sd, _ = transmission_stats(mat, thickness_cm=thickness_cm,
                                       n_hist=n_hist, n_reps=n_reps, rng_seed=rng_seed)
        se = sd / max(np.sqrt(n_reps - 1), 1.0)  # standard error of the mean
        labels.append(mat.name); means.append(mu); ses.append(se)
    ax.errorbar(labels, means, yerr=ses, fmt='o', capsize=4)
    ax.set_ylabel("Transmission fraction (mean ± SE)")
    ax.set_title(f"Transmission by material (L={thickness_cm} cm, N={n_hist}×{n_reps})")
    ax.grid(True, axis='y', alpha=0.3)
    _save(fig, save_dir, f"transmission_uncertainty_L{thickness_cm}cm")
    plt.tight_layout(); plt.show(block=False)

# ----------------------------
# Script entry (all figures shown together)
# ----------------------------
if __name__ == "__main__":
    # Folder where PNGs are saved (created automatically)
    OUT = "figs"

    # 1) Single-material demo: trajectories, depth–dose, 2D heatmap
    mat = MATERIALS["concrete"]
    res = run_mc(mat, n_hist=N_HIST)
    visualize(res, title_suffix=f"(N={N_HIST})", save_dir=OUT)

    # 2) Depth–dose overlay across materials (same thickness)
    compare_materials(thickness_cm=10.0, save_dir=OUT)

    # 3) Transmission uncertainty plot (replicates per material)
    compare_materials_with_uncertainty(thickness_cm=10.0, n_hist=4000, n_reps=12, save_dir=OUT)

    # 4) Beer–Lambert validation (pure absorption limit)
    validate_beer_lambert(thickness_list=(2,4,6,8,10), n_hist=8000, save_dir=OUT)

    # Show ALL figures at the very end (so they appear together)
    plt.show()
