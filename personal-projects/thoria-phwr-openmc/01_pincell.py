"""
Stage 1: a single thoria-urania fuel pin in an infinite lattice.

Goal: confirm your install works and get a feel for the OpenMC API.
This is not a CANDU model yet. It's one pin with reflective boundaries,
which gives you k-infinity for an infinite array of identical pins.

Run:  python 01_pincell.py
"""

import openmc

# ---------------------------------------------------------------------------
# 1. MATERIALS
# ---------------------------------------------------------------------------
# In OpenMC you build a Material, add nuclides or elements to it, and set a
# density. Numbers after each element are atom fractions by default.

# Thoria: ThO2
thoria = openmc.Material(name="ThO2")
thoria.add_element("Th", 1.0)
thoria.add_element("O", 2.0)
thoria.set_density("g/cm3", 10.0)

# Urania with HALEU. The `enrichment` argument is weight percent U-235.
urania = openmc.Material(name="UO2 (HALEU)")
urania.add_element("U", 1.0, enrichment=19.75)
urania.add_element("O", 2.0)
urania.set_density("g/cm3", 10.5)

# Mix them. 'wo' = weight fractions. Adjust this ratio to explore the design
# space — it is one of the main knobs you have.
TH_FRACTION = 0.90
fuel = openmc.Material.mix_materials(
    [thoria, urania], [TH_FRACTION, 1.0 - TH_FRACTION], "wo"
)
fuel.name = f"Thoria-urania ({TH_FRACTION:.0%} ThO2)"
fuel.temperature = 900.0  # K, roughly fuel average

# Zircaloy-4 cladding
clad = openmc.Material(name="Zircaloy-4")
clad.add_element("Zr", 0.9823, "wo")
clad.add_element("Sn", 0.0145, "wo")
clad.add_element("Fe", 0.0021, "wo")
clad.add_element("Cr", 0.0010, "wo")
clad.set_density("g/cm3", 6.55)
clad.temperature = 600.0

# Heavy water coolant. add_s_alpha_beta gives thermal scattering treatment —
# leave it out and your thermal spectrum will be wrong.
coolant = openmc.Material(name="D2O coolant")
coolant.add_nuclide("H2", 2.0)
coolant.add_element("O", 1.0)
coolant.set_density("g/cm3", 0.807)  # ~561 K
coolant.add_s_alpha_beta("c_D_in_D2O")
coolant.temperature = 561.0

materials = openmc.Materials([fuel, clad, coolant])
materials.export_to_xml()

# ---------------------------------------------------------------------------
# 2. GEOMETRY
# ---------------------------------------------------------------------------
# OpenMC geometry is CSG: define surfaces, then cells as regions bounded by
# them. `-surface` means inside; `+surface` means outside.

R_FUEL = 0.6122  # cm, pellet radius
R_CLAD = 0.6540  # cm, clad outer radius
PITCH = 1.6      # cm, arbitrary for this test problem

fuel_outer = openmc.ZCylinder(r=R_FUEL)
clad_outer = openmc.ZCylinder(r=R_CLAD)

box = openmc.model.RectangularPrism(
    width=PITCH, height=PITCH, boundary_type="reflective"
)

fuel_cell = openmc.Cell(name="fuel", fill=fuel, region=-fuel_outer)
clad_cell = openmc.Cell(name="clad", fill=clad, region=+fuel_outer & -clad_outer)
cool_cell = openmc.Cell(name="coolant", fill=coolant, region=+clad_outer & -box)

geometry = openmc.Geometry([fuel_cell, clad_cell, cool_cell])
geometry.export_to_xml()

# ---------------------------------------------------------------------------
# 3. SETTINGS
# ---------------------------------------------------------------------------
# batches      = total generations of neutrons
# inactive     = generations discarded while the fission source converges
# particles    = neutrons per generation
# More particles = tighter statistics. More inactive = better converged source.

settings = openmc.Settings()
settings.batches = 100
settings.inactive = 20
settings.particles = 5000
settings.source = openmc.IndependentSource(
    space=openmc.stats.Point((0, 0, 0))
)
# ENDF/B-VIII.0 tabulates cross sections at 250/294/600/900/1200/2500 K.
# The 561 K coolant falls between points, so interpolate rather than
# demanding an exact match (the default would abort).
settings.temperature = {"method": "interpolation"}
settings.export_to_xml()

# ---------------------------------------------------------------------------
# 4. RUN
# ---------------------------------------------------------------------------
openmc.run()

# Read the result back out
with openmc.StatePoint(f"statepoint.{settings.batches}.h5") as sp:
    k = sp.keff
    print()
    print("=" * 55)
    print(f"  Fuel: {fuel.name}")
    print(f"  k-inf = {k.nominal_value:.5f} +/- {k.std_dev:.5f}")
    print("=" * 55)

# ---------------------------------------------------------------------------
# THINGS TO TRY BEFORE MOVING ON
# ---------------------------------------------------------------------------
# 1. Change TH_FRACTION to 0.95 and 0.80. Which way does k-inf move, and does
#    the direction match what you'd predict from Th-232 absorption?
# 2. Drop enrichment to 5%. How much reactivity do you lose?
# 3. Raise `particles` to 50000. Watch the uncertainty shrink as 1/sqrt(N).
# 4. Comment out the add_s_alpha_beta line and rerun. The size of that error
#    is a good thing to have felt once.
