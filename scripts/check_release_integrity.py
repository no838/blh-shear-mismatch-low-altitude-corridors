#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
required = [
    root / "data/figure_1/regime_state_summary_table.csv",
    root / "data/figure_2/mechanism_index_hotspot_contrast_v1.csv",
    root / "data/figure_3/hotspot_membership_table.csv",
    root / "data/figure_4/city_typology_table.csv",
    root / "data/figure_5/paris_lidar_event_support_summary_600s.csv",
    root / "figures/Figure_2_mechanism_diagnostic.pdf",
    root / "figures/Figure_5_paris_lidar_profile_evidence.pdf",
]
missing = [str(p.relative_to(root)) for p in required if not p.exists()]
if missing:
    print("Missing required files:")
    print("\n".join(missing))
    sys.exit(1)
print("Release integrity check passed.")
