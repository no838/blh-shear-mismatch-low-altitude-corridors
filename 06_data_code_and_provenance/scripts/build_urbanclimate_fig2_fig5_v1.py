#!/usr/bin/env python3
"""Build UrbanClimate-polished main figures for the low-altitude decoupling manuscript.

Outputs publication-oriented vector/raster bundles for:
- Fig. 2: bounded SMII diagnostic and BLH-shear benchmark.
- Fig. 5: Paris Doppler-wind-lidar profile evidence.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle, FancyBboxPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SMII_SRC = ROOT / "06_data_code_and_provenance" / "smii_core" / "tables"
PARIS_SRC = ROOT / "06_data_code_and_provenance" / "paris_dwl_validation" / "tables"
OUT = ROOT / "06_data_code_and_provenance" / "generated" / "urbanclimate_fig2_fig5_v1"
FIG_DIR = OUT / "FIGURES"
TAB_DIR = OUT / "TABLES"
REP_DIR = OUT / "REPORTS"
for d in (FIG_DIR, TAB_DIR, REP_DIR):
    d.mkdir(parents=True, exist_ok=True)

PALETTE = {
    "ink": "#1F2428",
    "muted": "#67717A",
    "grid": "#D7DCE0",
    "paper": "#FFFFFF",
    "panel_bg": "#F6F8F7",
    "mix": "#176F63",
    "ratio": "#B77A34",
    "smii": "#0E6973",
    "simple": "#7666A7",
    "wind": "#B95B4B",
    "shear": "#53606E",
    "joint": "#236192",
    "blue": "#2B6F9F",
    "light_blue": "#DDEBF3",
    "orange": "#C9822E",
    "red": "#B2483F",
    "grey": "#8B949E",
    "light_grey": "#EEF1F2",
}


def require_files(paths: Iterable[Path]) -> None:
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError("Missing required source files:\n" + "\n".join(missing))


def setup_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 7.4,
        "axes.titlesize": 7.8,
        "axes.labelsize": 7.4,
        "xtick.labelsize": 6.8,
        "ytick.labelsize": 6.8,
        "legend.fontsize": 6.8,
        "axes.linewidth": 0.62,
        "xtick.major.width": 0.55,
        "ytick.major.width": 0.55,
        "xtick.major.size": 2.4,
        "ytick.major.size": 2.4,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })


def panel_label(ax, label: str, x: float = -0.10, y: float = 1.10) -> None:
    ax.text(x, y, label, transform=ax.transAxes, ha="left", va="top",
            fontsize=8.8, fontweight="bold", color=PALETTE["ink"])


def clean_axis(ax, grid_axis: str | None = None) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(colors=PALETTE["ink"], labelcolor=PALETTE["ink"])
    if grid_axis:
        ax.grid(axis=grid_axis, color=PALETTE["grid"], lw=0.35, alpha=0.85)
        ax.set_axisbelow(True)


def export_bundle(fig, base: Path) -> dict[str, dict[str, float | str]]:
    outputs = {}
    fig.canvas.draw()
    for suffix, kwargs in [
        (".png", {"dpi": 600}),
        (".pdf", {}),
        (".svg", {}),
        (".tiff", {"dpi": 600, "pil_kwargs": {"compression": "tiff_lzw"}}),
    ]:
        path = base.with_suffix(suffix)
        fig.savefig(path, bbox_inches="tight", **kwargs)
        outputs[suffix.lstrip(".")] = {"path": str(path), "bytes": path.stat().st_size}
    return outputs


def overlap_report(fig) -> dict[str, object]:
    """Conservative text-overlap preflight based on rendered text boxes."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    boxes = []
    labels = []
    for ax_i, ax in enumerate(fig.axes):
        for text in ax.texts:
            if not text.get_visible() or not text.get_text().strip():
                continue
            bbox = text.get_window_extent(renderer=renderer).expanded(1.03, 1.05)
            if bbox.width <= 0 or bbox.height <= 0:
                continue
            boxes.append(bbox)
            labels.append((ax_i, text.get_text()[:45]))
    overlaps = []
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if boxes[i].overlaps(boxes[j]):
                # Ignore same-position intentional labels inside tiny heatmap cells only if identical text is not involved.
                overlaps.append({"a": labels[i], "b": labels[j]})
    return {"text_boxes": len(boxes), "overlap_count_conservative": len(overlaps), "sample_overlaps": overlaps[:12]}


