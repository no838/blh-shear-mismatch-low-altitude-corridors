# Fig. 5 Release Figure QA v4

{
  "figure": "Fig. 5",
  "claim": "Paris Doppler-wind-lidar profiles independently confirm event-specific cross-height wind-profile decoupling in observable 100-300 m and 200-500 m layers.",
  "claim_ceiling": "profile evidence of vertical-profile expression; not direct BLH closure, not strict 10-100 m or 20-200 m validation, not global validation",
  "panel_map": {
    "A": "documents the six-site urban transect",
    "B": "shows strict target-height availability and missing low-layer overlaps",
    "C": "quantifies which height pairs support observed profile contrasts",
    "D": "tests event specificity against a placebo distribution"
  },
  "source_tables": [
    "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/data/figure_5/paris_lidar_station_metadata.csv",
    "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/data/figure_5/paris_lidar_height_availability_600s.csv",
    "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/data/figure_5/paris_lidar_pair_summary_600s.csv",
    "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/data/figure_5/paris_lidar_event_chain_summary_600s.csv",
    "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/data/figure_5/paris_lidar_event_support_summary_600s.csv",
    "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/data/figure_5/paris_lidar_event_placebo_600s.csv"
  ],
  "exports": {
    "png": {
      "path": "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/figures/Figure_5_paris_lidar_profile_evidence_v2.png",
      "bytes": 619922
    },
    "pdf": {
      "path": "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/figures/Figure_5_paris_lidar_profile_evidence_v2.pdf",
      "bytes": 44369
    },
    "svg": {
      "path": "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/figures/Figure_5_paris_lidar_profile_evidence_v2.svg",
      "bytes": 65090
    },
    "tiff": {
      "path": "<local_root>/\u4f4e\u7a7a\u7ecf\u6d4e/TOPJOURNAL_NC_MASTER_WORKSPACE_V1/public_release_v2/urban_boundary_layer_vertical_decoupling_release/figures/Figure_5_paris_lidar_profile_evidence_v2.tiff",
      "bytes": 1863200
    }
  },
  "preflight": {
    "text_boxes": 57,
    "overlap_count_conservative": 0,
    "sample_overlaps": []
  },
  "event_core_minus_lead_z": 0.936323725244115,
  "placebo_core_minus_lead_p95": 0.1310832352176993,
  "notes": "ERA5 BLH alignment remains supplementary context because it does not close event-scale BLH mediation."
}