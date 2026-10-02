"""
Stage 2: a 37-element PHWR/CANDU fuel bundle in a lattice cell.

This is the real geometry: 37 pins in concentric rings (1 + 6 + 12 + 18),
inside a pressure tube, a CO2 gas annulus, a calandria tube, and cool heavy
water moderator.

Two things make CANDU physics different from a PWR and both show up here:
  - the moderator is separate from the coolant and much colder
  - the coolant is a small part of the moderation, which is why voiding it
    does something surprising (see script 03)

Run:  python 02_bundle.py

NOTE ON THE DIMENSIONS BELOW: these are representative CANDU-6 37-element
values from open benchmark literature. Verify them against a published
source before you put any number in front of a reactor physicist. Good
starting point: the IAEA CANDU-6 benchmark documentation, or Rouben's
CANDU course notes.
"""

import math
import openmc

# ---------------------------------------------------------------------------
# DIMENSIONS (cm)
# ---------------------------------------------------------------------------
R_FUEL = 0.6122          # pellet radius
R_CLAD = 0.6540          # clad outer radius

RING_RADII = [0.0, 1.4885, 2.8755, 4.3305]   # ring center-to-center radii
RING_COUNTS = [1, 6, 12, 18]                 # pins per ring
RING_OFFSETS = [0.0, 0.0, 15.0, 0.0]         # deg, rotational offset per ring

R_PT_IN = 5.1689         # pressure tube inner
R_PT_OUT = 5.6007        # pressure tube outer
R_CT_IN = 6.4478         # calandria tube inner
R_CT_OUT = 6.5875        # calandria tube outer

LATTICE_PITCH = 28.575   # square lattice pitch

# ---------------------------------------------------------------------------
# MATERIALS
# ---------------------------------------------------------------------------
TH_FRACTION = 0.90

thoria = openmc.Material(name="ThO2")
thoria.add_element("Th", 1.0)
thoria.add_element("O", 2.0)
thoria.set_density("g/cm3", 10.0)

urania = openmc.Material(name="UO2 HALEU")
urania.add_element("U", 1.0, enrichment=19.75)
urania.add_element("O", 2.0)
urania.set_density("g/cm3", 10.5)

fuel = openmc.Material.mix_materials(
    [thoria, urania], [TH_FRACTION, 1.0 - TH_FRACTION], "wo"
)
fuel.name = "Thoria-urania fuel"
fuel.temperature = 900.0

# --- Reference case for comparison: natural uranium, the CANDU standard ---
nu_fuel = openmc.Material(name="Natural UO2")
nu_fuel.add_element("U", 1.0, enrichment=0.711)
nu_fuel.add_element("O", 2.0)
nu_fuel.set_density("g/cm3", 10.6)
nu_fuel.temperature = 900.0

# Switch this to nu_fuel to run the natural-uranium reference case.
ACTIVE_FUEL = fuel

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
coolant.set_density("g/cm3", 0.807)
coolant.add_s_alpha_beta("c_D_in_D2O")
coolant.temperature = 561.0

# Moderator is much colder and denser than the coolant. That separation is
# the defining feature of a CANDU lattice.
moderator = openmc.Material(name="D2O moderator")
moderator.add_nuclide("H2", 2.0)
moderator.add_element("O", 1.0)
moderator.set_density("g/cm3", 1.0851)
moderator.add_s_alpha_beta("c_D_in_D2O")
moderator.temperature = 342.0

pressure_tube = openmc.Material(name="Zr-2.5Nb pressure tube")
pressure_tube.add_element("Zr", 0.975, "wo")
pressure_tube.add_element("Nb", 0.025, "wo")
pressure_tube.set_density("g/cm3", 6.57)
pressure_tube.temperature = 561.0

annulus_gas = openmc.Material(name="CO2 annulus gas")
annulus_gas.add_element("C", 1.0)
annulus_gas.add_element("O", 2.0)
annulus_gas.set_density("g/cm3", 0.0014)
annulus_gas.temperature = 450.0

calandria_tube = openmc.Material(name="Zircaloy-2 calandria tube")
calandria_tube.add_element("Zr", 0.982, "wo")
calandria_tube.add_element("Sn", 0.015, "wo")
calandria_tube.add_element("Fe", 0.002, "wo")
calandria_tube.add_element("Cr", 0.001, "wo")
calandria_tube.set_density("g/cm3", 6.55)
calandria_tube.temperature = 400.0

