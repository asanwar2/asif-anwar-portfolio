# Neutronic Assessment of a Thoria-Urania Fuel Bundle in a Pressurized Heavy Water Lattice

**An open-source Monte Carlo study using OpenMC**

Asif Anwar - M.S. Nuclear Engineering, Purdue University


---

## Abstract

A 37-element pressurized heavy water reactor (PHWR) fuel bundle loaded with a
thoria-urania (ThO₂–UO₂) fuel blend was modeled in OpenMC and compared against
a natural-uranium reference of identical geometry. The thoria-urania case used
90 wt% ThO₂ with 10 wt% UO₂ enriched to 19.75% U-235, giving approximately
1.74 wt% fissile content against 0.63 wt% for natural UO₂.

Three results follow. Fresh lattice reactivity increased by only 30.6 mk
(1.13138 → 1.17197 in k∞) despite a 2.8× increase in fissile loading, a
consequence of Th-232's large thermal absorption cross section. Coolant void
reactivity fell from +14.78 ± 0.37 mk to +10.90 ± 0.35 mk, a reduction of
26 ± 3% at 7.6σ significance, though the coefficient remains positive. Bundle
depletion to 59.9 MWd/kgHM showed k∞ crossing unity near 18.5 MWd/kgHM against
roughly 7.5 MWd/kgHM for natural-uranium CANDU fuel, with the reactivity loss
rate flattening from −7.0 to −1.8 mk per MWd/kgHM as U-233 bred in.

The model reproduced four independently known quantities, natural-uranium
CANDU lattice k∞, xenon equilibrium reactivity worth, CANDU bundle heavy-metal
mass, and the sign and magnitude of natural-uranium void reactivity, before
any comparative result was drawn from it.

---

## 1. Introduction

### 1.1 Why thorium

Thorium is roughly three to four times more abundant in the Earth's crust than
uranium and occurs as essentially a single isotope, Th-232. Th-232 is fertile
rather than fissile: it cannot sustain a chain reaction alone, but on capturing
a neutron it becomes Th-233, which beta-decays through Pa-233 (27-day
half-life) to U-233.

U-233 is an attractive thermal fissile isotope. Its reproduction factor η - the
number of fission neutrons released per neutron absorbed - is higher than that
of either U-235 or Pu-239 across most of the thermal energy range, and it stays
comparatively flat with energy. A thorium fuel cycle therefore consumes a
fertile isotope and produces a superior fissile one in place.

The offsetting cost is up front. Th-232's thermal absorption cross section is
about 7.4 barns against U-238's 2.7 barns. Substituting thorium for uranium as
the fertile component means the lattice absorbs neutrons harder from the first
day, and that penalty must be paid for with enrichment before any breeding
benefit is realized. This trade of paying early, collecting late, is the central
economic and neutronic question of any thorium fuel design, and it is the
question this study is built around.

### 1.2 Why a PHWR

Heavy water reactors are unusually well suited to thorium. Deuterium's
absorption cross section is roughly two orders of magnitude below that of
ordinary hydrogen, so a D₂O-moderated lattice has neutrons to spare, enough
economy to sustain a chain reaction on natural uranium at 0.711% enrichment,
which no light water lattice can do. That surplus is precisely what a thorium
cycle needs to absorb the Th-232 penalty.

The CANDU design adds a second advantage: on-power refuelling. Fuel can be
shuffled and replaced without shutting down, which allows a thorium cycle's
slow approach to equilibrium to be managed operationally rather than designed
around.

The relevant industrial context is Clean Core Thorium Energy's ANEEL fuel, a
patented thorium–HALEU blend intended as a drop-in replacement for
natural-uranium fuel in the existing PHWR fleet. Its claimed advantages are
higher burnup, reduced waste volume, and improved coolant void and temperature
coefficients. The composition of ANEEL is proprietary. This study therefore
does not model ANEEL. It models a thoria-urania bundle of the same general
family, using open literature values, to test whether those claimed
directions emerge from first-principles transport calculation.

### 1.3 The coolant void problem

