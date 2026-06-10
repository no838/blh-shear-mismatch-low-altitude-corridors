#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    root / "06_data_code_and_provenance/figure_source_data/Fig1/source_tables/regime_state_summary_table.csv",
    root / "06_data_code_and_provenance/figure_source_data/Fig3/source_tables/hotspot_membership_table.csv",
    root / "06_data_code_and_provenance/figure_source_data/Fig4/source_tables/per_city_typology_table.csv",
    root / "06_data_code_and_provenance/smii_core/tables/smii_hotspot_contrast_v1.csv",
    root / "06_data_code_and_provenance/paris_dwl_validation/tables/paris_dwl_event_support_summary_600s.csv",
]
missing = [str(p.relative_to(root)) for p in required if not p.exists()]
if missing:
    print("Missing required files:")
    print("\n".join(missing))
    sys.exit(1)
print("Release integrity check passed.")