def build_fig2() -> tuple[Path, dict[str, object]]:
    required = [
        SMII_SRC / "smii_hotspot_contrast_v1.csv",
        SMII_SRC / "smii_upper_state_summary_v1.csv",
        SMII_SRC / "smii_predictive_benchmark_v1.csv",
    ]
    require_files(required)
    contrast = pd.read_csv(required[0])
    upper = pd.read_csv(required[1])
    bench = pd.read_csv(required[2])

    fig = plt.figure(figsize=(7.20, 4.78), dpi=220)
    gs = fig.add_gridspec(
        2, 3,
        height_ratios=[0.92, 1.34],
        width_ratios=[1.10, 1.02, 1.20],
        left=0.065, right=0.985, bottom=0.105, top=0.95,
        wspace=0.42, hspace=0.52,
    )
    axA = fig.add_subplot(gs[0, :])
    axB = fig.add_subplot(gs[1, 0])
    axC = fig.add_subplot(gs[1, 1])
    axD = fig.add_subplot(gs[1, 2])

    # Panel A: mechanism diagnostic strip.
    axA.axis("off")
    panel_label(axA, "A", x=-0.045, y=1.05)
    axA.set_xlim(0, 1)
    axA.set_ylim(0, 1)
    axA.text(0.00, 0.98, "Bounded shear-mixing imbalance diagnostic", ha="left", va="top",
             fontsize=8.0, fontweight="bold", color=PALETTE["ink"])
    axA.text(0.00, 0.82, "Scalar SMII is an enrichment diagnostic; the BLH-shear state-space benchmark remains primary.",
             ha="left", va="top", fontsize=6.7, color=PALETTE["muted"])

    cards = [
        (0.01, 0.18, 0.30, 0.45, "Simple SMII", "z(log(1 + S))\n- z(log(1 + BLH))", PALETTE["simple"]),
        (0.35, 0.18, 0.29, 0.45, "Constrained SMII", "-z(log(1 + BLH))\n+ z(log(1 + S / BLH))", PALETTE["smii"]),
        (0.68, 0.18, 0.29, 0.45, "Primary test", "BLH-shear phase state\nplus interaction benchmark", PALETTE["joint"]),
    ]
    for x, y, w, h, title, body, col in cards:
        axA.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.018",
                                     fc=PALETTE["panel_bg"], ec="#CBD4D7", lw=0.65))
        axA.add_patch(Rectangle((x, y), 0.010, h, fc=col, ec=col, lw=0))
        axA.text(x + 0.025, y + h - 0.090, title, ha="left", va="top", fontsize=6.7,
                 color=col, fontweight="bold")
        axA.text(x + 0.025, y + 0.145, body, ha="left", va="center", fontsize=5.75,
                 color=PALETTE["ink"], wrap=True)
    axA.text(0.01, 0.05, "Observation unit: city-state-response cell; n = 167, hotspot rows = 32. All z-scores use the finite cell table.",
             ha="left", va="bottom", fontsize=6.35, color=PALETTE["muted"])

    # Panel B: contrasts as signed lollipop plot.
    panel_label(axB, "B")
    contrast_items = [
        ("smii_z", "Constrained SMII", PALETTE["smii"]),
        ("mixing_deficit_z", "Mixing deficit", PALETTE["mix"]),
        ("smii_simple_z", "Simple SMII", PALETTE["simple"]),
        ("shear_z", "Shear", PALETTE["shear"]),
        ("wind_intensity_z", "Bulk wind", PALETTE["wind"]),
    ]
    rows = []
    for metric, label, color in contrast_items:
        r = contrast.loc[contrast["metric"] == metric].iloc[0]
        rows.append((label, float(r["hotspot_minus_nonhotspot"]), color))
    y = np.arange(len(rows))[::-1]
    vals = [r[1] for r in rows]
    labels = [r[0] for r in rows]
    colors = [r[2] for r in rows]
    axB.axvline(0, color="#7D858B", lw=0.65)
    for yi, val, col in zip(y, vals, colors):
        axB.plot([0, val], [yi, yi], color=col, lw=1.35, solid_capstyle="round")
        axB.scatter(val, yi, s=28, color=col, edgecolor="white", linewidth=0.55, zorder=3)
        axB.text(val + (0.065 if val >= 0 else -0.065), yi, f"{val:+.2f}",
                 ha="left" if val >= 0 else "right", va="center", fontsize=6.6, color=PALETTE["ink"])
    axB.set_yticks(y)
    axB.set_yticklabels(labels)
    axB.set_xlim(-0.90, 1.48)
    axB.set_xlabel("Hotspot minus non-hotspot (z)")
    axB.set_title("Hotspot cells are shallow-mixing states", loc="left", pad=4)
    clean_axis(axB, grid_axis="x")

    # Panel C: hotspot prevalence under gates.
    panel_label(axC, "C")
    gate_items = [
        ("background_all_cells", "All\ncells", PALETTE["grey"]),
        ("wind_intensity_top20_only", "Wind\ntop", PALETTE["wind"]),
        ("simple_SMII_top20_only", "Simple\nSMII", PALETTE["simple"]),
        ("mixing_deficit_top20_only", "Mixing\ndeficit", PALETTE["mix"]),
        ("SMII_upper_state", "Constrained\nstate", PALETTE["smii"]),
    ]
    cvals, cn, clabs, ccols = [], [], [], []
    for gate, label, color in gate_items:
        r = upper.loc[upper["gate"] == gate].iloc[0]
        cvals.append(float(r["hotspot_rate"]))
        cn.append(int(r["n"]))
        clabs.append(label)
        ccols.append(color)
    y2 = np.arange(len(cvals))[::-1]
    axC.barh(y2, cvals, color=ccols, edgecolor="#2C3338", linewidth=0.45, height=0.58)
    axC.axvline(cvals[0], color=PALETTE["muted"], lw=0.7, ls="--")
    for yi, val, n in zip(y2, cvals, cn):
        axC.text(val + 0.020, yi, f"{val:.2f}", ha="left", va="center", fontsize=6.3, color=PALETTE["ink"])
        axC.text(0.018, yi, f"n={n}", ha="left", va="center", fontsize=5.7, color="white" if val > 0.28 else PALETTE["muted"])
    axC.set_xlim(0, 0.60)
    axC.set_yticks(y2)
    axC.set_yticklabels([lab.replace("\n", " ") for lab in clabs])
    axC.set_xlabel("Hotspot prevalence")
    axC.set_title("Upper-state enrichment", loc="left", pad=4)
    clean_axis(axC, grid_axis="x")
    bg = cvals[0]
    enriched = cvals[-1]

    # Panel D: benchmark AUC.
    panel_label(axD, "D")
    bench_items = [
        ("Bulk wind intensity", "Bulk wind", PALETTE["wind"]),
        ("Shear only", "Shear only", PALETTE["shear"]),
        ("Simple SMII scalar", "Simple SMII", PALETTE["simple"]),
        ("SMII scalar", "Constrained SMII", PALETTE["smii"]),
        ("Mixing deficit only", "Mixing deficit", PALETTE["mix"]),
        ("BLH + shear", "BLH + shear", PALETTE["joint"]),
        ("BLH x shear (poly2)", "BLH x shear", PALETTE["joint"]),
        ("BLH x shear x gust (poly2)", "BLH x shear x gust", PALETTE["joint"]),
    ]
    b_rows = []
    for model, label, color in bench_items:
        r = bench.loc[bench["model"] == model].iloc[0]
        b_rows.append((label, float(r["auc_mean"]), float(r["auc_sd"]), color))
    b_rows = sorted(b_rows, key=lambda t: t[1])
    yy = np.arange(len(b_rows))
    axD.axvspan(0.50, 0.60, color="#F1F3F4", zorder=0)
    axD.axvline(0.50, color="#858B90", ls="--", lw=0.65)
    for yi, (label, auc, sd, color) in zip(yy, b_rows):
        axD.plot([auc - sd, auc + sd], [yi, yi], color=color, lw=1.0, alpha=0.70)
        axD.scatter(auc, yi, s=28, color=color, edgecolor="white", linewidth=0.55, zorder=3)
        axD.text(auc + 0.012, yi, f"{auc:.2f}", ha="left", va="center", fontsize=6.4)
    axD.set_yticks(yy)
    axD.set_yticklabels([r[0] for r in b_rows])
    axD.set_xlim(0.54, 0.93)
    axD.set_xlabel("Cross-validated ROC AUC")
    axD.set_title("State-space model remains strongest", loc="left", pad=4)
    clean_axis(axD, grid_axis="x")

    base = FIG_DIR / "Fig2_SMII_bounded_diagnostic_UrbanClimate_v4"
    outputs = export_bundle(fig, base)
    preflight = overlap_report(fig)
    plt.close(fig)

    source_rows = []
    for label, val, color in rows:
        source_rows.append({"figure": "Fig2", "panel": "B", "item": label, "value": val, "uncertainty_sd": np.nan, "color": color})
    for label, val, n, color in zip(clabs, cvals, cn, ccols):
        source_rows.append({"figure": "Fig2", "panel": "C", "item": label.replace("\n", " "), "value": val, "n": n, "uncertainty_sd": np.nan, "color": color})
    for label, auc, sd, color in b_rows:
        source_rows.append({"figure": "Fig2", "panel": "D", "item": label, "value": auc, "uncertainty_sd": sd, "color": color})
    pd.DataFrame(source_rows).to_csv(TAB_DIR / "Fig2_SMII_bounded_diagnostic_UrbanClimate_source_data_v4.csv", index=False)

    report = {
        "figure": "Fig. 2",
        "claim": "A bounded shear-mixing imbalance diagnostic enriches amplified-decoupling hotspots, but the BLH-shear state-space benchmark remains the primary discriminator.",
        "claim_ceiling": "diagnostic enrichment and mechanism-consistent state-space support; not a universal scalar law or causal closure",
        "panel_map": {
            "A": "defines transparent and constrained SMII forms and states the boundary",
            "B": "shows hotspot cells are shallow-mixing / high-SMII states rather than bulk-wind states",
            "C": "shows constrained-state enrichment relative to background and intensity top tail",
            "D": "benchmarks scalar diagnostics against BLH-shear state-space classifiers",
        },
        "source_tables": [str(p) for p in required],
        "exports": outputs,
        "preflight": preflight,
        "notes": "No figure-level title is rendered inside the image; caption should carry Fig. 2 title.",
    }
    (REP_DIR / "Fig2_SMII_bounded_diagnostic_UrbanClimate_QA_v4.md").write_text(
        "# Fig. 2 UrbanClimate Figure QA v4\n\n" + json.dumps(report, indent=2), encoding="utf-8"
    )
    return base.with_suffix(".png"), report