CANDU reactors have a positive coolant void reactivity coefficient. Loss of
coolant from a fuel channel *increases* reactivity rather than decreasing it, which is the opposite of the behavior in a light water reactor, and a long-standing
focus of CANDU safety analysis.

The mechanism is spectral. In a CANDU lattice the coolant and the moderator are
physically separated: hot, low-density D₂O flows inside the pressure tube among
the fuel elements, while cold, dense D₂O fills the calandria outside. Most
moderation happens in the calandria. The coolant contributes only modestly, but
what it does contribute is the last thermalization a neutron receives before
re-entering the fuel.

Remove it and the in-bundle spectrum hardens. Two effects follow. Fast fission
in U-238 increases, adding reactivity. And the epithermal flux rises, shifting
absorption into the resonance region. In natural-uranium fuel the first effect
dominates and the net coefficient is positive.

Substituting Th-232 for most of the U-238 changes both terms. Th-232 has no
appreciable fast fission threshold behavior comparable to U-238's, removing
part of the positive contribution, and its resonance structure captures a
larger share of the upshifted epithermal flux. The prediction is a less
positive coefficient. Testing that prediction is the central objective here.

---

## 2. Objectives

1. Build and verify a 37-element PHWR bundle model in OpenMC.
2. Establish credibility by reproducing known natural-uranium CANDU results
   before drawing any comparative conclusion.
3. Quantify the fresh-lattice reactivity penalty attributable to Th-232
   absorption.
4. Measure coolant void reactivity for thoria-urania and natural-uranium fuel
   in identical geometry.
5. Determine the burnup at which lattice reactivity is exhausted, and
   characterize the U-233 breeding contribution through the shape of the
   reactivity-versus-burnup curve.

---

## 3. Methodology

### 3.1 Code and data

| Item | Selection |
|---|---|
| Transport code | OpenMC (continuous-energy Monte Carlo) |
| Cross-section library | ENDF/B-VIII.0 |
| Thermal scattering | `c_D_in_D2O` applied to coolant and moderator |
| Temperature treatment | Interpolation between tabulated points |
| Depletion chain | ENDF/B-VIII.0, thermal spectrum |
| Depletion integrator | Predictor (first order) |

OpenMC was chosen deliberately over MCNP or Serpent. It is open source, its
Python API makes parameter studies scriptable rather than manual, and the
entire study is reproducible by anyone without a license.

Temperature interpolation warrants a note. The ENDF/B-VIII.0 library tabulates
cross sections at 250, 294, 600, 900, 1200 and 2500 K. Several model
temperatures, notably the 561 K coolant and 342 K moderator, fall between
tabulated points. OpenMC's default nearest-point method rejects gaps beyond
about 10 K rather than silently substituting inappropriate data. Interpolation
was selected as the more physically defensible option; nearest-neighbor
rounding with a widened tolerance would have placed the coolant at 600 K, a
39 K error.

### 3.2 Geometry

Representative CANDU-6 37-element dimensions were used, taken from open
benchmark literature.

| Parameter | Value (cm) |
|---|---|
| Fuel pellet radius | 0.6122 |
| Clad outer radius | 0.6540 |
| Ring radii (0/1/2/3) | 0.0 / 1.4885 / 2.8755 / 4.3305 |
| Elements per ring | 1 / 6 / 12 / 18 |
| Pressure tube inner / outer | 5.1689 / 5.6007 |
| Calandria tube inner / outer | 6.4478 / 6.5875 |
| Lattice pitch (square) | 28.575 |
| Active length | 49.53 |

Ring 2 was given a 15° rotational offset relative to rings 1 and 3, following
standard CANDU element placement.

Geometry was constructed in constructive solid geometry using explicit
`ZCylinder` surfaces at each of the 37 element centers, with the coolant region
formed by successive intersection of the exterior of every clad cylinder. This
is more verbose than a lattice-and-universe construction but is transparent and
difficult to get subtly wrong.

The model is two-dimensional in effect: an infinite square lattice with
reflective boundaries on all four sides, giving k-infinity with zero leakage.

**Geometry verification.** Three independent checks were applied.

