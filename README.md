# BLH-shear mismatch low-altitude corridors: Urban Climate release

This repository contains the derived data tables and portable scripts needed to
reproduce the manuscript figures from figure-ready inputs.

## Contents

- `06_data_code_and_provenance/figure_source_data/`: source tables and scripts for Figures 1, 3 and 4.
- `06_data_code_and_provenance/smii_core/tables/`: source tables for the SMII diagnostic and model benchmarks.
- `06_data_code_and_provenance/paris_dwl_validation/tables/`: derived Paris Doppler wind lidar validation tables.
- `06_data_code_and_provenance/scripts/build_urbanclimate_fig2_fig5_v1.py`: portable script for Figures 2 and 5.
- `06_data_code_and_provenance/01_city_domain/`: city-domain and analysis-selection manifests.

The release does not redistribute complete upstream ERA5 archives, complete raw
Paris Doppler wind lidar files, credentials, local working directories or
intermediate caches. Upstream public datasets retain their original licenses.

## Quick check

```bash
python scripts/check_release_integrity.py
```

## Rebuild figures

```bash
python 06_data_code_and_provenance/figure_source_data/Fig1/scripts/build_fig01_urbanclimate.py
python 06_data_code_and_provenance/figure_source_data/Fig3/scripts/build_fig03_urbanclimate.py
python 06_data_code_and_provenance/figure_source_data/Fig4/scripts/build_fig04_urbanclimate.py
python 06_data_code_and_provenance/scripts/build_urbanclimate_fig2_fig5_v1.py
```
