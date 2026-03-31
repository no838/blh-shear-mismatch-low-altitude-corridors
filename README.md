# BLH-Shear Mismatch and Low-Altitude Corridor Decoupling

This repository contains code and reproducibility scaffolding for a cross-city analysis of boundary-layer height-shear mismatch, low-altitude corridor decoupling, observational validation, operational-endpoint linkage, and manuscript figure generation.

## Scope

The repository supports:

- low-altitude corridor dynamics analysis
- boundary-layer event diagnostics
- cross-city structural typology analysis
- independent validation against public observations
- operational-endpoint linkage
- manuscript figure generation

## Repository layout

- `integrated_pipeline/`: top-level execution entry points
- `workspace/`: path helpers and release-friendly workspace utilities
- `core_analysis/`: main corridor and boundary-layer diagnostics
- `figure_generation/`: manuscript and supplementary figure scripts
- `upgrade/`: external outcome, independent validation, operational endpoint, and figure-recast modules
- `manifests/`: release manifest and reproducibility notes

## Data access

This repository does not redistribute third-party raw datasets. Upstream public sources include ERA5, NOAA ISD, IGRA, BTS TranStats, public CAAC bulletins, and Hong Kong Observatory archives. Derived tables used in the manuscript can be regenerated from these sources with the provided workflow.

## Reproducibility

See `REPRODUCIBILITY.md` for environment setup, execution order, expected inputs, and output checkpoints.
