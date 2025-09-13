# mc_shielding.py — all figures show at once (non-blocking)
from dataclasses import dataclass
from typing import Optional
import os, datetime as _dt

import numpy as np
import matplotlib.pyplot as plt

# ----------------------------
# Auto-save helpers
# ----------------------------
def _ensure_dir(d: Optional[str]) -> None:
    if d:
        os.makedirs(d, exist_ok=True)

def _save(fig, save_dir: Optional[str], name: str) -> None:
    if not save_dir:
        return
    _ensure_dir(save_dir)
    ts = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    fig.savefig(os.path.join(save_dir, f"{name}-{ts}.png"), dpi=300, bbox_inches="tight")

# ----------------------------
# Model & materials
# ----------------------------
np.random.seed(42)

@dataclass
class Material:
    name: str
    sigma_t: float  # [1/cm]
    sigma_a: float  # [1/cm]
    @property
    def sigma_s(self) -> float:
        return max(self.sigma_t - self.sigma_a, 0.0)

MATERIALS = {
    "lead":     Material("Lead",     1.0,   0.3),
    "concrete": Material("Concrete", 0.12,  0.02),
    "poly":     Material("Poly",     0.10,  0.01),
    "water":    Material("Water",    0.095, 0.005),
}

# Defaults
E0_MEV = 0.662
E_MIN  = 0.05
F_LOSS = 0.15
N_HIST = 20_000
THICKNESS_CM = 10.0
HEIGHT_CM    = 10.0
Y0_SPREAD    = 0.2
MAX_STEPS    = 10_000
NX, NY = 200, 120
PLOT_N_TRAJ = 200

# ----------------------------
# Core MC
# ----------------------------
def sample_free_path(sig_t, rng):
    xi = rng.random()
    return -np.log(xi) / sig_t

def sample_isotropic_direction_2d(rng):
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
    rng = np.random.default_rng(rng_seed)
    dx = thickness_cm / nx
    dy = height_cm / ny

    dose_map = np.zeros((ny, nx))
    transmitted = reflected = absorbed = 0
    trajs = []

    for n in range(n_hist):
        x = 0.0
        y = (rng.random() * 2 - 1) * Y0_SPREAD
        theta0 = (rng.random() - 0.5) * (np.pi / 36)
        dir_vec = np.array([np.cos(theta0), np.sin(theta0)])
        E = e0_mev
        if n < plot_n_traj:
            traj = [(x, y)]

        for _ in range(MAX_STEPS):
            if E < e_min:
                i = min(int((y + 0.5 * height_cm) / dy), ny - 1)
                j = min(int(x / dx), nx - 1)
                if 0 <= i < ny and 0 <= j < nx:
                    dose_map[i, j] += E
                absorbed += 1
                break

            s = np.inf if material.sigma_t <= 0 else sample_free_path(material.sigma_t, rng)

            # distances to boundaries
            s_exit_x = (thickness_cm - x) / dir_vec[0] if dir_vec[0] > 0 else (-x / dir_vec[0] if dir_vec[0] < 0 else np.inf)
            s_y = ((+0.5 * height_cm - y) / dir_vec[1] if dir_vec[1] > 0
                   else ((-0.5 * height_cm - y) / dir_vec[1] if dir_vec[1] < 0 else np.inf))

            # reflect on y if sooner than interaction & x exit
            if s_y < s and s_y < s_exit_x:
                x += s_y * dir_vec[0]
                y += s_y * dir_vec[1]
                if n < plot_n_traj:
                    traj.append((x, y))
                dir_vec[1] *= -1
                continue

            # exit on x if sooner
            if s_exit_x < s:
                x += s_exit_x * dir_vec[0]
                y += s_exit_x * dir_vec[1]
                if n < plot_n_traj:
                    traj.append((x, y))
                if x >= thickness_cm - 1e-9:
                    transmitted += 1
                else:
                    reflected += 1
                break

            # interaction inside slab
            x += s * dir_vec[0]
            y += s * dir_vec[1]
            if n < plot_n_traj:
                traj.append((x, y))
            p_abs = material.sigma_a / material.sigma_t if material.sigma_t > 0 else 0.0
            i = min(int((y + 0.5 * height_cm) / dy), ny - 1)
            j = min(int(x / dx), nx - 1)

            if np.random.random() < p_abs:
                if 0 <= i < ny and 0 <= j < nx:
                    dose_map[i, j] += E
                absorbed += 1
                break
            else:
                dE = f_loss * E
                if 0 <= i < ny and 0 <= j < nx:
                    dose_map[i, j] += dE
                E -= dE
                dir_vec = sample_isotropic_direction_2d(rng)
                continue

        if n < plot_n_traj:
            trajs.append(np.array(traj))

    depth_dose = dose_map.sum(axis=0)
    x_centers = (np.arange(nx) + 0.5) * (thickness_cm / nx)
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
# Plotters (non-blocking + auto-save)
# ----------------------------
def visualize(results: dict, title_suffix: str = "", save_dir: Optional[str] = None):
    dose_map = results["dose_map"]
    depth_dose = results["depth_dose"]
    x_centers = results["x_centers"]
    trajs = results["trajs"]
    cfg = results["config"]

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
    plt.tight_layout(); plt.show(block=False)

    fig2, ax2 = plt.subplots(figsize=(7, 3.5))
    ax2.plot(x_centers, depth_dose)
    ax2.set_title(f"Depth-Dose — {cfg['material']} {title_suffix}")
    ax2.set_xlabel("Depth x (cm)")
    ax2.set_ylabel("Dose tally (a.u.)")
    ax2.grid(True, alpha=0.3)
    _save(fig2, save_dir, f"depthdose_{cfg['material']}")
    plt.tight_layout(); plt.show(block=False)

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

    print("Transmission fraction:")
    for name, frac in trans.items():
        print(f"  {name:10s}: {frac:.4f}")

