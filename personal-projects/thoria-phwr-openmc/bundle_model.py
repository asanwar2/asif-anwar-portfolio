"""
bundle_model.py — shared geometry and materials for the 37-element bundle.

This file doesn't run anything on its own. Scripts 03 and 04 import
build_model() from it so they don't each carry a copy of the geometry.

Python can't import a module whose name starts with a digit, which is why
this one has a word name instead of a number.
"""

import math
import openmc

# ---------------------------------------------------------------------------
# DIMENSIONS (cm) — representative CANDU-6 37-element values.
# Verify against a published benchmark before quoting any result.
# ---------------------------------------------------------------------------
R_FUEL = 0.6122
R_CLAD = 0.6540

RING_RADII = [0.0, 1.4885, 2.8755, 4.3305]
RING_COUNTS = [1, 6, 12, 18]
RING_OFFSETS = [0.0, 0.0, 15.0, 0.0]

R_PT_IN, R_PT_OUT = 5.1689, 5.6007
R_CT_IN, R_CT_OUT = 6.4478, 6.5875
LATTICE_PITCH = 28.575
ACTIVE_LENGTH = 49.53

N_PINS = sum(RING_COUNTS)

TH_FRACTION = 0.90
NOMINAL_COOLANT_DENSITY = 0.807
VOID_COOLANT_DENSITY = 0.0001


def pin_positions():
    """(x, y) for all 37 element centers."""
    coords = []
    for radius, count, offset in zip(RING_RADII, RING_COUNTS, RING_OFFSETS):
        if count == 1:
            coords.append((0.0, 0.0))
            continue
        for i in range(count):
            a = math.radians(offset + i * 360.0 / count)
            coords.append((radius * math.cos(a), radius * math.sin(a)))
    return coords


def build_fuel(kind):
    """kind is 'thoria' or 'natural_u'."""
    if kind == "thoria":
        thoria = openmc.Material(name="ThO2")
        thoria.add_element("Th", 1.0)
        thoria.add_element("O", 2.0)
        thoria.set_density("g/cm3", 10.0)

        urania = openmc.Material(name="UO2 HALEU")
        urania.add_element("U", 1.0, enrichment=19.75)
        urania.add_element("O", 2.0)
        urania.set_density("g/cm3", 10.5)

        m = openmc.Material.mix_materials(
            [thoria, urania], [TH_FRACTION, 1.0 - TH_FRACTION], "wo"
        )
        m.name = "Thoria-urania"
    elif kind == "natural_u":
        m = openmc.Material(name="Natural UO2")
        m.add_element("U", 1.0, enrichment=0.711)
        m.add_element("O", 2.0)
        m.set_density("g/cm3", 10.6)
    else:
        raise ValueError(f"unknown fuel kind: {kind!r}")

    m.temperature = 900.0
    return m


def build_model(fuel_kind="thoria",
                coolant_density=NOMINAL_COOLANT_DENSITY,
                particles=30000,
                batches=200,
                inactive=40):
    """Return an openmc.Model for one bundle in an infinite lattice."""
    fuel = build_fuel(fuel_kind)

    clad = openmc.Material(name="Zircaloy-4")
    clad.add_element("Zr", 0.9823, "wo")
    clad.add_element("Sn", 0.0145, "wo")
    clad.add_element("Fe", 0.0021, "wo")
    clad.add_element("Cr", 0.0010, "wo")
    clad.set_density("g/cm3", 6.55)
    clad.temperature = 600.0

    coolant = openmc.Material(name="D2O coolant")
    coolant.add_nuclide("H2", 2.0)
    coolant.add_element("O", 1.0)
    coolant.set_density("g/cm3", coolant_density)
    coolant.add_s_alpha_beta("c_D_in_D2O")
    coolant.temperature = 561.0

    moderator = openmc.Material(name="D2O moderator")
    moderator.add_nuclide("H2", 2.0)
    moderator.add_element("O", 1.0)
    moderator.set_density("g/cm3", 1.0851)
    moderator.add_s_alpha_beta("c_D_in_D2O")
    moderator.temperature = 342.0

    pt = openmc.Material(name="Zr-2.5Nb pressure tube")
    pt.add_element("Zr", 0.975, "wo")
    pt.add_element("Nb", 0.025, "wo")
    pt.set_density("g/cm3", 6.57)
    pt.temperature = 561.0

    gas = openmc.Material(name="CO2 annulus gas")
    gas.add_element("C", 1.0)
    gas.add_element("O", 2.0)
    gas.set_density("g/cm3", 0.0014)
    gas.temperature = 450.0

    ct = openmc.Material(name="Zircaloy-2 calandria tube")
    ct.add_element("Zr", 0.982, "wo")
    ct.add_element("Sn", 0.015, "wo")
    ct.add_element("Fe", 0.002, "wo")
    ct.add_element("Cr", 0.001, "wo")
    ct.set_density("g/cm3", 6.55)
    ct.temperature = 400.0

    # --- geometry -----------------------------------------------------
    cells = []
    coolant_region = -openmc.ZCylinder(r=R_PT_IN)

    for idx, (x, y) in enumerate(pin_positions()):
        fs = openmc.ZCylinder(x0=x, y0=y, r=R_FUEL)
        cs = openmc.ZCylinder(x0=x, y0=y, r=R_CLAD)
        cells.append(openmc.Cell(name=f"fuel_{idx}", fill=fuel, region=-fs))
        cells.append(openmc.Cell(name=f"clad_{idx}", fill=clad,
                                 region=+fs & -cs))
        coolant_region &= +cs

    cells.append(openmc.Cell(name="coolant", fill=coolant,
                             region=coolant_region))

    pt_in = openmc.ZCylinder(r=R_PT_IN)
    pt_out = openmc.ZCylinder(r=R_PT_OUT)
    ct_in = openmc.ZCylinder(r=R_CT_IN)
    ct_out = openmc.ZCylinder(r=R_CT_OUT)
    box = openmc.model.RectangularPrism(
        width=LATTICE_PITCH, height=LATTICE_PITCH, boundary_type="reflective"
    )

    cells += [
        openmc.Cell(name="pressure_tube", fill=pt, region=+pt_in & -pt_out),
        openmc.Cell(name="annulus", fill=gas, region=+pt_out & -ct_in),
        openmc.Cell(name="calandria_tube", fill=ct, region=+ct_in & -ct_out),
        openmc.Cell(name="moderator", fill=moderator, region=+ct_out & -box),
    ]

    model = openmc.Model()
    model.geometry = openmc.Geometry(cells)
    model.materials = openmc.Materials(
        [fuel, clad, coolant, moderator, pt, gas, ct]
    )

    settings = openmc.Settings()
    settings.batches = batches
    settings.inactive = inactive
    settings.particles = particles
    settings.source = openmc.IndependentSource(
        space=openmc.stats.Box((-4.5, -4.5, -1), (4.5, 4.5, 1),
                               only_fissionable=True)
    )
    settings.temperature = {"method": "interpolation"}
    model.settings = settings

    return model, fuel


def reactivity_mk(k):
    """k-eff (ufloat) -> reactivity in milli-k."""
    return (k - 1.0) / k * 1000.0