1. An assertion confirmed 37 pin positions were generated.
2. A material-colored plot was rendered and inspected. All seven material
   regions were visually distinct and correctly ordered from the center
   outward, with the coolant and moderator clearly differentiated, the
   physical separation that defines PHWR neutronics.
3. `openmc.run(geometry_debug=True)` reported zero cells with insufficient
   overlap checks, confirming no CSG regions intersect.

**Dimensional verification.** The modeled fuel volume of 2,157.8 cm³ at a
mixture density of 10.048 g/cm³ and heavy-metal mass fraction of 0.879 gives
19.06 kg of heavy metal per bundle. A real CANDU-6 bundle contains
approximately 19.1 kg. This agreement emerges from the dimensions and densities independently and is strong evidence the geometry is dimensionally correct.

### 3.3 Materials

**Thoria-urania fuel.** 90 wt% ThO₂ (10.0 g/cm³) blended with 10 wt% UO₂
enriched to 19.75% U-235 (10.5 g/cm³), giving a mixture density of
10.048 g/cm³ and 1.74 wt% fissile content. The 19.75% figure is the upper
bound of the HALEU range, consistent with public descriptions of ANEEL as a
thorium-HALEU fuel.

**Natural uranium reference.** UO₂ at 0.711% enrichment, 10.6 g/cm³, giving
0.63 wt% fissile.

| Component | Material | Density (g/cm³) | Temperature (K) |
|---|---|---|---|
| Fuel | ThO₂–UO₂ or natural UO₂ | 10.048 / 10.6 | 900 |
| Cladding | Zircaloy-4 | 6.55 | 600 |
| Coolant | D₂O | 0.807 | 561 |
| Moderator | D₂O | 1.0851 | 342 |
| Pressure tube | Zr-2.5Nb | 6.57 | 561 |
| Annulus gas | CO₂ | 0.0014 | 450 |
| Calandria tube | Zircaloy-2 | 6.55 | 400 |

The coolant/moderator density and temperature difference is the defining feature of the lattice and drives the void reactivity result in Section 4.3.

### 3.4 Simulation parameters

| Study | Particles | Batches | Inactive |
|---|---|---|---|
| Moderation scan (pin cell) | 5,000 | 100 | 20 |
| Fresh bundle reactivity | 20,000 | 150 | 30 |
| Coolant void reactivity | 30,000 | 200 | 40 |
| Depletion | 10,000 | 100 | 20 |

Void reactivity received the highest particle count because it is computed as a
small difference between two large quantities, where statistical error
propagates unfavorably. Inactive batches were raised to 40 for the same study
because voiding the coolant alters the fission source distribution and slows
source convergence.

### 3.5 Depletion setup

Depletion was driven at 25 W per gram of heavy metal, corresponding to 476 kW
per bundle, within the normal CANDU bundle power range. Fourteen burnup steps
were used, fine early (0.1 MWd/kgHM) to resolve xenon and samarium equilibrium
and coarse later (10 MWd/kgHM), reaching 59.9 MWd/kgHM total.

The integrator reported a total irradiation time of 2.070 × 10⁸ seconds, or
2,396 days. Computed independently from 59.9 MWd/kgHM × 19.059 kgHM ÷ 476.5 kW,
the expected value is 2,396 days, exact agreement, confirming the power
normalization and heavy-metal mass are mutually consistent.

All 37 elements share a single fuel material, so depletion is bundle-averaged
rather than ring-wise. See Section 6 for the consequences.

---

## 4. Results

### 4.1 Moderation study

A single-pin cell was run at ten lattice pitches to characterize the
moderator-to-fuel ratio dependence.

| Pitch (cm) | k∞ | σ |
|---|---|---|
| 1.6 | 0.42824 | 0.00086 |
| 2.5 | 0.75619 | 0.00117 |
| 4.0 | 1.04604 | 0.00107 |
| 6.0 | 1.19707 | 0.00145 |
| 8.0 | 1.25518 | 0.00124 |
| 12.0 | 1.29498 | 0.00129 |
| 16.0 | **1.29648** | 0.00132 |
| 20.0 | 1.29244 | 0.00125 |
| 25.0 | 1.27164 | 0.00111 |
| 30.0 | 1.25092 | 0.00124 |

