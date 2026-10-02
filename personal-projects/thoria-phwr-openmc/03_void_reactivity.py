"""
Stage 3: coolant void reactivity (CVR).

The headline number. Natural-uranium CANDU fuel has a POSITIVE coolant void
coefficient — lose coolant and reactivity goes UP. That's the safety problem
thoria-urania fuel is partly meant to address, so the comparison is the point.

    rho = (k - 1) / k
    CVR = rho(voided) - rho(nominal),  reported in milli-k (mk)

Runs four cases: 2 fuels x 2 coolant states. Expect 20-60 minutes total.

Run:  python 03_void_reactivity.py
"""

import openmc

from bundle_model import (
    build_model,
    reactivity_mk,
    NOMINAL_COOLANT_DENSITY,
    VOID_COOLANT_DENSITY,
)


def run_case(fuel_kind, coolant_density, label):
    print(f"\n{'>' * 60}")
    print(f">>> {label}")
    print(f"{'>' * 60}")

    model, _ = build_model(fuel_kind, coolant_density)
    statepoint_path = model.run()

    with openmc.StatePoint(statepoint_path) as sp:
        return sp.keff


if __name__ == "__main__":
    cases = [
        ("natural_u", "Natural UO2"),
        ("thoria", "Thoria-urania"),
    ]

    results = {}
    for kind, name in cases:
        k_nom = run_case(kind, NOMINAL_COOLANT_DENSITY,
                         f"{name} — coolant present")
        k_void = run_case(kind, VOID_COOLANT_DENSITY,
                          f"{name} — coolant voided")
        cvr = reactivity_mk(k_void) - reactivity_mk(k_nom)
        results[name] = (k_nom, k_void, cvr)

    print("\n" + "=" * 70)
    print(f"{'Fuel':<18}{'k (nominal)':>15}{'k (voided)':>15}{'CVR [mk]':>20}")
    print("-" * 70)
    for name, (kn, kv, cvr) in results.items():
        print(f"{name:<18}"
              f"{kn.nominal_value:>15.5f}"
              f"{kv.nominal_value:>15.5f}"
              f"{cvr.nominal_value:>14.2f} +/-{cvr.std_dev:>4.2f}")
    print("=" * 70)

    print("""
HOW TO READ THIS

Natural UO2 should come out clearly POSITIVE. That is the known CANDU
result, and it is your validation that the model behaves. If it doesn't,
fix that before you look at the thoria row at all.

If the thoria case is less positive: that's the result worth writing up.
If it's more positive: report it anyway and work out why. A negative
result you can explain beats a positive one you can't.

Check your uncertainty. If +/- is comparable to the CVR itself, you have
no result — raise `particles` in build_model() and rerun.
""")