openmc.Materials([
    ACTIVE_FUEL, clad, coolant, moderator,
    pressure_tube, annulus_gas, calandria_tube,
]).export_to_xml()


# ---------------------------------------------------------------------------
# GEOMETRY
# ---------------------------------------------------------------------------
def pin_positions():
    """Return (x, y) for all 37 element centers."""
    coords = []
    for radius, count, offset in zip(RING_RADII, RING_COUNTS, RING_OFFSETS):
        if count == 1:
            coords.append((0.0, 0.0))
            continue
        for i in range(count):
            angle = math.radians(offset + i * 360.0 / count)
            coords.append((radius * math.cos(angle), radius * math.sin(angle)))
    return coords


positions = pin_positions()
assert len(positions) == 37, f"expected 37 pins, built {len(positions)}"

cells = []
coolant_region = -openmc.ZCylinder(r=R_PT_IN)   # start with the whole channel

# Each pin gets its own cylinders at its own (x, y). Verbose, but explicit and
# hard to get subtly wrong — worth it while you're learning.
fuel_cells = []
for idx, (x, y) in enumerate(positions):
    fuel_surf = openmc.ZCylinder(x0=x, y0=y, r=R_FUEL)
    clad_surf = openmc.ZCylinder(x0=x, y0=y, r=R_CLAD)

    fc = openmc.Cell(name=f"fuel_{idx}", fill=ACTIVE_FUEL, region=-fuel_surf)
    cc = openmc.Cell(name=f"clad_{idx}", fill=clad,
                     region=+fuel_surf & -clad_surf)

    fuel_cells.append(fc)
    cells.extend([fc, cc])

    # Carve this pin out of the coolant region
    coolant_region &= +clad_surf

cells.append(openmc.Cell(name="coolant", fill=coolant, region=coolant_region))

# Channel structure
pt_in = openmc.ZCylinder(r=R_PT_IN)
pt_out = openmc.ZCylinder(r=R_PT_OUT)
ct_in = openmc.ZCylinder(r=R_CT_IN)
ct_out = openmc.ZCylinder(r=R_CT_OUT)

box = openmc.model.RectangularPrism(
    width=LATTICE_PITCH, height=LATTICE_PITCH, boundary_type="reflective"
)

cells += [
    openmc.Cell(name="pressure_tube", fill=pressure_tube,
                region=+pt_in & -pt_out),
    openmc.Cell(name="annulus", fill=annulus_gas, region=+pt_out & -ct_in),
    openmc.Cell(name="calandria_tube", fill=calandria_tube,
                region=+ct_in & -ct_out),
    openmc.Cell(name="moderator", fill=moderator, region=+ct_out & -box),
]

geometry = openmc.Geometry(cells)
geometry.export_to_xml()

# ---------------------------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------------------------
settings = openmc.Settings()
settings.batches = 150
settings.inactive = 30
settings.particles = 20000
settings.source = openmc.IndependentSource(
    space=openmc.stats.Box((-4.5, -4.5, -1), (4.5, 4.5, 1), only_fissionable=True)
)
settings.temperature = {"method": "interpolation"}
settings.export_to_xml()

# ---------------------------------------------------------------------------
# PLOT — always look at your geometry before trusting a number from it
# ---------------------------------------------------------------------------
plot = openmc.Plot()
plot.filename = "bundle"
plot.width = (LATTICE_PITCH, LATTICE_PITCH)
plot.pixels = (1200, 1200)
plot.color_by = "material"
openmc.Plots([plot]).export_to_xml()
openmc.plot_geometry()
print("Wrote bundle.png — open it and count 37 pins before going further.")

# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
openmc.run()

with openmc.StatePoint(f"statepoint.{settings.batches}.h5") as sp:
    k = sp.keff
    print()
    print("=" * 55)
    print(f"  Fuel:  {ACTIVE_FUEL.name}")
    print(f"  k-inf = {k.nominal_value:.5f} +/- {k.std_dev:.5f}")
    print("=" * 55)

# ---------------------------------------------------------------------------
# WHAT TO DO WITH THIS
# ---------------------------------------------------------------------------
# Run it once with ACTIVE_FUEL = fuel, once with ACTIVE_FUEL = nu_fuel.
# Natural-uranium CANDU fresh k-inf should land somewhere around 1.1.
# If your reference case is wildly off that, your geometry or your moderator
# treatment is wrong — fix it before you trust the thoria case.