The curve rises steeply through the under-moderated region, peaks near 14–16 cm
at k∞ ≈ 1.296, and declines slowly thereafter. The peak is exceptionally flat:
the 12, 16, and 20 cm points span only 0.004 in k∞, roughly three standard
deviations.

Two features are worth drawing out.

**The asymmetry is the point.** Under-moderation is punishing, going from
16 cm down to 1.6 cm costs more than 0.86 in k∞. Over-moderation is nearly
free: 16 cm to 30 cm costs only 0.046, about 45 mk in reactivity. In a light
water lattice, over-moderation would be penalized far more heavily, because
every additional H atom is an absorber. Deuterium is not. This asymmetry is the
same property that lets CANDU run on natural uranium.

**The real lattice sits past the peak.** CANDU-6 pitch is 28.575 cm, well into
the over-moderated region, giving up roughly 40 mk relative to the optimum.
That is a deliberate design choice, not an oversight. Operating over-moderated
provides physical space between channels for the calandria tube and reactivity
control devices, flattens the flux across the core, and yields more favorable
moderator temperature feedback. When fuel is cheap and neutrons are plentiful,
buying those properties for a few tens of mk is a sound trade.

*Caveat: this is a single-pin cell, so the optimum found here is not the
bundle's optimum. It is also an infinite lattice with no leakage; in a finite
core, leakage penalizes large pitch more heavily and would shift the practical
optimum tighter.*

### 4.2 Fresh lattice reactivity

Identical bundle geometry, two fuels.

| Fuel | Fissile (wt%) | k∞ | ρ (mk) |
|---|---|---|---|
| Natural UO₂ | 0.63 | 1.13138 ± 0.00052 | 116.1 |
| Thoria-urania | 1.74 | 1.17197 ± 0.00056 | 146.7 |
| **Difference** | **2.8×** | | **+30.6** |

**Validation.** The natural-uranium result of 1.131 falls within the published
range for fresh CANDU lattice k∞. This is the study's primary credibility
check: a well-established quantity, reproduced in the same geometry and code
path used for every subsequent result.

**Interpretation.** A 2.8-fold increase in fissile loading purchased only
30.6 mk. This is the Th-232 absorption penalty made quantitative, and it is the
single most important number for understanding why ANEEL requires HALEU rather
than conventional LEU. Nearly all of the additional enrichment is consumed
offsetting the fertile substitution rather than adding reactivity.

Read in isolation, this looks like a poor trade. Section 4.4 shows why it is
not.

### 4.3 Coolant void reactivity

Coolant density was reduced from 0.807 g/cm³ to 10⁻⁴ g/cm³, effectively
voided, though not identically zero, which avoids numerical difficulty.
Reactivity is ρ = (k−1)/k, and CVR = ρ(voided) − ρ(nominal).

| Fuel | k (nominal) | k (voided) | ρ nom (mk) | ρ void (mk) | CVR (mk) |
|---|---|---|---|---|---|
| Natural UO₂ | 1.13235 | 1.15163 | 116.88 | 131.67 | **+14.78 ± 0.37** |
| Thoria-urania | 1.17245 | 1.18763 | 147.09 | 157.99 | **+10.90 ± 0.35** |

**Difference: 3.88 ± 0.51 mk — a 26 ± 3% reduction, significant at 7.6σ.**

**Validation.** Two checks passed. The natural-uranium nominal case gave
1.13235 against 1.13138 from the independent Section 4.2 run, a 1.3σ
difference, consistent with Monte Carlo noise between different random seeds.
And +14.78 mk for fresh natural-uranium CANDU fuel is both positive, as the
literature requires, and of the expected magnitude. Reported leakage fraction
was identically zero, as reflective boundaries demand.

**Interpretation.** The predicted direction is confirmed with high statistical
confidence. Substituting Th-232 for most of the U-238 reduces the reactivity
gain on voiding by roughly a quarter, consistent with the spectral argument in
Section 1.3: less positive fast-fission contribution, and more resonance
capture of the upshifted epithermal flux.

