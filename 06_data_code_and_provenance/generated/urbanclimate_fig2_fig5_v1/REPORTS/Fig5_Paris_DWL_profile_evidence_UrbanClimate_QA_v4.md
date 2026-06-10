# Fig. 5 UrbanClimate Figure QA v4

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
    "./06_data_code_and_provenance/paris_dwl_validation/tables/paris_dwl_station_metadata.csv",
    "./06_data_code_and_provenance/paris_dwl_validation/tables/paris_dwl_height_availability_600s.csv",
    "./06_data_code_and_provenance/paris_dwl_validation/tables/paris_dwl_pair_summary_600s.csv",
    "./06_data_code_and_provenance/paris_dwl_validation/tables/paris_dwl_event_chain_summary_600s.csv",
    "./06_data_code_and_provenance/paris_dwl_validation/tables/paris_dwl_event_support_summary_600s.csv",
    "./06_data_code_and_provenance/paris_dwl_validation/tables/paris_dwl_event_placebo_600s.csv"
  ],
  "exports": {
    "png": {
      "path": "./06_data_code_and_provenance/generated/urbanclimate_fig2_fig5_v1/FIGURES/Fig5_Paris_DWL_profile_evidence_UrbanClimate_v4.png",
      "bytes": 619922
    },
    "pdf": {
      "path": "./06_data_code_and_provenance/generated/urbanclimate_fig2_fig5_v1/FIGURES/Fig5_Paris_DWL_profile_evidence_UrbanClimate_v4.pdf",
      "bytes": 44369
    },
    "svg": {
      "path": "./06_data_code_and_provenance/generated/urbanclimate_fig2_fig5_v1/FIGURES/Fig5_Paris_DWL_profile_evidence_UrbanClimate_v4.svg",
      "bytes": 65090
    },
    "tiff": {
      "path": "./06_data_code_and_provenance/generated/urbanclimate_fig2_fig5_v1/FIGURES/Fig5_Paris_DWL_profile_evidence_UrbanClimate_v4.tiff",
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