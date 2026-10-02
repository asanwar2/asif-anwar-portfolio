# Thoria-Urania PHWR Fuel Bundle Neutronics (OpenMC)

Monte Carlo study of a 37-element CANDU fuel bundle loaded with a thoria-urania
(ThO₂–UO₂) blend, compared against a natural-uranium reference of identical
geometry. Built with OpenMC and ENDF/B-VIII.0 continuous-energy nuclear data.

The question: does a thorium-based fuel actually improve a pressurized heavy
water reactor's coolant void coefficient, and does it reach higher burnup?

## Results

| Quantity | Natural UO₂ | Thoria-urania |
|---|---|---|
| Fissile content | 0.63 wt% | 1.74 wt% |
| Fresh k∞ | 1.13138 ± 0.00052 | 1.17197 ± 0.00056 |
| Coolant void reactivity | +14.78 ± 0.37 mk | +10.90 ± 0.35 mk |
| k∞ = 1 burnup | ~7.5 MWd/kgHM (literature) | 18.5 MWd/kgHM |

**Coolant void reactivity fell by 26 ± 3%, significant at 7.6σ.** The
coefficient remains positive — reduced, not eliminated.

**Fresh reactivity rose only 30.6 mk despite a 2.8× increase in fissile
loading.** That gap is the Th-232 absorption penalty made quantitative, and it
is why a thorium PHWR fuel needs HALEU rather than conventional LEU.

**Reactivity loss rate flattened from −7.0 to −1.8 mk per MWd/kgHM** across the
burnup curve as Th-232 → Pa-233 → U-233 bred fissile material in place.

## Validation

Four independently known quantities were reproduced before any comparative
result was drawn from the model:

| Check | Model | Reference |
|---|---|---|
| Natural-U lattice k∞ | 1.131 | published CANDU range |
| Xenon equilibrium worth | 27.9 mk | 25–30 mk typical |
| Bundle heavy-metal mass | 19.06 kg | ~19.1 kg (CANDU-6) |
| Natural-U void reactivity | +14.78 mk | positive, right magnitude |

The heavy-metal mass was not fitted, it falls out of the modeled dimensions
and densities. Geometry also passed OpenMC's cell-overlap checker and visual
inspection of a material-colored plot.

## Files

| File | Purpose |
|---|---|
| `01_pincell.py` | Single-pin moderation study across 10 lattice pitches |
| `02_bundle.py` | 37-element bundle, fresh reactivity, geometry plot |
| `bundle_model.py` | Shared geometry and material definitions |
| `03_void_reactivity.py` | Four-case coolant void reactivity comparison |
| `04_deplete.py` | Bundle depletion to 59.9 MWd/kgHM, post-processing |
| `REPORT.md` | Full write-up: methodology, data, discussion, limitations |
| `00_SETUP_WALKTHROUGH.md` | Environment setup from scratch |

`bundle_model.py` is a module; scripts 03 and 04 import it.

## Running it

```bash
conda create --name openmc-env openmc
conda activate openmc-env
export OPENMC_CROSS_SECTIONS=/path/to/endfb-viii.0-hdf5/cross_sections.xml
python 01_pincell.py
```

Cross-section data and the depletion chain are not in this repository.
Download both from <https://openmc.org/data/> - ENDF/B-VIII.0 under Official
Data Libraries, and the thermal-spectrum chain under Depletion Chains.

Runtimes on a consumer laptop: seconds for the pin cell, minutes for the fresh
bundle, ~40 minutes for the void study, several hours for depletion.

## Scope and limitations

The fuel composition is a stand-in constructed from open literature on
thoria-urania PHWR fuel: 90 wt% ThO₂ with 10 wt% UO₂ at 19.75% enrichment.
It is not any proprietary commercial composition, and no claim about a specific
commercial fuel follows from these results.

The burnup gain is roughly proportional to the fissile investment (2.8× fissile,
~2.5× burnup), so it should not be attributed to thorium alone. A
matched-enrichment LEU comparison would be needed to isolate thorium's
contribution, and has not been run.

Ten model limitations are documented in [REPORT.md](REPORT.md), including the
absence of a burnable absorber, bundle-averaged rather than ring-wise depletion,
and void reactivity evaluated only at zero burnup.