**The coefficient remains positive.** This must not be overstated.
Thoria-urania fuel reduces coolant void reactivity in this lattice; it does not
eliminate it, and it does not change its sign. The safety characteristic is
improved, not removed.

*Caveat: this is fresh fuel only. CANDU void reactivity typically worsens with
burnup as plutonium accumulates, and mid-cycle void behavior governs the actual
safety case. See Section 7.*

### 4.4 Depletion

Thoria-urania bundle depleted to 59.9 MWd/kgHM at 25 W/gHM.

| Burnup (MWd/kgHM) | k∞ | σ | ρ (mk) |
|---|---|---|---|
| 0.00 | 1.17215 | 0.00092 | 146.87 |
| 0.10 | 1.13499 | 0.00081 | 118.94 |
| 0.40 | 1.12085 | 0.00094 | 107.82 |
| 0.90 | 1.11013 | 0.00080 | 99.20 |
| 1.90 | 1.09768 | 0.00090 | 88.99 |
| 2.90 | 1.08876 | 0.00077 | 81.52 |
| 4.90 | 1.07653 | 0.00088 | 71.09 |
| 7.40 | 1.05943 | 0.00089 | 56.10 |
| 9.90 | 1.04566 | 0.00085 | 43.67 |
| 14.90 | 1.01754 | 0.00084 | 17.24 |
| 19.90 | 0.99351 | 0.00077 | −6.53 |
| 29.90 | 0.96407 | 0.00088 | −37.27 |
| 39.90 | 0.94361 | 0.00082 | −59.76 |
| 49.90 | 0.92797 | 0.00083 | −77.62 |
| 59.90 | 0.91621 | 0.00088 | −91.45 |

**k∞ crosses unity at approximately 18.5 MWd/kgHM** (linear interpolation
between the 14.90 and 19.90 points).

Three features, each physically meaningful.

**Xenon transient.** The first step costs 27.9 mk. Equilibrium Xe-135 worth in
a thermal reactor is typically 25–30 mk, so this is the expected magnitude —
a third independent validation, and one that emerges from the depletion solver
rather than the transport solver.

**Slope flattening.** The reactivity loss rate decreases monotonically:

| Burnup range (MWd/kgHM) | Slope (mk per MWd/kgHM) |
|---|---|
| 0.9 – 4.9 | −7.03 |
| 4.9 – 19.9 | −5.17 |
| 29.9 – 59.9 | −1.81 |

This is the thorium cycle visible in the data. Early on, fissile U-235 depletes
faster than U-233 breeds in. As Th-232 capture accumulates Pa-233 and it decays
through to U-233, the bred fissile increasingly offsets the loss. By the far
end of the curve, production and consumption are approaching balance and the
reactivity decline has slowed nearly fourfold.

**Discharge burnup.** 18.5 MWd/kgHM against approximately 7.5 MWd/kgHM for
natural-uranium CANDU, a factor of about 2.5.

---

## 5. Discussion

### 5.1 What the fissile investment actually bought

Placing the results side by side gives a sharper reading than any one of them
alone.

| Quantity | Ratio, thoria-urania to natural U |
|---|---|
| Fissile loading | 2.8× |
| Discharge burnup | ~2.5× |
| Fresh reactivity | +30.6 mk only |

The burnup gain is approximately proportional to the fissile investment. This
is the honest framing, and it is the one most likely to be probed: **most of
the higher burnup demonstrated here is bought with enrichment and not conjured by
thorium.** A straightforward LEU-in-CANDU case at matched fissile content would
likely achieve comparable or greater burnup, because it would not pay the
Th-232 absorption penalty.

Thorium's distinctive contributions are elsewhere, and this study captures two
of them: the reduced void coefficient (Section 4.3), and the flattening
reactivity slope (Section 4.4) that signals in-situ fissile production. A
matched-enrichment LEU comparison would isolate these properly and is the
highest-priority extension of this work.

### 5.2 On the coolant void result

Of the results here, this is the most defensible and the most useful. It is a
controlled comparison with identical geometry, identical code path, identical
statistical treatment, and one variable changed, with a 7.6σ separation and a
validated reference case. It does not depend on the depletion chain, on the
power normalization, or on the burnup schedule.

