# City Domain Manifest Notes

- No project-authoritative city polygon shapefile or GeoJSON was preserved in the current workspace.
- Bounding boxes were parsed from `PROJECT_ROOT/pipeline/01_data_download_and_preprocess/arco_era5_2015_2025_global_urban_clusters_to_netcdf.py`.
- `retained_ERA5_cells` is an estimated count of 0.25-degree ERA5 grid-cell centers within each download bbox.
- The study time window was inferred from the retained 2015-2025 ERA5 pipeline plus `n_months_with_state = 132` in the hotspot-membership table.