def build_fig5() -> tuple[Path, dict[str, object]]:
    required = [
        PARIS_SRC / "paris_dwl_station_metadata.csv",
        PARIS_SRC / "paris_dwl_height_availability_600s.csv",
        PARIS_SRC / "paris_dwl_pair_summary_600s.csv",
        PARIS_SRC / "paris_dwl_event_chain_summary_600s.csv",
        PARIS_SRC / "paris_dwl_event_support_summary_600s.csv",
        PARIS_SRC / "paris_dwl_event_placebo_600s.csv",
    ]
    require_files(required)
    stations = pd.read_csv(required[0])
    avail = pd.read_csv(required[1])
    pairs = pd.read_csv(required[2])
    event = pd.read_csv(required[3])
    support = pd.read_csv(required[4]).iloc[0]
    placebo = pd.read_csv(required[5])

    fig = plt.figure(figsize=(7.20, 4.92), dpi=220)
    gs = fig.add_gridspec(
        2, 2,
        height_ratios=[1.0, 1.16],
        width_ratios=[1.0, 1.08],
        left=0.072, right=0.985, bottom=0.105, top=0.955,
        wspace=0.34, hspace=0.48,
    )
    axA = fig.add_subplot(gs[0, 0])
    axB = fig.add_subplot(gs[0, 1])
    axC = fig.add_subplot(gs[1, 0])
    axD = fig.add_subplot(gs[1, 1])

    # Panel A: six-site transect in geographic coordinates.
    panel_label(axA, "A")
    lon = stations["station_lon"].to_numpy()
    lat = stations["station_lat"].to_numpy()
    axA.add_patch(Rectangle((lon.min() - 0.035, lat.min() - 0.020),
                            lon.max() - lon.min() + 0.070, lat.max() - lat.min() + 0.040,
                            fc="#F4F8FA", ec="#D6DEE3", lw=0.6, zorder=0))
    axA.plot(lon, lat, color="#A7B6C1", lw=0.65, zorder=1)
    axA.scatter(lon, lat, s=34, color=PALETTE["blue"], edgecolor="white", linewidth=0.7, zorder=3)
    label_offsets = {
        "PAARBO": (0.010, -0.002),
        "PACHEM": (0.010, 0.004),
        "PAJUSS": (0.010, 0.002),
        "PALUPD": (0.010, -0.004),
        "PAROIS": (-0.012, 0.006),
        "PASIRT": (0.010, -0.002),
    }
    for _, r in stations.iterrows():
        dx, dy = label_offsets.get(r["station"], (0.008, 0.004))
        axA.text(r["station_lon"] + dx, r["station_lat"] + dy, r["station"], fontsize=6.15,
                 ha="left" if dx >= 0 else "right", va="center", color=PALETTE["ink"])
    axA.set_xlabel("Longitude")
    axA.set_ylabel("Latitude")
    axA.set_title("Six Doppler-wind-lidar sites", loc="left", pad=4)
    clean_axis(axA, grid_axis=None)
    axA.grid(color=PALETTE["grid"], lw=0.32, alpha=0.70)
    axA.set_aspect("equal", adjustable="box")

    # Panel B: target height availability matrix.
    panel_label(axB, "B")
    height_order = [10, 20, 100, 200, 300, 500]
    station_order = stations["station"].tolist()
    mat = avail.pivot(index="station", columns="target_height_m_agl", values="valid_fraction").reindex(index=station_order, columns=height_order)
    cmap = LinearSegmentedColormap.from_list("availability", ["#FFF3C4", "#7EC8BD", "#173B7A"])
    im = axB.imshow(mat.values, vmin=0, vmax=1, cmap=cmap, aspect="auto")
    axB.set_xticks(np.arange(len(height_order)))
    axB.set_xticklabels([f"{h}" for h in height_order])
    axB.set_xlabel("Target height AGL (m)")
    axB.set_yticks(np.arange(len(station_order)))
    axB.set_yticklabels(station_order)
    axB.set_title("Strict target-height availability", loc="left", pad=4)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = float(mat.values[i, j])
            if v <= 0.02 or v >= 0.85:
                axB.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=5.55,
                         color="white" if v > 0.62 else PALETTE["ink"])

    # Panel C: pair support with unavailable low-pair boundary.
    panel_label(axC, "C")
    pair_order = ["10-100", "20-200", "100-200", "100-300", "200-500"]
    pp = pairs.set_index("pair_m_agl").reindex(pair_order).reset_index()
    y_pairs = np.arange(len(pair_order))[::-1]
    coverage = pp["coverage_fraction"].fillna(0).to_numpy()
    median_shear = pp["median_abs_shear_ms"].to_numpy()
    valid = coverage > 0
    bar_colors = [PALETTE["light_grey"] if not v else PALETTE["blue"] for v in valid]
    axC.barh(y_pairs, coverage, height=0.58, color=bar_colors, edgecolor="#2C3338", linewidth=0.45)
    axC.set_xlim(0, 1.00)
    axC.set_yticks(y_pairs)
    axC.set_yticklabels(pair_order)
    axC.set_xlabel("Pair coverage fraction")
    for yi, cov, ok, med in zip(y_pairs, coverage, valid, median_shear):
        axC.text(cov + 0.018 if ok else 0.030, yi, f"{cov:.2f}", ha="left", va="center", fontsize=6.1,
                 color=PALETTE["ink"] if ok else PALETTE["muted"])
        if ok and np.isfinite(med):
            axC.text(0.97, yi, f"med={med:.2f}", ha="right", va="center",
                     fontsize=5.8, color=PALETTE["orange"])
        else:
            axC.text(0.97, yi, "no strict pair", ha="right", va="center",
                     fontsize=5.8, color=PALETTE["muted"])
    axC.set_title("Observable height-pair support", loc="left", pad=4)
    clean_axis(axC, grid_axis="x")

    # Panel D: event profile and placebo contrast.
    panel_label(axD, "D")
    eh = event["relative_hour"].to_numpy(dtype=float)
    mean = event["shear_abs_100_300m_z_mean"].to_numpy(dtype=float)
    se = event["shear_abs_100_300m_z_se"].to_numpy(dtype=float)
    axD.fill_between(eh, mean - se, mean + se, color=PALETTE["red"], alpha=0.16, lw=0)
    axD.plot(eh, mean, color=PALETTE["red"], lw=1.35)
    axD.axhline(0, color="#868E94", lw=0.6)
    axD.axvline(0, color=PALETTE["ink"], lw=0.7)
    axD.axvspan(-1, 1, color="#2C3338", alpha=0.06, lw=0)
    axD.set_xlim(-12, 12)
    axD.set_ylim(min(mean - se) - 0.16, max(mean + se) + 0.18)
    axD.set_xlabel("Relative hour from event center")
    axD.set_ylabel("100-300 m |Delta ws| anomaly (z)")
    axD.set_title("Event-specific profile response", loc="left", pad=4)
    clean_axis(axD, grid_axis="both")
    obs = float(support["core_minus_lead_z"])
    p95 = float(placebo["core_minus_lead_z"].quantile(0.95))
    n_events = int(support["n_event_centers"])
    axD.text(0.03, 0.95, f"n = {n_events} events\ncore - lead = {obs:.2f}\nplacebo p95 = {p95:.2f}",
             transform=axD.transAxes, ha="left", va="top", fontsize=6.2,
             bbox={"boxstyle": "round,pad=0.22", "fc": "white", "ec": "#C7CDD1", "lw": 0.45})
    axins = inset_axes(axD, width="34%", height="27%", loc="lower right", borderpad=1.25)
    axins.hist(placebo["core_minus_lead_z"], bins=20, color="#D8DEE2", edgecolor="white", lw=0.35)
    axins.axvline(p95, color=PALETTE["muted"], lw=0.8)
    axins.axvline(obs, color=PALETTE["red"], lw=1.2)
    axins.set_yticks([])
    axins.set_xticks([0, 0.5, 1.0])
    axins.tick_params(axis="x", labelsize=5.1, length=1.6, width=0.35)
    axins.spines["top"].set_visible(False)
    axins.spines["right"].set_visible(False)
    axins.spines["left"].set_visible(False)
    axins.spines["bottom"].set_linewidth(0.35)
    axins.text(0.04, 0.94, "placebo", transform=axins.transAxes, ha="left", va="top",
               fontsize=5.5, color=PALETTE["muted"])

    base = FIG_DIR / "Fig5_Paris_DWL_profile_evidence_UrbanClimate_v4"
    outputs = export_bundle(fig, base)
    preflight = overlap_report(fig)
    plt.close(fig)

    source_rows = []
    for _, r in stations.iterrows():
        source_rows.append({"figure": "Fig5", "panel": "A", "item": r["station"], "station_lon": r["station_lon"], "station_lat": r["station_lat"]})
    for _, r in avail.iterrows():
        source_rows.append({"figure": "Fig5", "panel": "B", "item": r["station"], "target_height_m_agl": r["target_height_m_agl"], "valid_fraction": r["valid_fraction"]})
    for _, r in pp.iterrows():
        source_rows.append({"figure": "Fig5", "panel": "C", "item": r["pair_m_agl"], "coverage_fraction": r["coverage_fraction"], "median_abs_shear_ms": r["median_abs_shear_ms"]})
    for _, r in event.iterrows():
        source_rows.append({"figure": "Fig5", "panel": "D", "item": int(r["relative_hour"]),
                            "shear_abs_100_300m_z_mean": r["shear_abs_100_300m_z_mean"],
                            "shear_abs_100_300m_z_se": r["shear_abs_100_300m_z_se"]})
    pd.DataFrame(source_rows).to_csv(TAB_DIR / "Fig5_Paris_DWL_profile_evidence_UrbanClimate_source_data_v4.csv", index=False)

    report = {
        "figure": "Fig. 5",
        "claim": "Paris Doppler-wind-lidar profiles independently confirm event-specific cross-height wind-profile decoupling in observable 100-300 m and 200-500 m layers.",
        "claim_ceiling": "profile evidence of vertical-profile expression; not direct BLH closure, not strict 10-100 m or 20-200 m validation, not global validation",
        "panel_map": {
            "A": "documents the six-site urban transect",
            "B": "shows strict target-height availability and missing low-layer overlaps",
            "C": "quantifies which height pairs support observed profile contrasts",
            "D": "tests event specificity against a placebo distribution",
        },
        "source_tables": [str(p) for p in required],
        "exports": outputs,
        "preflight": preflight,
        "event_core_minus_lead_z": obs,
        "placebo_core_minus_lead_p95": p95,
        "notes": "ERA5 BLH alignment remains supplementary context because it does not close event-scale BLH mediation.",
    }
    (REP_DIR / "Fig5_Paris_DWL_profile_evidence_UrbanClimate_QA_v4.md").write_text(
        "# Fig. 5 UrbanClimate Figure QA v4\n\n" + json.dumps(report, indent=2), encoding="utf-8"
    )
    return base.with_suffix(".png"), report


def main() -> None:
    setup_style()
    fig2_path, fig2_report = build_fig2()
    fig5_path, fig5_report = build_fig5()
    summary = {
        "output_root": str(OUT),
        "figures": [str(fig2_path), str(fig5_path)],
        "figure_contracts": {
            "Fig2": fig2_report["claim"],
            "Fig5": fig5_report["claim"],
        },
        "submission_target": "Urban Climate manuscript; figures exported as editable vector plus high-resolution raster support.",
    }
    (REP_DIR / "UrbanClimate_Fig2_Fig5_Polish_Summary_v4.md").write_text(
        "# UrbanClimate Fig. 2 and Fig. 5 Polish Summary v4\n\n" + json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
