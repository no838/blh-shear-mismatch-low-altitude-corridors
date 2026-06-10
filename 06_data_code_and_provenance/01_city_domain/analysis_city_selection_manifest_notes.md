# Analysis City Selection Notes

This table reconstructs the relationship among three preserved layers:

- the 42-city ERA5 download catalogue in `city_domain_manifest.csv`;
- the 13-city main-analysis layer preserved in `per_city_typology_table.csv` and the repaired hourly-meteorology summary;
- the 11-city hotspot layer preserved in `hotspot_membership_table.csv`.

Reconstructed counts:

- download catalogue cities: 42
- main-analysis cities: 13
- hotspot-subset cities: 11

Important boundary:

- the bundle preserves a repaired hourly-meteorology summary and a missing-gust-month log;
- the bundle does **not** preserve the original city-level hotspot exclusion ledger;
- therefore the 11-city hotspot subset is documented as a preserved complete-case layer, not as a uniquely attributed consequence of one specific missing-data mechanism.