# ----------------------------
# Validation & Uncertainty
# ----------------------------
def beer_lambert_expected(sigma_t: float, thickness_cm: float) -> float:
    return float(np.exp(-sigma_t * thickness_cm))

def transmission_stats(material: Material, thickness_cm: float,
                       n_hist: int = 5000, n_reps: int = 20, rng_seed: int = 99):
    rng = np.random.default_rng(rng_seed)
    fracs = []
    for _ in range(n_reps):
        seed = int(rng.integers(0, 1_000_000))
        res = run_mc(material, n_hist=n_hist, thickness_cm=thickness_cm, rng_seed=seed)
        fracs.append(res["transmitted"] / n_hist)
    fracs = np.array(fracs)
    return fracs.mean(), fracs.std(ddof=1), fracs

def validate_beer_lambert(thickness_list=(2.0, 4.0, 6.0, 8.0, 10.0), n_hist=10_000,
                          save_dir: Optional[str] = None):
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
    fig, ax = plt.subplots(figsize=(7, 3.6))
    labels, means, ses = [], [], []
    for k in material_keys:
        mat = MATERIALS[k]
        mu, sd, _ = transmission_stats(mat, thickness_cm=thickness_cm,
                                       n_hist=n_hist, n_reps=n_reps, rng_seed=rng_seed)
        se = sd / max(np.sqrt(n_reps - 1), 1.0)
        labels.append(mat.name); means.append(mu); ses.append(se)
    ax.errorbar(labels, means, yerr=ses, fmt='o', capsize=4)
    ax.set_ylabel("Transmission fraction (mean ± SE)")
    ax.set_title(f"Transmission by material (L={thickness_cm} cm, N={n_hist}×{n_reps})")
    ax.grid(True, axis='y', alpha=0.3)
    _save(fig, save_dir, f"transmission_uncertainty_L{thickness_cm}cm")
    plt.tight_layout(); plt.show(block=False)

# ----------------------------
# Script entry (all figures shown together at end)
# ----------------------------
if __name__ == "__main__":
    OUT = "figs"

    mat = MATERIALS["concrete"]
    res = run_mc(mat, n_hist=N_HIST)
    visualize(res, title_suffix=f"(N={N_HIST})", save_dir=OUT)

    compare_materials(thickness_cm=10.0, save_dir=OUT)
    compare_materials_with_uncertainty(thickness_cm=10.0, n_hist=4000, n_reps=12, save_dir=OUT)
    validate_beer_lambert(thickness_list=(2,4,6,8,10), n_hist=8000, save_dir=OUT)

    # Display ALL accumulated figures at once
    plt.show()
