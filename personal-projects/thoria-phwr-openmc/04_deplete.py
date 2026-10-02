"""
Stage 4: burnup. k-infinity versus burnup, plus the U-233 breeding curve.

This backs the "higher burnup" claim, and the U-233 curve is the thorium
story in one plot: Th-232 captures a neutron, decays through Pa-233, and
becomes fissile U-233 that then contributes to power.

SLOW. Expect several hours. Start it and walk away.

Needs:
  - bundle_model.py in this folder
  - chain_endfb80_pwr.xml in this folder

Get the chain file with:
  wget -O chain_endfb80_pwr.xml \\
    https://anl.box.com/shared/static/nyezmyuofd4eqt6wzd626lqth7wvpprr.xml

Run:  python 04_deplete.py
"""

import math
import os

import numpy as np
import openmc
import openmc.deplete

from bundle_model import (
    build_model, R_FUEL, ACTIVE_LENGTH, N_PINS, NOMINAL_COOLANT_DENSITY
)

CHAIN = "chain_endfb80_pwr.xml"

# Total fuel volume in the bundle. Depletion needs this to turn reaction
# rates into number densities — without it OpenMC will refuse to run.
FUEL_VOLUME = N_PINS * math.pi * R_FUEL**2 * ACTIVE_LENGTH   # cm3

SPECIFIC_POWER = 25.0    # W per gram of heavy metal

# Burnup increments in MWd/kgHM (each entry is a STEP, not a cumulative total).
# Fine early to catch Xe/Sm equilibrium, coarse later.
# Natural-U CANDU discharges near 7.5 — the question is how far past that
# thoria-urania can run.
BURNUP_STEPS = [
    0.1, 0.3, 0.5, 1.0, 1.0, 2.0, 2.5, 2.5,
    5.0, 5.0, 10.0, 10.0, 10.0, 10.0,
]

FUEL_KIND = "thoria"     # switch to "natural_u" for the reference case


def main():
    if not os.path.exists(CHAIN):
        raise SystemExit(
            f"\nMissing {CHAIN} in this folder.\n"
            "Download it with the wget command in this file's docstring.\n"
        )

    # Scripts 01 and 02 write XML into this folder as a side effect. The
    # depletion operator would pick those up instead of the model built
    # here, and fail with "No material exists with ID=N". Clear them.
    for stale in ("materials.xml", "geometry.xml", "settings.xml",
                  "tallies.xml", "plots.xml", "model.xml"):
        if os.path.exists(stale):
            os.remove(stale)
            print(f"removed stale {stale}")

    model, fuel = build_model(
        FUEL_KIND,
        coolant_density=NOMINAL_COOLANT_DENSITY,
        particles=10000,   # lower than script 03 — depletion runs this many times
        batches=100,
        inactive=20,
    )

    # One fuel material fills all 37 pins, so its volume is the bundle total.
    fuel.volume = FUEL_VOLUME
    fuel.depletable = True

    operator = openmc.deplete.CoupledOperator(model, CHAIN)
    integrator = openmc.deplete.PredictorIntegrator(
        operator,
        timesteps=BURNUP_STEPS,
        power_density=SPECIFIC_POWER,
        timestep_units="MWd/kg",
    )

    print(f"\nDepleting {fuel.name} to "
          f"{sum(BURNUP_STEPS):.1f} MWd/kgHM in {len(BURNUP_STEPS)} steps.")
    print("This will take hours. Output appears after each step.\n")

    integrator.integrate()
    report(fuel.id)


def report(fuel_id):
    results = openmc.deplete.Results("depletion_results.h5")

    _, keff = results.get_keff()
    k_vals = keff[:, 0]
    k_errs = keff[:, 1]

    burnup = np.concatenate([[0.0], np.cumsum(BURNUP_STEPS)])
    burnup = burnup[:len(k_vals)]

    print("\n" + "=" * 52)
    print(f"{'Burnup [MWd/kgHM]':>20}{'k-inf':>16}{'+/-':>12}")
    print("-" * 52)
    for b, k, e in zip(burnup, k_vals, k_errs):
        print(f"{b:>20.2f}{k:>16.5f}{e:>12.5f}")
    print("=" * 52)

    # Rough discharge burnup: where k-inf crosses 1
    below = np.where(k_vals < 1.0)[0]
    if len(below):
        i = below[0]
        if i > 0:
            b0, b1 = burnup[i - 1], burnup[i]
            k0, k1 = k_vals[i - 1], k_vals[i]
            crossing = b0 + (k0 - 1.0) * (b1 - b0) / (k0 - k1)
            print(f"\nk-inf crosses 1.0 near {crossing:.1f} MWd/kgHM")
    else:
        print("\nk-inf never dropped below 1.0 — extend BURNUP_STEPS.")

    plot(burnup, k_vals, k_errs, results, fuel_id)


def plot(burnup, k_vals, k_errs, results, fuel_id):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\nmatplotlib not installed — skipping plot.")
        print("Install it with:  conda install matplotlib")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 9), sharex=True)

    ax1.errorbar(burnup, k_vals, yerr=k_errs, marker="o", lw=1.5, capsize=3)
    ax1.axhline(1.0, ls="--", c="k", lw=1, label="k = 1")
    ax1.set_ylabel("k-infinity")
    ax1.set_title(f"{FUEL_KIND}: reactivity vs burnup")
    ax1.grid(alpha=0.3)
    ax1.legend()

    try:
        _, u233 = results.get_atoms(str(fuel_id), "U233")
        _, u235 = results.get_atoms(str(fuel_id), "U235")
        n = min(len(burnup), len(u233))
        ax2.plot(burnup[:n], u233[:n], marker="s", label="U-233 (bred)")
        ax2.plot(burnup[:n], u235[:n], marker="^", label="U-235 (consumed)")
        ax2.set_yscale("log")
        ax2.set_ylabel("Atoms")
        ax2.legend()
    except Exception as exc:
        print(f"\nCouldn't plot nuclide inventories: {exc}")
        print("Check material IDs in depletion_results.h5.")

    ax2.set_xlabel("Burnup [MWd/kgHM]")
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("burnup.png", dpi=150)
    print("\nWrote burnup.png")


if __name__ == "__main__":
    main()
