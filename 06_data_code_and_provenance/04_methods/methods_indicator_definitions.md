# Methods Indicator Definitions

## Quantity Boundary Across the Two Evidence Layers

The bundle preserves two related but non-identical evidence layers.

- **ERA5 main analysis** uses *vertical diagnostic differences* between the 100 m and 10 m layers for occupancy, persistence, connected-structure, percolation-style, and anisotropy diagnostics.
- **Paris DWL validation** uses directly observed 100-300 m and 200-500 m wind-profile gradients and direction contrasts from independent Doppler-wind-lidar profiles.

The ERA5 layer should therefore be described as a diagnostic-difference framework rather than as a direct `|U100 - U10|` speed-difference analysis.

## Core Cross-height Diagnostic Differences

- `vd_occ = critical_band_occupancy_100m - critical_band_occupancy_10m`
- `vd_persistence = corridor_persistence_index_100m - corridor_persistence_index_10m`
- `vd_largest_frac = HIGH_largest_frac_100m - HIGH_largest_frac_10m`
- `vd_pc = p_c_S_100m - p_c_S_10m`
- `vd_anis = HIGH_pca_anisotropy_100m - HIGH_pca_anisotropy_10m`

Source: `code/core/low_altitude_boundary_layer_event_diagnostics_from_dynamics_v2.py`.

## Occupancy

- `critical_band_occupancy` is the fraction of valid internal city-grid points falling inside the phase-space critical band, implemented as `mean((W >= W_thr) & support_ok)`.
- Source: `compute_city_critical_band_occupancy()` in `code/core/low_altitude_safety_corridor_dynamics_pipeline_v2.py`.

## Persistence

- `corridor_persistence_index = cp0_max / sum(pers0)` where `pers0` are H0 persistence lifetimes from the corridor backbone and `cp0_max` is the maximum retained H0 persistence.
- Current pipeline defaults: `persistence_min_mode = quantile`, `persistence_min_value = 0.50`.
- Source: `corridor_ph_backbone()` in `code/core/low_altitude_safety_corridor_dynamics_pipeline_v2.py`.

## Largest Connected Fraction (LCF)

- `largest_frac = largest_component_size / total_active_area` for the binary corridor mask.
- Source: `corridor_topology_metrics()` in `code/core/low_altitude_safety_corridor_dynamics_pipeline_v2.py`.

## Regime Thresholds Used in the Current Pipeline Defaults

- Day window: `08:00-18:00` local-hour mask.
- `stable_like`: night + BLH <= monthly 30th percentile.
- `unstable_like`: day + BLH >= monthly 70th percentile.
- `shear_weak`: monthly shear <= 30th percentile.
- `shear_moderate`: monthly shear between 30th and 90th percentiles.
- `shear_extreme`: monthly shear >= 90th percentile.
- `gust_high`: monthly gust >= 70th percentile.
- `gust_extreme`: monthly gust >= 90th percentile.
- `stable_shear_high`: `stable_like` AND shear >= 70th percentile.
- `gust_shear_compound`: gust >= 90th percentile AND shear >= 90th percentile.

Source: `compute_state_mask_for_month()` in `code/core/low_altitude_safety_corridor_dynamics_pipeline_v2.py`.

## Hotspot Logic

- Within complete-case city-state-response rows, define `abs_occ = abs(vd_occ)` and `abs_per = abs(vd_persistence)`.
- Thresholds: `thr_occ = Q80(abs_occ)`, `thr_per = Q80(abs_per)`.
- Bin BLH and shear into 5x5 quantile cells; within each valid cell compute `joint_hotspot_ratio = mean((abs_occ >= thr_occ) & (abs_per >= thr_per))`.
- Valid cells require `n >= 6`.
- Structural hotspot cells are the upper 20% of valid `joint_hotspot_ratio` cells (`cell_thr = Q80(joint_hotspot_ratio)`).
- The preserved hotspot-membership table in this bundle is an 11-city complete-case subset linked to the broader analysis through `01_city_domain/analysis_city_selection_manifest.csv`.

Source: `define_hotspot_membership()` in `code/figures/topjournal_boundary_layer_mainstory_v10.py`.

## Bulk Wind Intensity

- In the SMII layer, `wind_intensity_mean = mean(gust_mean, wind10_mean, wind100_mean)`.
- `wind_intensity_z = zscore(wind_intensity_mean)` across the preserved city-state-response cells.

Source: `upgrade/smii_core_mechanism_20260514/build_smii_core_mechanism.py`.

## SMII Forms

- `mixing_deficit_z = -z(log(1 + BLH))`
- `shear_to_mixing_log_z = z(log(1 + shear_mean / BLH))`
- `smii_z = mixing_deficit_z + shear_to_mixing_log_z`
- `smii_simple_z = z(shear_mean) - z(log(1 + BLH))`

The manuscript should treat SMII as a bounded diagnostic rather than a universal closure law.