It is also fresh-fuel only, which is its principal limitation rather than a
minor caveat. The void coefficient at mid-burnup is what safety analysis
actually turns on.

### 5.3 On the discharge burnup figure

18.5 MWd/kgHM is an infinite-lattice quantity with zero leakage, no reactivity
control devices, and no refuelling ripple. A real core must hold excess
reactivity to cover all three, so an actual bundle-averaged discharge burnup
would be meaningfully lower.

The figure should be presented as a lattice-level indicator, and the ratio to
the natural-uranium reference is more meaningful than the absolute value.

---

## 6. Limitations

Stated plainly, in rough order of significance.

1. **Fuel composition is a stand-in.** ANEEL's actual thoria/urania ratio,
   enrichment, and burnable absorber loading are proprietary. The 90/10 blend
   at 19.75% is constructed from open literature on thoria-urania PHWR fuel.
   No claim about ANEEL specifically follows from these results.

2. **No burnable absorber is modeled.** ANEEL is publicly described as
   incorporating one. Its absence inflates fresh reactivity and distorts the
   early shape of the burnup curve.

3. **No natural-uranium depletion reference.** The 18.5 MWd/kgHM figure is
   compared against a literature value rather than against the same model. This
   is the single largest gap in the study and the easiest to close, with one run of
   the existing script with the fuel switched.

4. **Bundle-averaged depletion.** All 37 elements share one fuel material, so
   all deplete identically. In reality the outer ring sees substantially higher
   thermal flux and depletes faster, which flattens the bundle's aggregate
   reactivity curve relative to what a ring-wise model would produce.

5. **First-order integrator with coarse late steps.** Predictor-only
   integration with 10 MWd/kgHM steps accumulates truncation error. A
   predictor-corrector scheme (CE/CM) would be more accurate for the same
   number of transport solves.

6. **PWR-oriented depletion chain.** The thermal chain is built around a
   U-235/Pu-239 fission product yield set. It tracks the relevant actinides
   including Pa-233, but fission product yields for U-233 fission are not
   tailored. The effect on k∞ is likely modest but is not quantified.

7. **Two-dimensional, infinite, no leakage.** No axial effects, no core-level
   flux shape, no control devices.

8. **No thermal feedback.** Fixed temperatures throughout; no coupling between
   power, fuel temperature, and coolant density.

9. **Single nuclear data library.** No sensitivity or uncertainty analysis on
   cross-section data, which for Th-232 and U-233 carries larger uncertainty
   than for U-235 and U-238.

10. **Source convergence not formally verified.** Shannon entropy was not
    monitored. Given the small, symmetric, reflected geometry, source
    convergence is expected to be rapid, but it was not demonstrated.

---

## 7. Future work

In priority order.

1. **Natural-uranium depletion run.** Closes limitation 3 and yields the
   two-curve comparison figure this study is missing. One run.

2. **Void reactivity versus burnup.** Restart void calculations from depleted
   compositions at several burnup points. This addresses the most substantive
   limitation of the Section 4.3 result and is the question a fuel physicist
   would ask first.

3. **Matched-enrichment LEU comparison.** Run LEU-in-CANDU at 1.74% fissile
   to isolate thorium's contribution from enrichment's. Directly tests the
   Section 5.1 argument.

4. **Ring-wise depletion.** Assign independent materials to each ring to
   capture the radial burnup gradient.

5. **Fuel temperature coefficient.** Perturb fuel temperature across the
   tabulated library points and evaluate Doppler feedback for both fuels.
   Th-232's resonance structure differs from U-238's and the comparison is
   directly relevant to safety.

6. **Blend ratio parameter study.** Sweep ThO₂ fraction and enrichment to map
   the design space rather than sampling one point in it.

---

## 8. Conclusions

A 37-element PHWR bundle model was built in OpenMC and verified against four
independent known variables: natural-uranium lattice k∞ (1.131), xenon equilibrium
worth (27.9 mk), CANDU bundle heavy-metal mass (19.06 kg), and the sign and
magnitude of natural-uranium coolant void reactivity (+14.78 mk). 

