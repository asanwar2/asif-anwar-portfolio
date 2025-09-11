# Monte Carlo Radiation Shielding Simulator (Python)

This project implements a **Monte Carlo transport** simulator to study photon attenuation and dose build-up in shielding materials (lead, concrete, water, polyethylene). The work deepened my understanding of stochastic simulation, statistical tallies, and scientific visualization,

---

## Objective
**Build and validate** a lightweight Monte Carlo code that:
- simulates photon transport in a slab,
- tallies **depth–dose**, **2D dose maps**, and **transmission**,
- compares different materials, and
- quantifies uncertainty (mean ± SE) via replicate runs.

---

## Methods
- **Transport kernel:**  
  - Sample free path  
  - Interaction = absorption or scatter (isotropic in 2D with toy energy loss)  
- **Tallies:** 2D dose grid (x–y), 1D depth–dose (sum over y), transmission/reflection/absorption counts  
- **Validation:** Pure-absorption case vs. **Beer–Lambert**  
- **Uncertainty:** Replicate batches → **mean ± standard error** of transmission  
- **Auto-save & non-blocking plots:** All figures save to `./figs/` and appear **at once**

---

## Contents
- `mc_shielding.py` — main simulator + plotting + validation + uncertainty  
- (optional) `simulator.py` — small “live data” generator for dashboards (power, temps, etc.)

---

## File Index

| File Name         | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| `mc_shielding.py` | Monte Carlo simulator (slab geometry), material comparison, validation, UQ  |
| `figs/`           | Auto-saved figures (PNG, timestamped)                                       |

---

## How to Run

### 1) Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate      # On Windows: .venv\Scripts\activate
pip install numpy matplotlib
```

### 2) Environment Setup
2) Execute the Simulator
```bash
python mc_shielding.py
```
When you run the script, you will see:

- **Sample Trajectories** (subset of particle paths)
- **Depth–Dose curve**
- **2D Dose Map** (heatmap of deposited energy)
- **Material Comparison** (depth–dose overlays)
- **Transmission uncertainty** (mean ± SE)
- **Beer–Lambert validation** (theory vs MC)
- All figures open together and are saved to ./figs/.

3) Adjust Parameters (inside mc_shielding.py)
N_HIST = 20000        # increase for smoother curves (e.g., 100_000)
THICKNESS_CM = 10.0   # change slab thickness
MATERIALS["lead"] = Material("Lead", sigma_t=1.0, sigma_a=0.3)  # try your own

Example Usage

Run only the single-material demo at higher statistics:
```
mat = MATERIALS["concrete"]
res = run_mc(mat, n_hist=100_000)
visualize(res, title_suffix="(N=100k)", save_dir="figs")
plt.show()
```

Compare materials with a thicker slab:
```
compare_materials(thickness_cm=20.0, save_dir="figs")
plt.show()
```

Transmission with uncertainty (more reps, fewer histories each):
```
compare_materials_with_uncertainty(thickness_cm=10.0, n_hist=3000, n_reps=20, save_dir="figs")
plt.show()
```

Beer–Lambert validation with more data points:
```
validate_beer_lambert(thickness_list=(2,4,6,8,10,12), n_hist=10000, save_dir="figs")
plt.show()
```
## Outputs (Figures)
- **Sample Trajectories** — visual intuition for absorption vs scattering vs leakage
- **Depth–Dose** — how dose changes with depth into the slab
- **2D Dose Map** — spatial dose deposition across the slab
- **Material Comparison** — overlay of depth–dose curves for different materials
- **Transmission** (mean ± SE) — replicate-based error bars
- **Beer–Lambert Validation** — simulation vs analytic exponential decay

All figures are auto-saved as PNGs in ./figs/ with timestamps.

Uncertainty: Multiple replicate runs give a distribution of transmission fractions; plotted as mean ± standard error.

## Why It Matters

- Demonstrates core Monte Carlo principles without external codes like MCNP or OpenMC.
- Produces publication-quality figures for reports or posters.
- Acts as a teaching/demo tool for shielding intuition and as a baseline for more realistic models.

## Results (Typical Observations)
- Dose decreases with depth; scatter spreads deposition laterally.
- Hydrogen-rich materials (poly, water) often outperform per unit mass compared to high-Z materials like lead.
- Transmission uncertainty decreases as histories per replicate increase.

## Extensions / Future Work

- **Physics:** Add Klein–Nishina scattering, multigroup energies, dose in Gy with densities
- **Performance:** Speed up with Numba or JAX
- **Geometry:** Multilayer slabs (e.g., Al + PE), larger grids, 3D voxel geometries
- **Applications:** Compare dose vs areal density (g/cm²) for spacecraft feasibility; add simple CSDA proton mode for SPE scenarios

## Tools & Libraries
- Python 3.10+
- NumPy
- Matplotlib