Substituting a 90/10 thoria-urania blend at 19.75% enrichment for natural
uranium raised fresh lattice reactivity by only 30.6 mk despite a 2.8×
increase in fissile loading, quantifying the Th-232 absorption penalty and
explaining the HALEU requirement. Coolant void reactivity fell from +14.78 ± 0.37 mk to +10.90 ± 0.35 mk, a 26 ± 3% reduction significant at 7.6σ. The coefficient remains positive. Depletion to 59.9 MWd/kgHM gave a k∞ = 1 crossing near 18.5 MWd/kgHM, approximately 2.5× the natural-uranium CANDU value, with the reactivity loss rate flattening from −7.0 to −1.8 mk per MWd/kgHM as U-233 bred in.

The burnup gain is approximately proportional to the fissile investment, so
it should not be attributed to thorium alone. The reduced void coefficient
and the flattening reactivity slope are the results more properly
attributable to the thorium cycle itself.

---

## Appendix A: Reproducibility

All code is plain Python against the OpenMC API. Complete environment:

```bash
conda create --name openmc-env openmc
conda activate openmc-env
export OPENMC_CROSS_SECTIONS=/path/to/endfb-viii.0-hdf5/cross_sections.xml
```

| File | Purpose |
|---|---|
| `01_pincell.py` | Single-pin moderation study |
| `02_bundle.py` | 37-element bundle, fresh reactivity, geometry plot |
| `bundle_model.py` | Shared geometry and material definitions |
| `03_void_reactivity.py` | Four-case void reactivity comparison |
| `04_deplete.py` | Bundle depletion and post-processing |

Runtime on a consumer laptop: seconds for the pin cell, minutes for the fresh
bundle, approximately 40 minutes for the void study, and several hours for
depletion.

---

## Appendix B: Anticipated questions

Questions a reviewer is likely to raise, with the answers this study supports.

**"Your void coefficient is still positive — didn't thorium fix that?"**
No, and the study does not claim it did. The coefficient dropped 26%, from
+14.78 to +10.90 mk. It remains positive. Reduction of an adverse coefficient
is a real improvement; elimination would be a different and much stronger
claim that this work does not support.

**"How do you know your model is right?"**
Four independent checks, all passed before any comparative result was drawn:
natural-uranium k∞ of 1.131 against the published range; xenon equilibrium
worth of 27.9 mk against the expected 25–30; heavy-metal mass of 19.06 kg
against a real CANDU bundle's 19.1; and positive natural-uranium void
reactivity of the right magnitude. The geometry also passed OpenMC's overlap
checker and visual inspection.

**"Isn't the higher burnup just from the enrichment?"**
Largely, yes, and that is stated in Section 5.1. Fissile loading rose 2.8×
and burnup rose about 2.5×, so the gain is roughly proportional. A
matched-enrichment LEU comparison is needed to isolate thorium's contribution
and has not been run. Thorium's distinctive effects visible here are the
reduced void coefficient and the flattening reactivity slope.

**"Why OpenMC rather than MCNP or Serpent?"**
Open source, scriptable through a Python API which made the parameter studies
practical, and fully reproducible by anyone without a license. Prior lattice
depletion experience with Serpent and HELIOS informed the model setup.

**"Is this ANEEL?"**
No. ANEEL's composition is proprietary. This is a thoria-urania bundle of the
same general family, built from open literature values, used to test whether
the publicly claimed directional benefits emerge from transport calculation.

**"What's the biggest weakness?"**
The absence of a natural-uranium depletion run in the same model, which leaves
the burnup comparison resting on a literature value rather than an internal
reference. Second is that void reactivity was evaluated only at zero burnup,
when mid-cycle behavior governs the actual safety case.

**"Why is the discharge burnup an infinite-lattice number?"**
Because the model is a reflected single lattice cell with zero leakage and no
reactivity devices. A real core holds excess reactivity for leakage, control,
and refuelling ripple, so actual discharge burnup would be lower. The ratio to
the natural-uranium reference is the meaningful comparison, not the absolute
figure.

**"What would you do next?"**
The natural-uranium depletion run, then void reactivity as a function of
burnup. The second is the question that most needs answering.
