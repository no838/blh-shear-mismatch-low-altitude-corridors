#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 13:31:29 2026

"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

"""
LOW-ALTITUDE SAFETY CORRIDOR DYNAMICS PIPELINE v2
=================================================
Upgrade target
--------------
Extend the original state-conditioned corridor pipeline toward boundary-layer
dynamics and extreme-event-window analysis.

Compared with v1, this version adds:
1) stronger BLH-controlled states
2) stronger shear-controlled states
3) gust-controlled states
4) compound dynamic states
5) event-centered lead/core/lag windows around extreme hours

Core science question
---------------------
How do low-altitude safety-corridor structure, persistence, fragmentation,
and percolation thresholds differ between 10 m and 100 m wind layers under
boundary-layer dynamical states and extreme-event windows?

Supported target variables
--------------------------
- wind10
- wind100

Supported responses
-------------------
- var
- ar1

Supported state groups (new)
----------------------------
Basic:
- all
- day
- night

BLH-related:
- stable_like
- unstable_like
- stable_lowblh
- unstable_highblh

Shear-related:
- shear_low
- shear_high
- shear_weak
- shear_moderate
- shear_extreme

Gust-related:
- gust_high
- gust_extreme

Compound:
- stable_shear_high
- unstable_shear_high
- gust_shear_compound
- stable_gust_extreme

Event windows:
- event_gust_lead
- event_gust_core
- event_gust_lag
- event_gust_leadlag
- event_shear_lead
- event_shear_core
- event_shear_lag
- event_shear_leadlag

Input
-----
ERA5 monthly zip files:
  <ERA5_ROOT>/<CITY>/ERA5_<CITY>_YYYYMM_low_altitude_RLCC.zip

City tables:
  <ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/metrics_city_table.csv
  <ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/cluster_assignments.csv

Output
------
  <ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR/

Notes
-----
- English-only plots.
- Built to preserve the core logic of your v1 pipeline.
- This script is long but self-contained.


/opt/anaconda3/envs/raynode/bin/python "<PROJECT_ROOT>/low_altitude_safety_corridor_dynamics_pipeline_v2.py" \
  --era5_root "<ERA5_ROOT>" \
  --city_level_root "<ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL" \
  --cities China_GBA China_JJJ China_YRD Japan_Kanto USA_NYC UK_London Germany_RhineRuhr Singapore_Johor_Riau UAE_Dubai_AbuDhabi India_DelhiNCR Brazil_SaoPaulo Australia_Sydney Nigeria_Lagos \
  --state_group day night stable_like unstable_like shear_weak shear_moderate shear_extreme gust_high gust_extreme stable_shear_high gust_shear_compound \
  --responses var ar1 \
  --year0 2015 --year1 2025 \
  --tau 0.10 \
  --roll_win 24 \
  --neigh 3 \
  --sample_per_file 12000 \
  --max_samples 1200000 \
  --support_bins 70 \
  --support_min_count 5 \
  --grid_res 180 \
  --quantiles 0.05 0.10 0.25 0.50 0.75 0.90 0.95 \
  --critical_lo 0.10 \
  --critical_hi 0.90 \
  --critical_band_q 0.90 \
  --min_city_points 200 \
  --min_city_points_floor 2 \
  --city_output_points_floor 1 \
  --per_city_train_cap 20000 \
  --min_pooled_train 600 \
  --min_quantile_samples 250 \
  --global_max_train 800000 \
  --bootstrap_B 80 \
  --bootstrap_seed 2026 \
  --bootstrap_max_train 250000 \
  --loco_max_train 200000 \
  --allow_extrapolation \
  --soft_clip_qlo 0.01 \
  --soft_clip_qhi 0.99 \
  --make_corridors \
  --mosaic_cols 3 \
  --ph_alpha 0.65 \
  --ph_top_k 1 \
  --ph_persistence_mode quantile \
  --ph_persistence_value 0.50 \
  --ph_make_skeleton \
  --make_percolation \
  --perc_levels 31 \
  --perc_connectivity 4 \
  --perc_smooth_win 5 \
  --perc_tau_fit \
  --tau_fit_bins 22 \
  --tau_smin 2 \
  --tau_smax_quantile 0.95 \
  --tau_fit_min_points 10 \
  --scaling_window_frac 0.25 \
  --scaling_min_points 8 \
  --scaling_r2_min 0.55 \
  --day_hour_start 8 \
  --day_hour_end 18 \
  --shear_q 0.50 \
  --shear_low_q 0.30 \
  --shear_high_q 0.70 \
  --shear_extreme_q 0.90 \
  --gust_high_q 0.70 \
  --gust_extreme_q 0.90 \
  --blh_low_q 0.30 \
  --blh_high_q 0.70 \
  --event_lead_hours 6 \
  --event_lag_hours 6 \
  --event_min_gap_hours 6



/opt/anaconda3/envs/raynode/bin/python "<PROJECT_ROOT>/low_altitude_safety_corridor_dynamics_pipeline_v2.py" \
  --era5_root "<ERA5_ROOT>" \
  --city_level_root "<ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL" \
  --cities China_GBA China_JJJ China_YRD Japan_Kanto USA_NYC UK_London Germany_RhineRuhr Singapore_Johor_Riau UAE_Dubai_AbuDhabi India_DelhiNCR Brazil_SaoPaulo Australia_Sydney Nigeria_Lagos \
  --state_group event_gust_lead event_gust_core event_gust_lag event_gust_leadlag event_shear_lead event_shear_core event_shear_lag event_shear_leadlag \
  --responses var ar1 \
  --year0 2015 --year1 2025 \
  --tau 0.10 \
  --roll_win 24 \
  --neigh 3 \
  --sample_per_file 12000 \
  --max_samples 1200000 \
  --support_bins 70 \
  --support_min_count 5 \
  --grid_res 180 \
  --quantiles 0.05 0.10 0.25 0.50 0.75 0.90 0.95 \
  --critical_lo 0.10 \
  --critical_hi 0.90 \
  --critical_band_q 0.90 \
  --min_city_points 200 \
  --min_city_points_floor 2 \
  --city_output_points_floor 1 \
  --per_city_train_cap 20000 \
  --min_pooled_train 600 \
  --min_quantile_samples 250 \
  --global_max_train 800000 \
  --bootstrap_B 80 \
  --bootstrap_seed 2026 \
  --bootstrap_max_train 250000 \
  --loco_max_train 200000 \
  --allow_extrapolation \
  --soft_clip_qlo 0.01 \
  --soft_clip_qhi 0.99 \
  --make_corridors \
  --mosaic_cols 3 \
  --ph_alpha 0.65 \
  --ph_top_k 1 \
  --ph_persistence_mode quantile \
  --ph_persistence_value 0.50 \
  --ph_make_skeleton \
  --make_percolation \
  --perc_levels 31 \
  --perc_connectivity 4 \
  --perc_smooth_win 5 \
  --perc_tau_fit \
  --tau_fit_bins 22 \
  --tau_smin 2 \
  --tau_smax_quantile 0.95 \
  --tau_fit_min_points 10 \
  --scaling_window_frac 0.25 \
  --scaling_min_points 8 \
  --scaling_r2_min 0.55 \
  --day_hour_start 8 \
  --day_hour_end 18 \
  --shear_q 0.50 \
  --shear_low_q 0.30 \
  --shear_high_q 0.70 \
  --shear_extreme_q 0.90 \
  --gust_high_q 0.70 \
  --gust_extreme_q 0.90 \
  --blh_low_q 0.30 \
  --blh_high_q 0.70 \
  --event_lead_hours 6 \
  --event_lag_hours 6 \
  --event_min_gap_hours 6
  
  
一次性运行两类

/opt/anaconda3/envs/raynode/bin/python "<PROJECT_ROOT>/low_altitude_safety_corridor_dynamics_pipeline_v2.py" \
  --era5_root "<ERA5_ROOT>" \
  --city_level_root "<ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL" \
  --cities China_GBA China_JJJ China_YRD Japan_Kanto USA_NYC UK_London Germany_RhineRuhr Singapore_Johor_Riau UAE_Dubai_AbuDhabi India_DelhiNCR Brazil_SaoPaulo Australia_Sydney Nigeria_Lagos \
  --state_group \
    day night stable_like unstable_like shear_weak shear_moderate shear_extreme gust_high gust_extreme stable_shear_high gust_shear_compound \
    event_gust_lead event_gust_core event_gust_lag event_gust_leadlag event_shear_lead event_shear_core event_shear_lag event_shear_leadlag \
  --responses var ar1 \
  --year0 2015 --year1 2025 \
  --tau 0.10 \
  --roll_win 24 \
  --neigh 3 \
  --sample_per_file 12000 \
  --max_samples 1200000 \
  --support_bins 70 \
  --support_min_count 5 \
  --grid_res 180 \
  --quantiles 0.05 0.10 0.25 0.50 0.75 0.90 0.95 \
  --critical_lo 0.10 \
  --critical_hi 0.90 \
  --critical_band_q 0.90 \
  --min_city_points 200 \
  --min_city_points_floor 2 \
  --city_output_points_floor 1 \
  --per_city_train_cap 20000 \
  --min_pooled_train 600 \
  --min_quantile_samples 250 \
  --global_max_train 800000 \
  --bootstrap_B 80 \
  --bootstrap_seed 2026 \
  --bootstrap_max_train 250000 \
  --loco_max_train 200000 \
  --allow_extrapolation \
  --soft_clip_qlo 0.01 \
  --soft_clip_qhi 0.99 \
  --make_corridors \
  --mosaic_cols 3 \
  --ph_alpha 0.65 \
  --ph_top_k 1 \
  --ph_persistence_mode quantile \
  --ph_persistence_value 0.50 \
  --ph_make_skeleton \
  --make_percolation \
  --perc_levels 31 \
  --perc_connectivity 4 \
  --perc_smooth_win 5 \
  --perc_tau_fit \
  --tau_fit_bins 22 \
  --tau_smin 2 \
  --tau_smax_quantile 0.95 \
  --tau_fit_min_points 10 \
  --scaling_window_frac 0.25 \
  --scaling_min_points 8 \
  --scaling_r2_min 0.55 \
  --day_hour_start 8 \
  --day_hour_end 18 \
  --shear_q 0.50 \
  --shear_low_q 0.30 \
  --shear_high_q 0.70 \
  --shear_extreme_q 0.90 \
  --gust_high_q 0.70 \
  --gust_extreme_q 0.90 \
  --blh_low_q 0.30 \
  --blh_high_q 0.70 \
  --event_lead_hours 6 \
  --event_lag_hours 6 \
  --event_min_gap_hours 6
  
"""

import os
import glob
import json
import math
import zipfile
import argparse
import warnings
import tempfile
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import GradientBoostingRegressor

try:
    from scipy.ndimage import label as cc_label
    from scipy.ndimage import gaussian_filter1d
except Exception:
    cc_label = None
    gaussian_filter1d = None

try:
    import numba
    from numba import njit
    _HAS_NUMBA = True
except Exception:
    _HAS_NUMBA = False

try:
    import gudhi as gd
    _HAS_GUDHI = True
except Exception:
    gd = None
    _HAS_GUDHI = False

try:
    from skimage.morphology import skeletonize
    _HAS_SKIMAGE = True
except Exception:
    skeletonize = None
    _HAS_SKIMAGE = False

EPS = 1e-12


# =========================================================
# Plot defaults
# =========================================================
def set_topjournal_rcparams():
    matplotlib.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "axes.linewidth": 1.1,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "xtick.major.width": 1.0,
        "ytick.major.width": 1.0,
        "legend.fontsize": 9.5,
        "legend.frameon": False,
        "figure.dpi": 120,
        "savefig.dpi": 350,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "axes.grid": False,
        "grid.alpha": 0.25,
        "lines.linewidth": 1.7,
    })


# =========================================================
# Utilities
# =========================================================
def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def month_iter(year0=2015, year1=2025):
    for y in range(year0, year1 + 1):
        for m in range(1, 13):
            yield y, m


def zip_nc_path(city_dir, city, y, m):
    return os.path.join(city_dir, f"ERA5_{city}_{y}{m:02d}_low_altitude_RLCC.zip")


def find_all_cities(era5_root):
    out = []
    for d in sorted(glob.glob(os.path.join(era5_root, "*"))):
        if os.path.isdir(d) and (not os.path.basename(d).startswith("_")):
            out.append(os.path.basename(d))
    return out


def savefig(path, dpi=350):
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()


def safe_div(a, b, fill=np.nan):
    a = float(a)
    b = float(b)
    if (not np.isfinite(a)) or (not np.isfinite(b)) or (abs(b) <= EPS):
        return float(fill)
    return float(a / b)


def shannon_entropy(p):
    p = np.asarray(p, dtype=float)
    s = np.nansum(p)
    if (not np.isfinite(s)) or (s <= 0):
        return 0.0
    p = np.clip(p / (s + EPS), EPS, 1.0)
    H = -np.sum(p * np.log(p))
    return float(H / np.log(len(p)))


def gini_1d(x):
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan
    x = np.clip(x, 0.0, None)
    s = x.sum()
    if s <= 0:
        return 0.0
    x = np.sort(x / s)
    n = len(x)
    return float(1.0 - 2.0 * np.sum(np.cumsum(x)) / n + (n + 1.0) / n)


def robust_slope(y):
    y = np.asarray(y, dtype=float)
    y = y[np.isfinite(y)]
    if len(y) < 10:
        return np.nan
    lo, hi = np.percentile(y, [1, 99])
    y = y[(y >= lo) & (y <= hi)]
    if len(y) < 10:
        return np.nan
    x = np.arange(len(y), dtype=float)
    x -= x.mean()
    y -= y.mean()
    den = np.sum(x * x)
    if den <= 0:
        return np.nan
    return float(np.sum(x * y) / den)


def pinball_loss(y_true, y_pred, q):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    u = y_true - y_pred
    return float(np.nanmean(np.maximum(q * u, (q - 1.0) * u)))


def finite_mask_2col(X, y=None):
    X = np.asarray(X, dtype=float)
    m = np.isfinite(X[:, 0]) & np.isfinite(X[:, 1])
    if y is not None:
        y = np.asarray(y, dtype=float)
        m = m & np.isfinite(y)
    return m


def nan_moving_average(x, win=7):
    x = np.asarray(x, dtype=float)
    if win <= 1:
        return x.copy()
    out = np.full_like(x, np.nan, dtype=float)
    n = len(x)
    for i in range(n):
        lo = max(0, i - win // 2)
        hi = min(n, i + win // 2 + 1)
        seg = x[lo:hi]
        seg = seg[np.isfinite(seg)]
        if len(seg) > 0:
            out[i] = float(np.mean(seg))
    return out


def smooth_1d(x, win=5):
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return x.copy()
    if gaussian_filter1d is not None and int(win) > 1:
        sigma = max(0.5, float(win) / 3.0)
        xf = np.where(np.isfinite(x), x, np.nan)
        if np.all(~np.isfinite(xf)):
            return x.copy()
        fill = np.nanmedian(xf[np.isfinite(xf)])
        xs = xf.copy()
        xs[~np.isfinite(xs)] = fill
        ys = gaussian_filter1d(xs, sigma=sigma, mode="nearest")
        ys[~np.isfinite(xf)] = np.nan
        return ys
    return nan_moving_average(x, win=win)


def qc_flag_from_points(valid_points: int, floor_out: int, floor_train_label_only: int, min_city_points: int) -> str:
    vp = int(valid_points)
    if vp < int(floor_out):
        return "OUT_FAIL"
    if vp < int(floor_train_label_only):
        return "OUT_OK_TRAIN_FAIL"
    if vp < int(min_city_points):
        return "OUT_OK_TRAIN_OK_SIG_FAIL"
    return "OUT_OK_TRAIN_OK_SIG_OK"


def soft_clip_w_pred(W_pred, support_ok, q1=0.01, q2=0.99):
    W_pred = np.asarray(W_pred, dtype=np.float64)
    support_ok = np.asarray(support_ok, dtype=bool)

    ref = W_pred[np.isfinite(W_pred) & support_ok]
    if ref.size < 50:
        return W_pred

    lo = float(np.quantile(ref, float(q1)))
    hi = float(np.quantile(ref, float(q2)))
    if (not np.isfinite(lo)) or (not np.isfinite(hi)) or (hi <= lo):
        return W_pred
    return np.clip(W_pred, lo, hi)


def safe_vmin_vmax_from_arrays(arr_list, qlo=0.02, qhi=0.98, fallback=(0.0, 1.0)):
    vals = []
    for a in arr_list:
        if a is None:
            continue
        x = np.asarray(a, dtype=np.float64).ravel()
        x = x[np.isfinite(x)]
        if x.size > 0:
            vals.append(x)
    if len(vals) == 0:
        return float(fallback[0]), float(fallback[1])
    x = np.concatenate(vals)
    if x.size == 0:
        return float(fallback[0]), float(fallback[1])
    vmin = float(np.quantile(x, float(qlo)))
    vmax = float(np.quantile(x, float(qhi)))
    if (not np.isfinite(vmin)) or (not np.isfinite(vmax)) or (vmax <= vmin):
        return float(fallback[0]), float(fallback[1])
    return vmin, vmax


# =========================================================
# ERA5 reading
# =========================================================
def _import_xarray():
    try:
        import xarray as xr
        return xr
    except Exception as e:
        raise RuntimeError(
            "xarray is required. Install:\n"
            "  conda install -c conda-forge xarray netcdf4 h5netcdf scipy\n"
            f"Original error: {e}"
        )


@dataclass
class VarSpec:
    name: str
    kind: str
    candidates: List[str]
    u_candidates: Optional[List[str]] = None
    v_candidates: Optional[List[str]] = None


def build_var_specs():
    return {
        "gust": VarSpec(
            name="gust",
            kind="single",
            candidates=[
                "i10fg", "instantaneous_10m_wind_gust", "10m_wind_gust",
                "fg10", "gust", "wind_gust"
            ],
        ),
        "wind10": VarSpec(
            name="wind10",
            kind="speed",
            candidates=[],
            u_candidates=["u10", "10m_u_component_of_wind"],
            v_candidates=["v10", "10m_v_component_of_wind"],
        ),
        "wind100": VarSpec(
            name="wind100",
            kind="speed",
            candidates=[],
            u_candidates=["u100", "100m_u_component_of_wind"],
            v_candidates=["v100", "100m_v_component_of_wind"],
        ),
        "blh": VarSpec(
            name="blh",
            kind="single",
            candidates=["blh", "boundary_layer_height"],
        ),
        "t2m": VarSpec(
            name="t2m",
            kind="single",
            candidates=["t2m", "2m_temperature"],
        ),
    }


def open_zip_dataset(zip_path):
    xr = _import_xarray()
    if not os.path.exists(zip_path):
        return None, None

    tmp_path = None
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            ncs = [n for n in zf.namelist() if n.lower().endswith(".nc")]
            if len(ncs) == 0:
                return None, None
            ncname = ncs[0]

            fd, tmp_path = tempfile.mkstemp(suffix=".nc", prefix="era5_zip_")
            os.close(fd)
            with zf.open(ncname) as f_in, open(tmp_path, "wb") as f_out:
                f_out.write(f_in.read())

        ds = None
        last_err = None
        for eng in ["netcdf4", "h5netcdf", None]:
            try:
                if eng is None:
                    ds = xr.open_dataset(tmp_path)
                else:
                    ds = xr.open_dataset(tmp_path, engine=eng)
                break
            except Exception as e:
                last_err = e
                ds = None

        if ds is None:
            raise RuntimeError(f"Failed to open nc with xarray engines. Last error: {last_err}")

        ds.attrs["_tmp_nc_path"] = tmp_path
        return ds, tmp_path

    except Exception:
        try:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
        raise


def close_dataset_and_cleanup(ds):
    if ds is None:
        return
    tmp_path = None
    try:
        tmp_path = ds.attrs.get("_tmp_nc_path", None)
    except Exception:
        tmp_path = None
    try:
        ds.close()
    except Exception:
        pass
    if tmp_path and isinstance(tmp_path, str) and os.path.exists(tmp_path):
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def extract_value_array(ds, var_key, varspec: VarSpec):
    lat_name = None
    lon_name = None
    for cand in ["latitude", "lat"]:
        if cand in ds.coords:
            lat_name = cand
            break
    for cand in ["longitude", "lon"]:
        if cand in ds.coords:
            lon_name = cand
            break
    if lat_name is None or lon_name is None:
        raise ValueError("Cannot find latitude/longitude coordinates")

    tname = None
    for cand in ["time", "valid_time"]:
        if cand in ds.coords:
            tname = cand
            break
    if tname is None:
        raise ValueError("Cannot find time coordinate")

    ds_vars = list(ds.data_vars.keys())

    if varspec.kind == "single":
        arr = None
        for cand in varspec.candidates:
            if cand in ds_vars:
                arr = ds[cand].values.astype(np.float32)
                break
        if arr is None:
            raise ValueError(
                f"Variable '{var_key}' not found. Candidates={varspec.candidates}, ds_vars={ds_vars}"
            )
    else:
        u = None
        v = None
        for cand in varspec.u_candidates or []:
            if cand in ds_vars:
                u = cand
                break
        for cand in varspec.v_candidates or []:
            if cand in ds_vars:
                v = cand
                break
        if u is None or v is None:
            raise ValueError(
                f"Wind components not found for '{var_key}'. "
                f"u_candidates={varspec.u_candidates}, v_candidates={varspec.v_candidates}, ds_vars={ds_vars}"
            )
        uu = ds[u].values.astype(np.float32)
        vv = ds[v].values.astype(np.float32)
        arr = np.sqrt(uu * uu + vv * vv).astype(np.float32)

    lats = ds[lat_name].values.astype(np.float32)
    lons = ds[lon_name].values.astype(np.float32)
    tt = ds[tname].values
    times = pd.to_datetime(tt)
    hours = times.hour.astype(np.int16)
    return arr, lats, lons, hours, times


# =========================================================
# State groups
# =========================================================
VALID_STATE_GROUPS = {
    "all",
    "day",
    "night",

    "stable_like",
    "unstable_like",
    "stable_lowblh",
    "unstable_highblh",

    "shear_low",
    "shear_high",
    "shear_weak",
    "shear_moderate",
    "shear_extreme",

    "gust_high",
    "gust_extreme",

    "stable_shear_high",
    "unstable_shear_high",
    "gust_shear_compound",
    "stable_gust_extreme",

    "event_gust_lead",
    "event_gust_core",
    "event_gust_lag",
    "event_gust_leadlag",
    "event_shear_lead",
    "event_shear_core",
    "event_shear_lag",
    "event_shear_leadlag",
}


def is_day_hour(hour_arr: np.ndarray, day_hour_start: int = 8, day_hour_end: int = 18) -> np.ndarray:
    h = np.asarray(hour_arr).astype(int)
    return (h >= int(day_hour_start)) & (h < int(day_hour_end))


def _hourly_spatial_mean(arr: Optional[np.ndarray]) -> Optional[np.ndarray]:
    if arr is None:
        return None
    return np.nanmean(arr, axis=(1, 2))


def _compute_hourly_shear(arr_w10: Optional[np.ndarray], arr_w100: Optional[np.ndarray]) -> Optional[np.ndarray]:
    if arr_w10 is None or arr_w100 is None:
        return None
    return np.nanmean(arr_w100 - arr_w10, axis=(1, 2))


def _monthly_quantile_mask(x: np.ndarray, q: float, side: str) -> np.ndarray:
    """
    side:
      - 'low'
      - 'high'
    """
    out = np.zeros_like(x, dtype=bool)
    finite = np.isfinite(x)
    if np.sum(finite) < max(24, len(x) // 5):
        return out
    thr = float(np.nanquantile(x[finite], float(q)))
    if side == "low":
        out = np.isfinite(x) & (x <= thr)
    else:
        out = np.isfinite(x) & (x >= thr)
    return out


def _monthly_three_way_mask(x: np.ndarray, qlo: float, qhi: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Returns weak / moderate / extreme for the given monthly series.
    """
    finite = np.isfinite(x)
    low = np.zeros_like(x, dtype=bool)
    mid = np.zeros_like(x, dtype=bool)
    high = np.zeros_like(x, dtype=bool)
    if np.sum(finite) < max(24, len(x) // 5):
        return low, mid, high

    thr_lo = float(np.nanquantile(x[finite], float(qlo)))
    thr_hi = float(np.nanquantile(x[finite], float(qhi)))

    low = np.isfinite(x) & (x <= thr_lo)
    high = np.isfinite(x) & (x >= thr_hi)
    mid = np.isfinite(x) & (x > thr_lo) & (x < thr_hi)
    return low, mid, high


def _detect_event_core_mask(
    x: np.ndarray,
    q_extreme: float,
    min_gap_hours: int = 6,
) -> np.ndarray:
    """
    Detect event-core hours from a monthly hourly diagnostic.
    Step:
      1) threshold by monthly quantile
      2) collapse adjacent/nearby hours into sparse event-core markers
    """
    core = np.zeros_like(x, dtype=bool)
    finite = np.isfinite(x)
    if np.sum(finite) < max(24, len(x) // 5):
        return core

    thr = float(np.nanquantile(x[finite], float(q_extreme)))
    cand = np.isfinite(x) & (x >= thr)
    idx = np.where(cand)[0]
    if len(idx) == 0:
        return core

    selected = [int(idx[0])]
    for ii in idx[1:]:
        if int(ii) - int(selected[-1]) >= int(min_gap_hours):
            selected.append(int(ii))
        else:
            if x[ii] > x[selected[-1]]:
                selected[-1] = int(ii)

    core[np.array(selected, dtype=int)] = True
    return core


def _expand_event_window(core_mask: np.ndarray, lead_hours: int, lag_hours: int) -> np.ndarray:
    n = len(core_mask)
    out = np.zeros(n, dtype=bool)
    idx = np.where(core_mask)[0]
    for ii in idx:
        lo = max(0, int(ii) - int(lead_hours))
        hi = min(n, int(ii) + int(lag_hours) + 1)
        out[lo:hi] = True
    return out


def _derive_event_masks(
    x: np.ndarray,
    q_extreme: float,
    event_lead_hours: int,
    event_lag_hours: int,
    min_gap_hours: int,
) -> Dict[str, np.ndarray]:
    core = _detect_event_core_mask(
        x=x,
        q_extreme=q_extreme,
        min_gap_hours=min_gap_hours,
    )
    lead = np.zeros_like(core, dtype=bool)
    lag = np.zeros_like(core, dtype=bool)

    idx = np.where(core)[0]
    for ii in idx:
        lo = max(0, int(ii) - int(event_lead_hours))
        hi = min(len(core), int(ii) + int(event_lag_hours) + 1)
        if lo < int(ii):
            lead[lo:int(ii)] = True
        if int(ii) + 1 < hi:
            lag[int(ii) + 1:hi] = True

    leadlag = _expand_event_window(core, event_lead_hours, event_lag_hours)
    return {
        "core": core,
        "lead": lead,
        "lag": lag,
        "leadlag": leadlag,
    }


def compute_state_mask_for_month(
    state_group: str,
    hours: np.ndarray,
    arr_w10: Optional[np.ndarray] = None,
    arr_w100: Optional[np.ndarray] = None,
    arr_blh: Optional[np.ndarray] = None,
    arr_gust: Optional[np.ndarray] = None,
    day_hour_start: int = 8,
    day_hour_end: int = 18,
    shear_q: float = 0.50,
    shear_low_q: float = 0.30,
    shear_high_q: float = 0.70,
    shear_extreme_q: float = 0.90,
    gust_high_q: float = 0.70,
    gust_extreme_q: float = 0.90,
    blh_low_q: float = 0.30,
    blh_high_q: float = 0.70,
    event_lead_hours: int = 6,
    event_lag_hours: int = 6,
    event_min_gap_hours: int = 6,
) -> np.ndarray:
    """
    Central upgraded state-definition function.

    Key monthly diagnostics:
      - hourly mean BLH
      - hourly mean gust
      - hourly mean shear = wind100 - wind10
      - day/night

    The goal is not only static partitioning, but dynamic-event conditioning.
    """
    state_group = str(state_group)
    if state_group not in VALID_STATE_GROUPS:
        raise ValueError(f"Unknown state_group={state_group}")

    T = len(hours)
    day_mask = is_day_hour(hours, day_hour_start=day_hour_start, day_hour_end=day_hour_end)
    night_mask = ~day_mask

    if state_group == "all":
        return np.ones(T, dtype=bool)

    if state_group == "day":
        return day_mask.copy()

    if state_group == "night":
        return night_mask.copy()

    shear_h = _compute_hourly_shear(arr_w10, arr_w100)
    gust_h = _hourly_spatial_mean(arr_gust)
    blh_h = _hourly_spatial_mean(arr_blh)

    # ---------------- original-like BLH states ----------------
    if state_group in {"stable_like", "unstable_like"}:
        if blh_h is None:
            raise ValueError("stable_like/unstable_like requires BLH")
        finite = np.isfinite(blh_h)
        if np.sum(finite) < max(24, T // 5):
            return np.zeros(T, dtype=bool)
        thr_lo = float(np.nanquantile(blh_h[finite], float(blh_low_q)))
        thr_hi = float(np.nanquantile(blh_h[finite], float(blh_high_q)))
        if state_group == "stable_like":
            return night_mask & np.isfinite(blh_h) & (blh_h <= thr_lo)
        else:
            return day_mask & np.isfinite(blh_h) & (blh_h >= thr_hi)

    # ---------------- strengthened BLH states ----------------
    if state_group == "stable_lowblh":
        if blh_h is None:
            raise ValueError("stable_lowblh requires BLH")
        return night_mask & _monthly_quantile_mask(blh_h, blh_low_q, side="low")

    if state_group == "unstable_highblh":
        if blh_h is None:
            raise ValueError("unstable_highblh requires BLH")
        return day_mask & _monthly_quantile_mask(blh_h, blh_high_q, side="high")

    # ---------------- shear states ----------------
    if state_group in {"shear_low", "shear_high"}:
        if shear_h is None:
            raise ValueError("shear_low/high requires wind10 and wind100")
        finite = np.isfinite(shear_h)
        if np.sum(finite) < max(24, T // 5):
            return np.zeros(T, dtype=bool)
        thr = float(np.nanquantile(shear_h[finite], float(shear_q)))
        if state_group == "shear_low":
            return np.isfinite(shear_h) & (shear_h <= thr)
        else:
            return np.isfinite(shear_h) & (shear_h > thr)

    if state_group in {"shear_weak", "shear_moderate", "shear_extreme"}:
        if shear_h is None:
            raise ValueError("shear_weak/moderate/extreme requires wind10 and wind100")
        weak, moderate, extreme = _monthly_three_way_mask(shear_h, qlo=shear_low_q, qhi=shear_extreme_q)
        if state_group == "shear_weak":
            return weak
        if state_group == "shear_moderate":
            return moderate
        return extreme

    # ---------------- gust states ----------------
    if state_group == "gust_high":
        if gust_h is None:
            raise ValueError("gust_high requires gust")
        return _monthly_quantile_mask(gust_h, gust_high_q, side="high")

    if state_group == "gust_extreme":
        if gust_h is None:
            raise ValueError("gust_extreme requires gust")
        return _monthly_quantile_mask(gust_h, gust_extreme_q, side="high")

    # ---------------- compound states ----------------
    if state_group == "stable_shear_high":
        if blh_h is None or shear_h is None:
            raise ValueError("stable_shear_high requires BLH + wind10 + wind100")
        stable = night_mask & _monthly_quantile_mask(blh_h, blh_low_q, side="low")
        shigh = _monthly_quantile_mask(shear_h, shear_high_q, side="high")
        return stable & shigh

    if state_group == "unstable_shear_high":
        if blh_h is None or shear_h is None:
            raise ValueError("unstable_shear_high requires BLH + wind10 + wind100")
        unstable = day_mask & _monthly_quantile_mask(blh_h, blh_high_q, side="high")
        shigh = _monthly_quantile_mask(shear_h, shear_high_q, side="high")
        return unstable & shigh

    if state_group == "gust_shear_compound":
        if gust_h is None or shear_h is None:
            raise ValueError("gust_shear_compound requires gust + wind10 + wind100")
        gext = _monthly_quantile_mask(gust_h, gust_extreme_q, side="high")
        sext = _monthly_quantile_mask(shear_h, shear_extreme_q, side="high")
        return gext & sext

    if state_group == "stable_gust_extreme":
        if gust_h is None or blh_h is None:
            raise ValueError("stable_gust_extreme requires gust + BLH")
        stable = night_mask & _monthly_quantile_mask(blh_h, blh_low_q, side="low")
        gext = _monthly_quantile_mask(gust_h, gust_extreme_q, side="high")
        return stable & gext

    # ---------------- event windows: gust ----------------
    if state_group in {
        "event_gust_lead", "event_gust_core", "event_gust_lag", "event_gust_leadlag"
    }:
        if gust_h is None:
            raise ValueError("event_gust_* requires gust")
        ev = _derive_event_masks(
            x=gust_h,
            q_extreme=gust_extreme_q,
            event_lead_hours=event_lead_hours,
            event_lag_hours=event_lag_hours,
            min_gap_hours=event_min_gap_hours,
        )
        if state_group == "event_gust_lead":
            return ev["lead"]
        if state_group == "event_gust_core":
            return ev["core"]
        if state_group == "event_gust_lag":
            return ev["lag"]
        return ev["leadlag"]

    # ---------------- event windows: shear ----------------
    if state_group in {
        "event_shear_lead", "event_shear_core", "event_shear_lag", "event_shear_leadlag"
    }:
        if shear_h is None:
            raise ValueError("event_shear_* requires wind10 + wind100")
        ev = _derive_event_masks(
            x=shear_h,
            q_extreme=shear_extreme_q,
            event_lead_hours=event_lead_hours,
            event_lag_hours=event_lag_hours,
            min_gap_hours=event_min_gap_hours,
        )
        if state_group == "event_shear_lead":
            return ev["lead"]
        if state_group == "event_shear_core":
            return ev["core"]
        if state_group == "event_shear_lag":
            return ev["lag"]
        return ev["leadlag"]

    return np.zeros(T, dtype=bool)


# =========================================================
# Threshold estimation under dynamic-state conditioning
# =========================================================
def estimate_city_threshold_state_conditioned(
    era5_root: str,
    city: str,
    target_varspec: VarSpec,
    state_group: str,
    tau: float = 0.10,
    year0: int = 2015,
    year1: int = 2025,
    max_samples: int = 1500000,
    sample_per_file: int = 12000,
    seed: int = 42,
    day_hour_start: int = 8,
    day_hour_end: int = 18,
    shear_q: float = 0.50,
    shear_low_q: float = 0.30,
    shear_high_q: float = 0.70,
    shear_extreme_q: float = 0.90,
    gust_high_q: float = 0.70,
    gust_extreme_q: float = 0.90,
    blh_low_q: float = 0.30,
    blh_high_q: float = 0.70,
    event_lead_hours: int = 6,
    event_lag_hours: int = 6,
    event_min_gap_hours: int = 6,
) -> float:
    """
    Estimate city-specific exceedance threshold for target variable using only
    hours belonging to the chosen state group.
    """
    rng = np.random.default_rng(int(seed))
    city_dir = os.path.join(era5_root, city)
    samples = []
    var_specs = build_var_specs()

    need_w10 = state_group in {
        "shear_low", "shear_high", "shear_weak", "shear_moderate", "shear_extreme",
        "stable_shear_high", "unstable_shear_high", "gust_shear_compound",
        "event_shear_lead", "event_shear_core", "event_shear_lag", "event_shear_leadlag"
    }
    need_w100 = need_w10
    need_blh = state_group in {
        "stable_like", "unstable_like", "stable_lowblh", "unstable_highblh",
        "stable_shear_high", "unstable_shear_high", "stable_gust_extreme"
    }
    need_gust = state_group in {
        "gust_high", "gust_extreme", "gust_shear_compound", "stable_gust_extreme",
        "event_gust_lead", "event_gust_core", "event_gust_lag", "event_gust_leadlag"
    }

    for y, m in month_iter(year0, year1):
        zp = zip_nc_path(city_dir, city, y, m)
        if not os.path.exists(zp):
            continue

        ds, _ = open_zip_dataset(zp)
        if ds is None:
            continue

        try:
            arr_tar, _, _, hours, _ = extract_value_array(ds, target_varspec.name, target_varspec)

            arr_w10 = None
            arr_w100 = None
            arr_blh = None
            arr_gust = None

            if need_w10:
                arr_w10, _, _, _, _ = extract_value_array(ds, "wind10", var_specs["wind10"])
            if need_w100:
                arr_w100, _, _, _, _ = extract_value_array(ds, "wind100", var_specs["wind100"])
            if need_blh:
                arr_blh, _, _, _, _ = extract_value_array(ds, "blh", var_specs["blh"])
            if need_gust:
                arr_gust, _, _, _, _ = extract_value_array(ds, "gust", var_specs["gust"])

            smask = compute_state_mask_for_month(
                state_group=state_group,
                hours=hours,
                arr_w10=arr_w10,
                arr_w100=arr_w100,
                arr_blh=arr_blh,
                arr_gust=arr_gust,
                day_hour_start=day_hour_start,
                day_hour_end=day_hour_end,
                shear_q=shear_q,
                shear_low_q=shear_low_q,
                shear_high_q=shear_high_q,
                shear_extreme_q=shear_extreme_q,
                gust_high_q=gust_high_q,
                gust_extreme_q=gust_extreme_q,
                blh_low_q=blh_low_q,
                blh_high_q=blh_high_q,
                event_lead_hours=event_lead_hours,
                event_lag_hours=event_lag_hours,
                event_min_gap_hours=event_min_gap_hours,
            )

            idx_t = np.where(smask)[0]
            if len(idx_t) == 0:
                continue

            sub = arr_tar[idx_t, :, :]
            flat = sub.reshape(-1)
            finite_idx = np.where(np.isfinite(flat))[0]
            if len(finite_idx) == 0:
                continue

            n_take = int(min(sample_per_file, len(finite_idx)))
            pick = rng.choice(finite_idx, size=n_take, replace=False)
            samples.append(flat[pick].astype(np.float32))

            if sum(len(s) for s in samples) >= int(max_samples):
                break

        finally:
            close_dataset_and_cleanup(ds)

    if len(samples) == 0:
        raise RuntimeError(
            f"[{city}/{target_varspec.name}/{state_group}] "
            f"No usable samples found for threshold estimation."
        )

    x = np.concatenate(samples).astype(np.float64)
    x = x[np.isfinite(x)]
    if len(x) < 1000:
        raise RuntimeError(
            f"[{city}/{target_varspec.name}/{state_group}] "
            f"Too few samples for threshold estimation: n={len(x)}"
        )

    q = float(np.quantile(x, 1.0 - float(tau)))
    return q


# =========================================================
# Dynamic-state-conditioned grid products
# =========================================================
def build_grid_products_state_conditioned(
    era5_root: str,
    city: str,
    target_varspec: VarSpec,
    state_group: str,
    thr: float,
    ews_on: str,
    year0: int = 2015,
    year1: int = 2025,
    day_hour_start: int = 8,
    day_hour_end: int = 18,
    shear_q: float = 0.50,
    shear_low_q: float = 0.30,
    shear_high_q: float = 0.70,
    shear_extreme_q: float = 0.90,
    gust_high_q: float = 0.70,
    gust_extreme_q: float = 0.90,
    blh_low_q: float = 0.30,
    blh_high_q: float = 0.70,
    event_lead_hours: int = 6,
    event_lag_hours: int = 6,
    event_min_gap_hours: int = 6,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """
    Build exceedance climatology and monthly EWS series using only selected state hours.
    Returns:
      lat, lon, clim_ex, monthly_series_ews, meta
    """
    city_dir = os.path.join(era5_root, city)
    var_specs = build_var_specs()

    lat = None
    lon = None

    sum_ex = None
    cnt_ex = np.zeros((12, 24), dtype=np.float64)
    monthly_list_ews = []

    used_hours_total = 0
    total_hours_total = 0
    used_months = 0
    event_hours_total = 0

    need_w10 = state_group in {
        "shear_low", "shear_high", "shear_weak", "shear_moderate", "shear_extreme",
        "stable_shear_high", "unstable_shear_high", "gust_shear_compound",
        "event_shear_lead", "event_shear_core", "event_shear_lag", "event_shear_leadlag"
    }
    need_w100 = need_w10
    need_blh = state_group in {
        "stable_like", "unstable_like", "stable_lowblh", "unstable_highblh",
        "stable_shear_high", "unstable_shear_high", "stable_gust_extreme"
    }
    need_gust = state_group in {
        "gust_high", "gust_extreme", "gust_shear_compound", "stable_gust_extreme",
        "event_gust_lead", "event_gust_core", "event_gust_lag", "event_gust_leadlag"
    }

    for y, m in month_iter(year0, year1):
        zp = zip_nc_path(city_dir, city, y, m)
        if not os.path.exists(zp):
            continue

        ds, _ = open_zip_dataset(zp)
        if ds is None:
            continue

        try:
            arr_tar, lats, lons, hours, _ = extract_value_array(ds, target_varspec.name, target_varspec)

            arr_w10 = None
            arr_w100 = None
            arr_blh = None
            arr_gust = None

            if need_w10:
                arr_w10, _, _, _, _ = extract_value_array(ds, "wind10", var_specs["wind10"])
            if need_w100:
                arr_w100, _, _, _, _ = extract_value_array(ds, "wind100", var_specs["wind100"])
            if need_blh:
                arr_blh, _, _, _, _ = extract_value_array(ds, "blh", var_specs["blh"])
            if need_gust:
                arr_gust, _, _, _, _ = extract_value_array(ds, "gust", var_specs["gust"])

            smask = compute_state_mask_for_month(
                state_group=state_group,
                hours=hours,
                arr_w10=arr_w10,
                arr_w100=arr_w100,
                arr_blh=arr_blh,
                arr_gust=arr_gust,
                day_hour_start=day_hour_start,
                day_hour_end=day_hour_end,
                shear_q=shear_q,
                shear_low_q=shear_low_q,
                shear_high_q=shear_high_q,
                shear_extreme_q=shear_extreme_q,
                gust_high_q=gust_high_q,
                gust_extreme_q=gust_extreme_q,
                blh_low_q=blh_low_q,
                blh_high_q=blh_high_q,
                event_lead_hours=event_lead_hours,
                event_lag_hours=event_lag_hours,
                event_min_gap_hours=event_min_gap_hours,
            )

            total_hours_total += int(len(hours))
            used_hours_total += int(np.sum(smask))

            if state_group.startswith("event_"):
                event_hours_total += int(np.sum(smask))

            idx_t = np.where(smask)[0]
            if len(idx_t) == 0:
                continue

            arr = arr_tar[idx_t, :, :]
            hours_sub = hours[idx_t]

            if lat is None:
                lat = lats
                lon = lons
                Ny = len(lat)
                Nx = len(lon)
                sum_ex = np.zeros((12, 24, Ny, Nx), dtype=np.float64)

            ex = (arr > float(thr)).astype(np.float32)
            mm = m - 1
            for hh in range(24):
                idx_h = np.where(hours_sub == hh)[0]
                if len(idx_h) == 0:
                    continue
                eh = np.nanmean(ex[idx_h, :, :], axis=0)
                sum_ex[mm, hh, :, :] += eh
                cnt_ex[mm, hh] += 1.0

            if ews_on == "exceed":
                monthly_ews = np.nanmean(ex, axis=0).astype(np.float32)
            elif ews_on == "raw_mean":
                monthly_ews = np.nanmean(arr, axis=0).astype(np.float32)
            elif ews_on == "raw_p95":
                monthly_ews = np.nanpercentile(arr, 95, axis=0).astype(np.float32)
            else:
                raise ValueError(f"Unknown ews_on={ews_on}")

            if np.any(np.isfinite(monthly_ews)):
                monthly_list_ews.append(monthly_ews)
                used_months += 1

        finally:
            close_dataset_and_cleanup(ds)

    if lat is None or sum_ex is None or len(monthly_list_ews) == 0:
        raise RuntimeError(
            f"[{city}/{target_varspec.name}/{state_group}] "
            f"No valid monthly data assembled."
        )

    clim_ex = np.zeros_like(sum_ex, dtype=np.float32)
    for mm in range(12):
        for hh in range(24):
            c = cnt_ex[mm, hh]
            if c > 0:
                clim_ex[mm, hh, :, :] = (sum_ex[mm, hh, :, :] / c).astype(np.float32)
            else:
                clim_ex[mm, hh, :, :] = 0.0

    monthly_series_ews = np.stack(monthly_list_ews, axis=0).astype(np.float32)

    meta = {
        "state_group": state_group,
        "used_hours_total": int(used_hours_total),
        "total_hours_total": int(total_hours_total),
        "used_hours_frac": safe_div(used_hours_total, total_hours_total, fill=np.nan),
        "used_months": int(used_months),
        "event_hours_total": int(event_hours_total),
    }
    return lat, lon, clim_ex, monthly_series_ews, meta


# =========================================================
# Grid entropy + local dispersion
# =========================================================
if _HAS_NUMBA:
    @njit(cache=True)
    def _local_gini_map_numba(field2d, pad):
        Ny = field2d.shape[0]
        Nx = field2d.shape[1]
        w = 2 * pad + 1
        out = np.empty((Ny, Nx), dtype=np.float64)
        Ny2 = Ny + 2 * pad
        Nx2 = Nx + 2 * pad
        fp = np.empty((Ny2, Nx2), dtype=np.float64)

        for i in range(Ny):
            for j in range(Nx):
                fp[i + pad, j + pad] = field2d[i, j]

        for i in range(pad):
            src = pad + (pad - i)
            for j in range(Nx):
                fp[i, j + pad] = fp[src, j + pad]
            src2 = pad + (Ny - 1 - i)
            for j in range(Nx):
                fp[Ny + pad + i, j + pad] = fp[src2, j + pad]

        for i in range(Ny2):
            for j in range(pad):
                src = pad + (pad - j)
                fp[i, j] = fp[i, src]
            for j in range(pad):
                src2 = pad + (Nx - 1 - j)
                fp[i, Nx + pad + j] = fp[i, src2]

        buf = np.empty((w * w,), dtype=np.float64)
        for i in range(Ny):
            for j in range(Nx):
                k = 0
                for ii in range(w):
                    for jj in range(w):
                        buf[k] = fp[i + ii, j + jj]
                        k += 1

                cnt = 0
                for kk in range(buf.shape[0]):
                    v = buf[kk]
                    if np.isfinite(v):
                        if v < 0.0:
                            v = 0.0
                        buf[cnt] = v
                        cnt += 1
                if cnt <= 0:
                    out[i, j] = np.nan
                    continue
                tmp = np.sort(buf[:cnt])
                s = np.sum(tmp)
                if s <= 0.0:
                    out[i, j] = 0.0
                else:
                    x = tmp / s
                    cs = 0.0
                    csum = 0.0
                    for kk in range(cnt):
                        csum += x[kk]
                        cs += csum
                    out[i, j] = 1.0 - 2.0 * cs / cnt + (cnt + 1.0) / cnt
        return out


def local_gini_map(field2d, neigh=3):
    field2d = np.asarray(field2d, dtype=np.float64)
    Ny, Nx = field2d.shape
    pad = int(neigh)

    if _HAS_NUMBA:
        return _local_gini_map_numba(field2d, pad)

    fp = np.pad(field2d, ((pad, pad), (pad, pad)), mode="reflect")
    out = np.full((Ny, Nx), np.nan, dtype=float)
    w = 2 * pad + 1
    for i in range(Ny):
        for j in range(Nx):
            win = fp[i:i + w, j:j + w].ravel()
            out[i, j] = gini_1d(win)
    return out


def compute_grid_entropy_and_dispersion(clim_exceed, neigh=3):
    clim = np.asarray(clim_exceed, dtype=float)
    _, _, Ny, Nx = clim.shape

    grid_entropy = np.full((Ny, Nx), 0.0, dtype=float)
    flat_len = 12 * 24
    for i in range(Ny):
        for j in range(Nx):
            p = clim[:, :, i, j].reshape(flat_len)
            grid_entropy[i, j] = shannon_entropy(np.nan_to_num(p, nan=0.0))

    num = np.zeros((Ny, Nx), dtype=float)
    den = np.zeros((Ny, Nx), dtype=float)

    for mm in range(12):
        for hh in range(24):
            F0 = np.nan_to_num(clim[mm, hh, :, :], nan=0.0)
            lg = local_gini_map(F0, neigh=neigh)
            w = np.clip(F0, 0.0, None)
            num += np.nan_to_num(lg, nan=0.0) * w
            den += w

    grid_disp = np.divide(num, den + EPS)
    return grid_entropy, grid_disp


# =========================================================
# EWS slopes (AR1 and VAR)
# =========================================================
def rolling_ar1_var(series, win=24):
    x = np.asarray(series, dtype=float)
    T = len(x)
    if T < win + 5:
        return None, None

    ar1 = []
    var = []
    for t in range(win, T + 1):
        seg = x[t - win:t]
        seg = seg[np.isfinite(seg)]
        if len(seg) < max(10, win // 2):
            ar1.append(np.nan)
            var.append(np.nan)
            continue

        var_val = float(np.var(seg, ddof=1)) if len(seg) > 1 else 0.0
        var.append(var_val)

        s0 = seg[:-1]
        s1 = seg[1:]
        if np.std(s0) <= 1e-12 or np.std(s1) <= 1e-12:
            ar1.append(np.nan)
        else:
            ar1.append(float(np.corrcoef(s0, s1)[0, 1]))

    return np.asarray(ar1, dtype=float), np.asarray(var, dtype=float)


def compute_grid_ews(monthly_series, roll_win=24):
    M = np.asarray(monthly_series, dtype=float)
    T, Ny, Nx = M.shape

    ar1_slope = np.full((Ny, Nx), np.nan, dtype=float)
    var_slope = np.full((Ny, Nx), np.nan, dtype=float)

    for i in range(Ny):
        for j in range(Nx):
            ts = M[:, i, j]
            a, v = rolling_ar1_var(ts, win=roll_win)
            if a is None:
                continue
            ar1_slope[i, j] = robust_slope(a)
            var_slope[i, j] = robust_slope(v)

    return ar1_slope, var_slope


# =========================================================
# Support density on phase space
# =========================================================
def support_hist2d(X, bins=60, xlim=None, ylim=None):
    X = np.asarray(X, dtype=float)
    if xlim is None:
        xlim = (np.nanmin(X[:, 0]), np.nanmax(X[:, 0]))
    if ylim is None:
        ylim = (np.nanmin(X[:, 1]), np.nanmax(X[:, 1]))
    xedges = np.linspace(xlim[0], xlim[1], int(bins) + 1)
    yedges = np.linspace(ylim[0], ylim[1], int(bins) + 1)
    H, xe, ye = np.histogram2d(X[:, 0], X[:, 1], bins=[xedges, yedges])
    return H.T, xe, ye


def interp_hist_count_on_grid(xvals, yvals, H_count, xedges, yedges):
    xi = np.searchsorted(xedges, xvals, side="right") - 1
    yi = np.searchsorted(yedges, yvals, side="right") - 1
    xi = np.clip(xi, 0, len(xedges) - 2)
    yi = np.clip(yi, 0, len(yedges) - 2)
    return H_count[yi, xi]


def build_support_mask_on_phase_grid(X_pool, support_bins, support_min_count, grid_res):
    H_count, xedges, yedges = support_hist2d(
        X_pool, bins=int(support_bins),
        xlim=(float(np.nanmin(X_pool[:, 0])), float(np.nanmax(X_pool[:, 0]))),
        ylim=(float(np.nanmin(X_pool[:, 1])), float(np.nanmax(X_pool[:, 1]))),
    )
    gx = np.linspace(xedges[0], xedges[-1], int(grid_res))
    gy = np.linspace(yedges[0], yedges[-1], int(grid_res))
    Xg, Yg = np.meshgrid(gx, gy, indexing="xy")
    count_on_grid = interp_hist_count_on_grid(Xg.ravel(), Yg.ravel(), H_count, xedges, yedges).reshape(Xg.shape)
    mask_on_grid = (count_on_grid >= float(support_min_count)).astype(np.uint8)
    return H_count, xedges, yedges, gx, gy, Xg, Yg, mask_on_grid, count_on_grid


# =========================================================
# Quantile regression (GBR quantile)
# =========================================================
def fit_quantile_gbr(
    X, y, q,
    seed=42,
    min_samples=300,
    n_estimators_max=300,
    learning_rate=0.05,
    max_depth=3,
    subsample=0.85,
    min_samples_leaf=25,
    max_features=1.0,
    val_frac=0.20,
    patience=12,
    step=25,
    tol=1e-4,
):
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)

    m = finite_mask_2col(X, y=y)
    X = X[m, :]
    y = y[m]
    n = len(y)
    if n < int(min_samples):
        return None

    q = float(q)
    rng = np.random.default_rng(int(seed))

    idx = np.arange(n)
    rng.shuffle(idx)

    n_val = int(max(50, np.floor(val_frac * n)))
    n_val = int(min(n_val, n - 50))
    if n_val <= 0:
        n_val = 0

    if n_val > 0:
        idx_val = idx[:n_val]
        idx_tr = idx[n_val:]
        X_tr, y_tr = X[idx_tr, :], y[idx_tr]
        X_val, y_val = X[idx_val, :], y[idx_val]
    else:
        X_tr, y_tr = X, y
        X_val, y_val = None, None

    cap_by_n = int(max(80, min(n_estimators_max, np.round(2.0 * np.sqrt(len(y_tr)) * 10))))
    n_estimators_max_eff = int(min(n_estimators_max, cap_by_n))

    model = GradientBoostingRegressor(
        loss="quantile",
        alpha=q,
        n_estimators=1,
        learning_rate=float(learning_rate),
        max_depth=int(max_depth),
        subsample=float(subsample),
        min_samples_leaf=int(min_samples_leaf),
        max_features=float(max_features),
        random_state=int(seed),
        warm_start=True,
    )

    def _refit_with_estimators(n_estimators_final):
        m2 = GradientBoostingRegressor(
            loss="quantile",
            alpha=q,
            n_estimators=int(n_estimators_final),
            learning_rate=float(learning_rate),
            max_depth=int(max_depth),
            subsample=float(subsample),
            min_samples_leaf=int(min_samples_leaf),
            max_features=float(max_features),
            random_state=int(seed),
        )
        m2.fit(X_tr, y_tr)
        return m2

    if X_val is None:
        n_final = int(min(n_estimators_max_eff, 200))
        return _refit_with_estimators(n_final)

    best_loss = np.inf
    best_stage = 1
    best_model = None
    no_improve = 0

    stage_list = list(range(1, n_estimators_max_eff + 1, int(step)))
    if stage_list[-1] != n_estimators_max_eff:
        stage_list.append(n_estimators_max_eff)

    for st in stage_list:
        model.set_params(n_estimators=int(st))
        model.fit(X_tr, y_tr)

        pred_val = model.predict(X_val)
        loss_val = pinball_loss(y_val, pred_val, q)

        if (best_loss - loss_val) > float(tol):
            best_loss = loss_val
            best_stage = int(st)
            best_model = _refit_with_estimators(best_stage)
            no_improve = 0
        else:
            no_improve += 1

        if no_improve >= int(patience):
            break

    if best_model is None:
        return _refit_with_estimators(int(min(n_estimators_max_eff, 200)))
    return best_model


def predict_quantile(model, X):
    X = np.asarray(X, dtype=float)
    if model is None:
        return np.full((X.shape[0],), np.nan, dtype=float)
    try:
        yhat = model.predict(X)
        yhat = np.asarray(yhat, dtype=float)
        if yhat.ndim != 1 or yhat.shape[0] != X.shape[0]:
            return np.full((X.shape[0],), np.nan, dtype=float)
        return yhat.astype(float)
    except Exception:
        return np.full((X.shape[0],), np.nan, dtype=float)


def fit_all_quantile_models(X_pool, y_pool, quantiles, seed, min_quantile_samples):
    X_pool = np.asarray(X_pool, dtype=float)
    y_pool = np.asarray(y_pool, dtype=float)
    m = np.isfinite(X_pool[:, 0]) & np.isfinite(X_pool[:, 1]) & np.isfinite(y_pool)
    X_pool = X_pool[m, :]
    y_pool = y_pool[m]
    if len(y_pool) < int(min_quantile_samples):
        return None

    models = {}
    ok_any = False
    for q in quantiles:
        try:
            m_q = fit_quantile_gbr(
                X_pool, y_pool, q=float(q),
                seed=int(seed) + int(float(q) * 1000) + 17,
                min_samples=int(min_quantile_samples)
            )
            models[float(q)] = m_q
            if m_q is not None:
                ok_any = True
        except Exception:
            models[float(q)] = None

    if not ok_any:
        return None
    return models


def predict_all_surfaces(models, quantiles, gx, gy):
    Xg, Yg = np.meshgrid(gx, gy, indexing="xy")
    grid_points = np.column_stack([Xg.ravel(), Yg.ravel()]).astype(np.float64)
    Qsurfs = {}
    for q in quantiles:
        yq = predict_quantile(models[q], grid_points).reshape(Xg.shape)
        Qsurfs[q] = yq
    return Qsurfs


# =========================================================
# Bootstrap uncertainty on surfaces
# =========================================================
def bootstrap_std_surfaces(
    X_pool, y_pool, quantiles, gx, gy,
    B, seed0, min_quantile_samples,
    max_train=None,
    boot_n=None,
    print_every=5,
    verbose=True,
):
    X_pool = np.asarray(X_pool, dtype=np.float64)
    y_pool = np.asarray(y_pool, dtype=np.float64)

    m = finite_mask_2col(X_pool, y=y_pool)
    X_pool = X_pool[m, :]
    y_pool = y_pool[m]
    n = int(len(y_pool))

    if n < int(min_quantile_samples) or int(B) < 2:
        return None

    rng = np.random.default_rng(int(seed0))

    if (max_train is not None) and (n > int(max_train)):
        idx0 = rng.choice(np.arange(n), size=int(max_train), replace=False)
        X_pool = X_pool[idx0, :]
        y_pool = y_pool[idx0]
        n = int(len(y_pool))

    if boot_n is None:
        boot_n = n
    boot_n = int(min(max(1, boot_n), n))

    Xg, Yg = np.meshgrid(gx, gy, indexing="xy")
    grid_points = np.column_stack([Xg.ravel(), Yg.ravel()]).astype(np.float64)
    G = int(grid_points.shape[0])

    means = {q: np.zeros(G, dtype=np.float64) for q in quantiles}
    M2s = {q: np.zeros(G, dtype=np.float64) for q in quantiles}
    counts = {q: 0 for q in quantiles}

    B_eff = 0
    for b in range(int(B)):
        idx = rng.integers(0, n, size=boot_n, endpoint=False)
        Xb = X_pool[idx, :]
        yb = y_pool[idx]

        models_b = fit_all_quantile_models(
            Xb, yb, quantiles,
            seed=int(seed0) + 1000 + b,
            min_quantile_samples=min_quantile_samples
        )
        if models_b is None:
            continue

        any_ok = False
        for q in quantiles:
            if (q not in models_b) or (models_b[q] is None):
                continue

            pred = predict_quantile(models_b[q], grid_points)
            pred = np.asarray(pred, dtype=np.float64)
            mf = np.isfinite(pred)
            if not np.any(mf):
                continue

            any_ok = True
            c = counts[q]
            c_new = c + 1
            counts[q] = c_new

            mu = means[q]
            M2 = M2s[q]

            delta = pred[mf] - mu[mf]
            mu[mf] += delta / c_new
            delta2 = pred[mf] - mu[mf]
            M2[mf] += delta * delta2

            means[q] = mu
            M2s[q] = M2

        if any_ok:
            B_eff += 1

        if verbose and (print_every is not None) and (print_every > 0) and ((b % int(print_every)) == 0):
            print(f"    [BOOT] b={b}/{int(B)} | B_eff={B_eff} | boot_n={boot_n} | pool_n={n}")

    if B_eff < 2:
        return None

    stds = {}
    Xg, Yg = np.meshgrid(gx, gy, indexing="xy")
    for q in quantiles:
        c = counts[q]
        if c < 2:
            stds[q] = np.full(Xg.shape, np.nan, dtype=np.float32)
            continue
        var = M2s[q] / (c - 1)
        std = np.sqrt(np.maximum(var, 0.0)).astype(np.float32)
        stds[q] = std.reshape(Xg.shape)

    return stds


# =========================================================
# LOCO evaluation
# =========================================================
def loco_pinball_evaluation(
    X_pool, y_pool, city_pool,
    quantiles,
    seed,
    min_quantile_samples,
    loco_max_train=200000
):
    X_pool = np.asarray(X_pool, dtype=float)
    y_pool = np.asarray(y_pool, dtype=float)
    city_pool = np.asarray(city_pool, dtype=object)

    rows = []
    rng = np.random.default_rng(int(seed) + 777)

    unique_cities = sorted(list(set(city_pool.tolist())))
    for city in unique_cities:
        test_mask = (city_pool == city)
        train_mask = ~test_mask

        Xtr = X_pool[train_mask, :]
        ytr = y_pool[train_mask]
        Xte = X_pool[test_mask, :]
        yte = y_pool[test_mask]

        mtr = finite_mask_2col(Xtr, y=ytr)
        mte = finite_mask_2col(Xte, y=yte)
        Xtr = Xtr[mtr, :]
        ytr = ytr[mtr]
        Xte = Xte[mte, :]
        yte = yte[mte]

        if len(yte) < 50 or len(ytr) < int(min_quantile_samples):
            for q in quantiles:
                rows.append({
                    "heldout_city": city,
                    "q": float(q),
                    "pinball": np.nan,
                    "n_test": int(len(yte)),
                    "n_train": int(len(ytr))
                })
            continue

        if len(ytr) > int(loco_max_train):
            idx = rng.choice(np.arange(len(ytr)), size=int(loco_max_train), replace=False)
            Xtr = Xtr[idx, :]
            ytr = ytr[idx]

        models = fit_all_quantile_models(
            Xtr, ytr, quantiles,
            seed=int(seed) + 100,
            min_quantile_samples=min_quantile_samples
        )
        if models is None:
            for q in quantiles:
                rows.append({
                    "heldout_city": city,
                    "q": float(q),
                    "pinball": np.nan,
                    "n_test": int(len(yte)),
                    "n_train": int(len(ytr))
                })
            continue

        for q in quantiles:
            pred = predict_quantile(models[q], Xte)
            loss = pinball_loss(yte, pred, q=float(q))
            rows.append({
                "heldout_city": city,
                "q": float(q),
                "pinball": float(loss),
                "n_test": int(len(yte)),
                "n_train": int(len(ytr))
            })

    return pd.DataFrame(rows)


# =========================================================
# W + thresholds
# =========================================================
def compute_W_for_points(models, qlo, qhi, H_vals, D_vals):
    H_vals = np.asarray(H_vals, dtype=np.float64).ravel()
    D_vals = np.asarray(D_vals, dtype=np.float64).ravel()
    if H_vals.size != D_vals.size:
        raise ValueError("compute_W_for_points: H_vals and D_vals must have same length")
    X = np.column_stack([H_vals, D_vals]).astype(np.float64)
    qlo = float(qlo)
    qhi = float(qhi)
    if (models is None) or (qlo not in models) or (qhi not in models):
        raise ValueError(f"compute_W_for_points: models missing qlo/qhi ({qlo}, {qhi})")
    y_lo = predict_quantile(models[qlo], X).astype(np.float64)
    y_hi = predict_quantile(models[qhi], X).astype(np.float64)
    return (y_hi - y_lo).astype(np.float64)


def safe_quantile_threshold(Wsurf, mask_on_grid, crit_q):
    Z = np.asarray(Wsurf, dtype=np.float64)
    mask = np.asarray(mask_on_grid, dtype=np.uint8)
    Zm = Z.copy()
    Zm[mask <= 0] = np.nan
    fin_m = Zm[np.isfinite(Zm)]
    if fin_m.size > 0:
        return float(np.nanquantile(fin_m, float(crit_q)))
    fin_u = Z[np.isfinite(Z)]
    if fin_u.size > 0:
        return float(np.nanquantile(fin_u, float(crit_q)))
    return np.nan

# =========================================================
# Plotting (global phase-space)
# =========================================================
def plot_support_density(H_count, xedges, yedges, outpath, title):
    plt.figure(figsize=(7.7, 6.1))
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    plt.imshow(H_count, origin="lower", aspect="auto", extent=extent)
    cb = plt.colorbar()
    cb.set_label("Training support count", fontsize=11)
    plt.xlabel("Grid entropy (H)")
    plt.ylabel("Grid dispersion (D)")
    plt.title(title)
    savefig(outpath)


def plot_phase(Z, gx, gy, outpath, title, cbar_label):
    plt.figure(figsize=(7.7, 6.1))
    extent = [gx.min(), gx.max(), gy.min(), gy.max()]
    plt.imshow(Z, origin="lower", aspect="auto", extent=extent)
    cb = plt.colorbar()
    cb.set_label(cbar_label, fontsize=11)
    plt.xlabel("Grid entropy (H)")
    plt.ylabel("Grid dispersion (D)")
    plt.title(title)
    savefig(outpath)


def plot_phase_masked(Z, mask, gx, gy, outpath, title, cbar_label):
    Zm = np.array(Z, dtype=float)
    Zm[np.asarray(mask) <= 0] = np.nan
    plt.figure(figsize=(7.7, 6.1))
    extent = [gx.min(), gx.max(), gy.min(), gy.max()]
    plt.imshow(Zm, origin="lower", aspect="auto", extent=extent)
    cb = plt.colorbar()
    cb.set_label(cbar_label, fontsize=11)
    plt.xlabel("Grid entropy (H)")
    plt.ylabel("Grid dispersion (D)")
    plt.title(title)
    savefig(outpath)


def plot_scatter_city_entropy(df, xcol, ycol, outpath, title, xlabel, ylabel):
    plt.figure(figsize=(8.2, 6.0))
    plt.scatter(df[xcol], df[ycol], s=70, edgecolor="k", linewidths=0.8, alpha=0.9)
    if "city" in df.columns:
        for _, r in df.iterrows():
            try:
                plt.text(float(r[xcol]), float(r[ycol]), str(r["city"]), fontsize=8.0, ha="left", va="bottom")
            except Exception:
                pass
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(alpha=0.25)
    savefig(outpath)


def plot_loco_pinball(df, outpath, title):
    qs = sorted(df["q"].unique())
    plt.figure(figsize=(8.2, 5.7))
    for q in qs:
        vals = df[df["q"] == q]["pinball"].values
        x = np.full_like(vals, fill_value=float(q), dtype=float)
        plt.scatter(x, vals, s=45, edgecolor="k", linewidths=0.7, alpha=0.85)
    plt.xlabel("Quantile q")
    plt.ylabel("Pinball loss")
    plt.title(title)
    plt.grid(alpha=0.25)
    savefig(outpath)


# =========================================================
# City maps
# =========================================================
def plot_city_risk_map(lat, lon, risk2d, outpath, title, cbar_label="Risk", vmin=None, vmax=None):
    lat = np.asarray(lat, dtype=float)
    lon = np.asarray(lon, dtype=float)
    Z = np.asarray(risk2d, dtype=float)

    if len(lat) >= 2 and lat[0] > lat[-1]:
        lat_plot = lat[::-1]
        Z_plot = Z[::-1, :]
    else:
        lat_plot = lat
        Z_plot = Z

    plt.figure(figsize=(7.7, 6.1))
    extent = [float(lon.min()), float(lon.max()), float(lat_plot.min()), float(lat_plot.max())]
    plt.imshow(Z_plot, origin="lower", aspect="auto", extent=extent, vmin=vmin, vmax=vmax)
    cb = plt.colorbar()
    cb.set_label(cbar_label, fontsize=11)
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.title(title)
    savefig(outpath)


def plot_city_mask(lat, lon, mask2d, outpath, title, cbar_label="Mask"):
    plot_city_risk_map(lat, lon, np.asarray(mask2d, dtype=float), outpath, title, cbar_label=cbar_label, vmin=0.0, vmax=1.0)


def plot_city_support_count(lat, lon, count2d, outpath, title):
    plot_city_risk_map(lat, lon, np.asarray(count2d, dtype=float), outpath, title, cbar_label="Support count")


def plot_city_extrap_mask(lat, lon, extrap2d, outpath, title):
    plot_city_risk_map(lat, lon, np.asarray(extrap2d, dtype=float), outpath, title, cbar_label="Extrapolation mask (1=extrap)", vmin=0.0, vmax=1.0)


def mosaic_city_maps(city_items, outpath, ncols=4, title="City Risk Mosaic"):
    n = len(city_items)
    if n == 0:
        return
    ncols = max(1, int(ncols))
    nrows = int(np.ceil(n / ncols))

    fig = plt.figure(figsize=(4.0 * ncols, 3.4 * nrows))
    for i, it in enumerate(city_items):
        ax = plt.subplot(nrows, ncols, i + 1)
        lat = np.asarray(it["lat"], dtype=float)
        lon = np.asarray(it["lon"], dtype=float)
        Z = np.asarray(it["Z"], dtype=float)

        if len(lat) >= 2 and lat[0] > lat[-1]:
            lat_plot = lat[::-1]
            Z_plot = Z[::-1, :]
        else:
            lat_plot = lat
            Z_plot = Z

        extent = [float(lon.min()), float(lon.max()), float(lat_plot.min()), float(lat_plot.max())]
        ax.imshow(
            Z_plot,
            origin="lower",
            aspect="auto",
            extent=extent,
            vmin=it.get("vmin", None),
            vmax=it.get("vmax", None),
        )
        ax.set_title(str(it["city"]), fontsize=9.5)
        ax.set_xlabel("Lon", fontsize=9)
        ax.set_ylabel("Lat", fontsize=9)
        ax.tick_params(labelsize=8)

    plt.suptitle(title, fontsize=13)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig(outpath, dpi=320)
    plt.close()


# =========================================================
# Build 2D risk map for a city
# =========================================================
def build_city_risk_map_from_cache(
    cache_path: str,
    models: Dict[float, Any],
    qlo: float,
    qhi: float,
    H_count: np.ndarray,
    xedges: np.ndarray,
    yedges: np.ndarray,
    support_min_count: int,
    allow_extrapolation: bool,
    soft_clip_quantiles: Tuple[float, float] = (0.01, 0.99),
) -> Optional[Dict[str, Any]]:
    if not os.path.exists(cache_path):
        return None
    z = np.load(cache_path)
    lat = z["lat"].astype(np.float64)
    lon = z["lon"].astype(np.float64)
    H2 = z["grid_entropy"].astype(np.float64)
    D2 = z["grid_disp"].astype(np.float64)

    Ny, Nx = H2.shape
    e = H2.ravel()
    d = D2.ravel()
    mX = np.isfinite(e) & np.isfinite(d)
    if int(np.sum(mX)) < 1:
        return None

    X = np.column_stack([e[mX], d[mX]]).astype(np.float64)
    counts = interp_hist_count_on_grid(X[:, 0], X[:, 1], H_count, xedges, yedges).astype(np.float64)
    support_ok = (counts >= float(support_min_count))

    W_pred = compute_W_for_points(models, qlo, qhi, X[:, 0], X[:, 1]).astype(np.float64)

    if soft_clip_quantiles is not None:
        q1, q2 = float(soft_clip_quantiles[0]), float(soft_clip_quantiles[1])
        W_pred = soft_clip_w_pred(W_pred, support_ok, q1=q1, q2=q2)

    risk_flat = np.full((Ny * Nx,), np.nan, dtype=float)
    sc_flat = np.full((Ny * Nx,), np.nan, dtype=float)
    ok_flat = np.zeros((Ny * Nx,), dtype=np.uint8)

    risk_flat[mX] = W_pred
    sc_flat[mX] = counts
    ok_flat[mX] = support_ok.astype(np.uint8)

    risk2d = risk_flat.reshape((Ny, Nx))
    support_count2d = sc_flat.reshape((Ny, Nx))
    support_ok2d = ok_flat.reshape((Ny, Nx))
    extrap_mask2d = (np.isfinite(risk2d) & (support_ok2d <= 0)).astype(np.uint8)

    if not allow_extrapolation:
        risk2d[extrap_mask2d > 0] = np.nan

    risk2d_support_only = np.array(risk2d, dtype=float)
    risk2d_support_only[extrap_mask2d > 0] = np.nan

    return {
        "lat": lat,
        "lon": lon,
        "risk2d": risk2d,
        "risk2d_support_only": risk2d_support_only,
        "support_count2d": support_count2d,
        "support_ok2d": support_ok2d,
        "extrap_mask2d": extrap_mask2d,
        "Ny": Ny,
        "Nx": Nx,
        "n_valid_points": int(np.sum(mX)),
        "extrap_frac": float(np.mean(extrap_mask2d[np.isfinite(risk2d)])) if np.any(np.isfinite(risk2d)) else np.nan,
    }


# =========================================================
# Corridor helpers
# =========================================================
def _cc_structure(connectivity=4):
    if int(connectivity) == 8:
        return np.ones((3, 3), dtype=np.uint8)
    return np.array([[0, 1, 0],
                     [1, 1, 1],
                     [0, 1, 0]], dtype=np.uint8)


def _label_components(mask_uint8, connectivity=4):
    if cc_label is None:
        return None, 0
    lab, nlab = cc_label((mask_uint8 > 0).astype(np.uint8), structure=_cc_structure(connectivity))
    return lab, int(nlab)


def _component_sizes_from_labels(lab, nlab):
    if lab is None or nlab <= 0:
        return np.array([], dtype=np.int64)
    bc = np.bincount(lab.ravel())
    if bc.size <= 1:
        return np.array([], dtype=np.int64)
    return bc[1:].astype(np.int64)


def _largest_component_mask(lab, nlab):
    if lab is None or nlab <= 0:
        return None
    sizes = _component_sizes_from_labels(lab, nlab)
    if sizes.size == 0:
        return None
    k = int(np.argmax(sizes)) + 1
    return (lab == k).astype(np.uint8)


def perimeter_4(mask_bool):
    m = (mask_bool > 0).astype(np.uint8)
    if m.size == 0:
        return 0
    per = 0
    per += int(np.sum(m[:, 1:] != m[:, :-1]))
    per += int(np.sum(m[1:, :] != m[:-1, :]))
    per += int(np.sum(m[0, :]))
    per += int(np.sum(m[-1, :]))
    per += int(np.sum(m[:, 0]))
    per += int(np.sum(m[:, -1]))
    return int(per)


def corridor_topology_metrics(mask_uint8, connectivity=4):
    out = {
        "area_frac": np.nan,
        "n_components": 0,
        "largest_size": 0,
        "largest_frac": np.nan,
        "mean_size": np.nan,
        "median_size": np.nan,
        "size_gini": np.nan,
        "perimeter_per_area": np.nan,
        "area": 0,
        "perimeter": 0,
    }
    if mask_uint8 is None:
        return out

    m = (mask_uint8 > 0).astype(np.uint8)
    Ny, Nx = m.shape
    area = int(np.sum(m))
    out["area"] = area
    out["area_frac"] = float(area / (Ny * Nx)) if Ny * Nx > 0 else np.nan
    out["perimeter"] = int(perimeter_4(m))

    if area <= 0:
        out["largest_frac"] = 0.0
        return out

    lab, nlab = _label_components(m, connectivity=connectivity)
    sizes = _component_sizes_from_labels(lab, nlab)
    if sizes.size == 0:
        out["perimeter_per_area"] = float(out["perimeter"] / (area + EPS))
        return out

    largest = int(np.max(sizes))
    out["n_components"] = int(nlab)
    out["largest_size"] = largest
    out["largest_frac"] = float(largest / (area + EPS))
    out["mean_size"] = float(np.mean(sizes))
    out["median_size"] = float(np.median(sizes))
    out["size_gini"] = float(gini_1d(sizes.astype(float)))
    out["perimeter_per_area"] = float(out["perimeter"] / (area + EPS))
    return out


def corridor_pca_anisotropy(mask_uint8, mode="largest"):
    out = {
        "pca_n": 0,
        "pca_lambda1": np.nan,
        "pca_lambda2": np.nan,
        "pca_angle_deg": np.nan,
        "pca_anisotropy": np.nan,
    }
    if mask_uint8 is None:
        return out

    m = (mask_uint8 > 0).astype(np.uint8)
    if int(np.sum(m)) < 2:
        return out

    use = m
    if mode == "largest" and cc_label is not None:
        lab, nlab = _label_components(m, connectivity=4)
        lc = _largest_component_mask(lab, nlab)
        if lc is not None and int(np.sum(lc)) >= 2:
            use = lc

    ys, xs = np.where(use > 0)
    if len(xs) < 2:
        return out

    X = np.column_stack([xs.astype(np.float64), ys.astype(np.float64)])
    mu = np.mean(X, axis=0)
    Xc = X - mu
    C = (Xc.T @ Xc) / max(1, (Xc.shape[0] - 1))
    try:
        w, v = np.linalg.eigh(C)
        order = np.argsort(w)[::-1]
        w = w[order]
        v = v[:, order]
        lam1 = float(w[0])
        lam2 = float(w[1]) if w.size > 1 else 0.0
        vx, vy = float(v[0, 0]), float(v[1, 0])
        ang = float(np.degrees(np.arctan2(vy, vx))) % 180.0
        anis = float((lam1 + EPS) / (lam2 + EPS))
        out.update({
            "pca_n": int(X.shape[0]),
            "pca_lambda1": lam1,
            "pca_lambda2": lam2,
            "pca_angle_deg": ang,
            "pca_anisotropy": anis,
        })
    except Exception:
        pass
    return out


def _prepare_ph_array(W_pred_2d: np.ndarray, support_mask: Optional[np.ndarray]):
    Z = np.asarray(W_pred_2d, dtype=np.float64)
    finite = np.isfinite(Z)
    if support_mask is None:
        support = finite.copy()
    else:
        support = np.asarray(support_mask).astype(bool) & finite

    if int(np.sum(support)) <= 0:
        return Z, support, np.zeros_like(Z, dtype=np.float64)

    F = np.full_like(Z, fill_value=np.inf, dtype=np.float64)
    F[support] = -Z[support]

    bad = ~support
    if np.any(bad):
        finiteF = F[np.isfinite(F)]
        maxF = float(np.max(finiteF)) if finiteF.size > 0 else 0.0
        F[bad] = maxF + max(1.0, abs(maxF)) + 1.0

    return Z, support, F


def _pairs_by_dim_from_gudhi(F: np.ndarray):
    if not _HAS_GUDHI:
        raise RuntimeError("Gudhi not installed. Install gudhi to use PH corridors.")

    cc = gd.CubicalComplex(dimensions=F.shape, top_dimensional_cells=F.ravel(order="C"))
    cc.persistence(homology_coeff_field=2, min_persistence=0.0)

    pairs = {0: [], 1: []}

    diag0 = cc.persistence_intervals_in_dimension(0)
    if diag0 is not None and len(diag0) > 0:
        for bd in np.asarray(diag0):
            b, d = float(bd[0]), float(bd[1])
            if np.isinf(d):
                continue
            birth_w = -b
            death_w = -d
            pers = birth_w - death_w
            pairs[0].append((birth_w, death_w, pers))

    diag1 = cc.persistence_intervals_in_dimension(1)
    if diag1 is not None and len(diag1) > 0:
        for bd in np.asarray(diag1):
            b, d = float(bd[0]), float(bd[1])
            if np.isinf(d):
                continue
            birth_w = -b
            death_w = -d
            pers = birth_w - death_w
            pairs[1].append((birth_w, death_w, pers))

    return pairs


def _fallback_pairs_from_threshold_scan(Z: np.ndarray, support: np.ndarray, n_levels: int = 64):
    vals = Z[support]
    if vals.size <= 0:
        return {0: [], 1: []}

    levels = np.unique(np.quantile(vals, np.linspace(1.0, 0.0, int(max(16, n_levels)))))
    levels = np.sort(levels)[::-1]

    pairs0 = []
    prev_lab = None
    prev_ids = {}
    birth_of = {}
    next_id = 1

    for th in levels:
        mask = (support & np.isfinite(Z) & (Z >= float(th))).astype(np.uint8)
        lab, nlab = _label_components(mask, connectivity=4)
        if lab is None:
            continue

        cur_ids = {}
        if prev_lab is None:
            for k in range(1, nlab + 1):
                cur_ids[k] = next_id
                birth_of[next_id] = float(th)
                next_id += 1
        else:
            for k in range(1, nlab + 1):
                overlap_prev = prev_lab[lab == k]
                overlap_prev = overlap_prev[overlap_prev > 0]
                if overlap_prev.size == 0:
                    cur_ids[k] = next_id
                    birth_of[next_id] = float(th)
                    next_id += 1
                else:
                    prev_comp = int(np.bincount(overlap_prev).argmax())
                    if prev_comp in prev_ids:
                        cur_ids[k] = prev_ids[prev_comp]
                    else:
                        cur_ids[k] = next_id
                        birth_of[next_id] = float(th)
                        next_id += 1

            prev_unique_ids = set(prev_ids.values())
            cur_unique_ids = set(cur_ids.values())
            dead_ids = prev_unique_ids - cur_unique_ids
            for gid in dead_ids:
                b = float(birth_of.get(gid, th))
                d = float(th)
                pairs0.append((b, d, b - d))

        prev_lab = lab.copy()
        prev_ids = cur_ids

    if len(birth_of) > 0:
        dlast = float(np.min(vals))
        still_alive = set(prev_ids.values())
        for gid in still_alive:
            b = float(birth_of.get(gid, dlast))
            pairs0.append((b, dlast, b - dlast))

    return {0: pairs0, 1: []}


def corridor_ph_backbone(
    W_pred_2d: np.ndarray,
    support_mask: Optional[np.ndarray] = None,
    alpha: float = 0.65,
    top_k: int = 1,
    persistence_min_mode: str = "quantile",
    persistence_min_value: float = 0.50,
    make_skeleton: bool = True,
    connectivity: int = 4,
):
    Z, support, F = _prepare_ph_array(W_pred_2d, support_mask)
    n_support = int(np.sum(support))
    if n_support <= 0:
        return None

    if _HAS_GUDHI:
        pairs = _pairs_by_dim_from_gudhi(F)
        method = "gudhi_cubical"
    else:
        pairs = _fallback_pairs_from_threshold_scan(Z, support, n_levels=64)
        method = "fallback_threshold_scan"

    pairs0 = [(float(b), float(d), float(p)) for (b, d, p) in pairs.get(0, []) if np.isfinite(p) and p >= 0.0]
    pairs1 = [(float(b), float(d), float(p)) for (b, d, p) in pairs.get(1, []) if np.isfinite(p) and p >= 0.0]

    pers0 = np.array([p[2] for p in pairs0], dtype=np.float64) if len(pairs0) else np.array([], dtype=np.float64)
    pers1 = np.array([p[2] for p in pairs1], dtype=np.float64) if len(pairs1) else np.array([], dtype=np.float64)

    if persistence_min_mode == "absolute":
        tau = float(persistence_min_value)
    else:
        tau = float(np.quantile(pers0, float(persistence_min_value))) if pers0.size > 0 else 0.0

    cp0_max = float(np.max(pers0)) if pers0.size > 0 else 0.0
    cp0_sum = float(np.sum(pers0[pers0 >= tau])) if pers0.size > 0 else 0.0
    cp1_sum = float(np.sum(pers1[pers1 >= tau])) if pers1.size > 0 else 0.0

    corridor_persistence_index = safe_div(cp0_max, np.sum(pers0), fill=np.nan)
    loop_suppression_index = safe_div(cp1_sum, cp0_sum, fill=np.nan)

    if len(pairs0) <= 0:
        theta_star = float(np.nanmedian(Z[support]))
        corridor_mask = (support & np.isfinite(Z) & (Z >= theta_star)).astype(np.uint8)
        skeleton_mask = corridor_mask.copy()

        if make_skeleton and _HAS_SKIMAGE and int(np.sum(corridor_mask)) > 0:
            skeleton_mask = skeletonize(corridor_mask > 0).astype(np.uint8)

        return {
            "method": method,
            "n_support": n_support,
            "tau": tau,
            "theta_star": theta_star,
            "cp0_max": cp0_max,
            "cp0_sum": cp0_sum,
            "cp1_sum": cp1_sum,
            "corridor_persistence_index": corridor_persistence_index,
            "loop_suppression_index": loop_suppression_index,
            "pairs0": pairs0,
            "pairs1": pairs1,
            "corridor_mask": corridor_mask,
            "skeleton_mask": skeleton_mask,
            "selected_birth": np.nan,
            "selected_death": np.nan,
            "selected_persistence": np.nan,
        }

    pairs0_sorted = sorted(pairs0, key=lambda t: (t[2], t[0]), reverse=True)
    sel = pairs0_sorted[:max(1, int(top_k))]
    b0, d0, p0 = sel[0]

    a = float(np.clip(alpha, 0.0, 1.0))
    theta_star = float(d0 + a * (b0 - d0))

    corridor_mask = (support & np.isfinite(Z) & (Z >= theta_star)).astype(np.uint8)

    if int(np.sum(corridor_mask)) <= 0:
        corridor_mask = np.zeros_like(corridor_mask, dtype=np.uint8)
        ztmp = np.where(support, Z, np.nan)
        if np.any(np.isfinite(ztmp)):
            flat_idx = np.nanargmax(ztmp)
            iy, ix = np.unravel_index(flat_idx, Z.shape)
            corridor_mask[iy, ix] = 1

    skeleton_mask = corridor_mask.copy()
    if make_skeleton and _HAS_SKIMAGE and int(np.sum(corridor_mask)) > 0:
        try:
            skeleton_mask = skeletonize(corridor_mask > 0).astype(np.uint8)
            if int(np.sum(skeleton_mask)) <= 0:
                skeleton_mask = corridor_mask.copy()
        except Exception:
            skeleton_mask = corridor_mask.copy()

    return {
        "method": method,
        "n_support": n_support,
        "tau": tau,
        "theta_star": theta_star,
        "cp0_max": cp0_max,
        "cp0_sum": cp0_sum,
        "cp1_sum": cp1_sum,
        "corridor_persistence_index": corridor_persistence_index,
        "loop_suppression_index": loop_suppression_index,
        "pairs0": pairs0,
        "pairs1": pairs1,
        "corridor_mask": corridor_mask,
        "skeleton_mask": skeleton_mask,
        "selected_birth": float(b0),
        "selected_death": float(d0),
        "selected_persistence": float(p0),
    }


def save_ph_pairs_json(path: str, ph_pack: Dict[str, Any]) -> None:
    payload = {
        "method": ph_pack.get("method"),
        "n_support": int(ph_pack.get("n_support", 0)),
        "tau": float(ph_pack.get("tau", 0.0)),
        "theta_star": float(ph_pack.get("theta_star", np.nan)),
        "cp0_max": float(ph_pack.get("cp0_max", 0.0)),
        "cp0_sum": float(ph_pack.get("cp0_sum", 0.0)),
        "cp1_sum": float(ph_pack.get("cp1_sum", 0.0)),
        "corridor_persistence_index": float(ph_pack.get("corridor_persistence_index", np.nan)),
        "loop_suppression_index": float(ph_pack.get("loop_suppression_index", np.nan)),
        "selected_birth": float(ph_pack.get("selected_birth", np.nan)),
        "selected_death": float(ph_pack.get("selected_death", np.nan)),
        "selected_persistence": float(ph_pack.get("selected_persistence", np.nan)),
        "pairs0": [[float(a), float(b), float(c)] for a, b, c in ph_pack.get("pairs0", [])],
        "pairs1": [[float(a), float(b), float(c)] for a, b, c in ph_pack.get("pairs1", [])],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


# =========================================================
# Percolation + susceptibility + tau + scaling
# =========================================================
def _label_and_sizes(mask_uint8, connectivity=4):
    if cc_label is None:
        return 0, np.array([], dtype=int), 0, 0

    m = (mask_uint8 > 0).astype(np.uint8)
    occupied_n = int(np.sum(m))
    if occupied_n <= 0:
        return occupied_n, np.array([], dtype=int), 0, 0

    lab, nlab = cc_label(m, structure=_cc_structure(connectivity))
    if nlab <= 0:
        return occupied_n, np.array([], dtype=int), 0, 0

    bc = np.bincount(lab.ravel())
    if bc.size <= 1:
        return occupied_n, np.array([], dtype=int), 0, 0

    sizes = bc[1:].astype(int)
    largest = int(sizes.max()) if sizes.size > 0 else 0
    return occupied_n, sizes, largest, int(nlab)


def _remove_one_largest(sizes):
    sizes = np.asarray(sizes, dtype=np.int64)
    if sizes.size == 0:
        return sizes
    idx = int(np.argmax(sizes))
    return np.delete(sizes, idx)


def susceptibility_from_sizes(sizes):
    sizes = np.asarray(sizes, dtype=np.int64)
    if sizes.size <= 0:
        return 0.0
    num = float(np.sum((sizes.astype(np.float64)) ** 2))
    den = float(np.sum(sizes.astype(np.float64)) + EPS)
    return float(num / den)


def finite_cluster_hist(sizes_excl_largest):
    sizes = np.asarray(sizes_excl_largest, dtype=np.int64)
    sizes = sizes[sizes > 0]
    if sizes.size == 0:
        return np.array([], dtype=np.int64), np.array([], dtype=np.int64)
    u, c = np.unique(sizes, return_counts=True)
    return u.astype(np.int64), c.astype(np.int64)


def _estimate_pc_from_dSdp(p, S_smooth):
    p = np.asarray(p, dtype=float)
    S = np.asarray(S_smooth, dtype=float)
    m = np.isfinite(p) & np.isfinite(S)
    if np.sum(m) < 5:
        return np.nan, -1, np.full_like(p, np.nan, dtype=float)

    px = p[m]
    sx = S[m]
    order = np.argsort(px)
    px = px[order]
    sx = sx[order]

    dSdp = np.gradient(sx, px)
    dSdp_full = np.full_like(p, np.nan, dtype=float)
    dSdp_full[np.where(m)[0][order]] = dSdp

    if not np.any(np.isfinite(dSdp)):
        return np.nan, -1, dSdp_full

    idx_local = int(np.nanargmax(dSdp))
    p_c = float(px[idx_local])

    idx_global = np.where(np.isfinite(dSdp_full))[0]
    if idx_global.size == 0:
        return np.nan, -1, dSdp_full

    real_idx = int(idx_global[np.argmin(np.abs(p[idx_global] - p_c))])
    return p_c, real_idx, dSdp_full


def percolation_scan_full(risk_map, levels=31, connectivity=4, smooth_win=5):
    Z = np.asarray(risk_map, dtype=float)
    fin = Z[np.isfinite(Z)]
    if fin.size < 50:
        return None, None

    levels = int(max(5, levels))
    qs = np.linspace(0.50, 0.99, levels)
    thetas = np.quantile(fin, qs)

    Ny, Nx = Z.shape
    N_eff = int(np.sum(np.isfinite(Z)))

    rows_raw = []
    sizes_list = []
    finite_sizes_list = []
    finite_u_list = []
    finite_c_list = []

    for q, th in zip(qs, thetas):
        th = float(th)
        mask = (Z >= th) & np.isfinite(Z)
        occ = float(np.sum(mask) / (N_eff + EPS))

        occupied_n, sizes, largest, nlab = _label_and_sizes(mask.astype(np.uint8), connectivity=connectivity)

        if occupied_n <= 0 or sizes.size == 0:
            G = 0.0
            S = 0.0
            ncomp = 0
            largest_sz = 0
            sizes_all = np.array([], dtype=np.int64)
            finite_sizes = np.array([], dtype=np.int64)
            u, c = np.array([], dtype=np.int64), np.array([], dtype=np.int64)
        else:
            G = float(largest / (occupied_n + EPS))
            sizes_all = sizes.astype(np.int64)
            finite_sizes = _remove_one_largest(sizes_all).astype(np.int64)
            finite_sizes = finite_sizes[finite_sizes > 0]
            S = susceptibility_from_sizes(finite_sizes)
            ncomp = int(nlab)
            largest_sz = int(largest)
            u, c = finite_cluster_hist(finite_sizes)

        rows_raw.append({
            "q": float(q),
            "theta": float(th),
            "occ": occ,
            "G": float(G),
            "S": float(S),
            "n_components": int(ncomp),
            "largest_size": int(largest_sz),
            "occupied_n": int(occupied_n),
            "N_eff": int(N_eff),
        })

        sizes_list.append(sizes_all)
        finite_sizes_list.append(finite_sizes)
        finite_u_list.append(u)
        finite_c_list.append(c)

    df0 = pd.DataFrame(rows_raw)
    if len(df0) < 5:
        df0["S_smooth"] = np.nan
        df0["dSdp"] = np.nan
        df0.attrs["theta_c_S"] = np.nan
        df0.attrs["q_c_S"] = np.nan
        df0.attrs["idx_c_S"] = -1
        df0.attrs["p_c_S"] = np.nan
        df0.attrs["pc_method"] = "invalid"
        hist_pack = {
            "theta": df0["theta"].values.astype(np.float64),
            "q": df0["q"].values.astype(np.float64),
            "occ": df0["occ"].values.astype(np.float64),
            "occupied_n": df0["occupied_n"].values.astype(np.int64),
            "largest_size": df0["largest_size"].values.astype(np.int64),
            "sizes_list": np.array(sizes_list, dtype=object),
            "finite_sizes_list": np.array(finite_sizes_list, dtype=object),
            "finite_u_list": np.array(finite_u_list, dtype=object),
            "finite_c_list": np.array(finite_c_list, dtype=object),
            "connectivity": np.int32(connectivity),
            "N_eff": np.int64(N_eff),
        }
        return df0, hist_pack

    order = np.argsort(df0["theta"].values)
    df = df0.iloc[order].reset_index(drop=True)
    sizes_list = [sizes_list[i] for i in order]
    finite_sizes_list = [finite_sizes_list[i] for i in order]
    finite_u_list = [finite_u_list[i] for i in order]
    finite_c_list = [finite_c_list[i] for i in order]

    S_arr = df["S"].values.astype(float)
    S_s = smooth_1d(S_arr, win=int(max(3, smooth_win)))
    df["S_smooth"] = S_s

    p_arr = df["occ"].values.astype(float)
    p_c_d, idx_c_d, dSdp = _estimate_pc_from_dSdp(p_arr, S_s)
    df["dSdp"] = dSdp

    if np.isfinite(p_c_d) and idx_c_d >= 0:
        df.attrs["theta_c_S"] = float(df.iloc[idx_c_d]["theta"])
        df.attrs["q_c_S"] = float(df.iloc[idx_c_d]["q"])
        df.attrs["idx_c_S"] = int(idx_c_d)
        df.attrs["p_c_S"] = float(df.iloc[idx_c_d]["occ"])
        df.attrs["pc_method"] = "dSdp_peak"
    elif np.any(np.isfinite(S_s)):
        iS = int(np.nanargmax(S_s))
        df.attrs["theta_c_S"] = float(df.iloc[iS]["theta"])
        df.attrs["q_c_S"] = float(df.iloc[iS]["q"])
        df.attrs["idx_c_S"] = int(iS)
        df.attrs["p_c_S"] = float(df.iloc[iS]["occ"])
        df.attrs["pc_method"] = "S_peak_fallback"
    else:
        df.attrs["theta_c_S"] = np.nan
        df.attrs["q_c_S"] = np.nan
        df.attrs["idx_c_S"] = -1
        df.attrs["p_c_S"] = np.nan
        df.attrs["pc_method"] = "invalid"

    hist_pack = {
        "theta": df["theta"].values.astype(np.float64),
        "q": df["q"].values.astype(np.float64),
        "occ": df["occ"].values.astype(np.float64),
        "occupied_n": df["occupied_n"].values.astype(np.int64),
        "largest_size": df["largest_size"].values.astype(np.int64),
        "sizes_list": np.array(sizes_list, dtype=object),
        "finite_sizes_list": np.array(finite_sizes_list, dtype=object),
        "finite_u_list": np.array(finite_u_list, dtype=object),
        "finite_c_list": np.array(finite_c_list, dtype=object),
        "connectivity": np.int32(connectivity),
        "N_eff": np.int64(N_eff),
    }
    return df, hist_pack


def save_cluster_hist_npz(out_npz_path, hist_pack: Dict[str, Any]):
    np.savez_compressed(
        out_npz_path,
        theta=hist_pack["theta"],
        q=hist_pack["q"],
        occ=hist_pack["occ"],
        occupied_n=hist_pack["occupied_n"],
        largest_size=hist_pack["largest_size"],
        sizes_list=hist_pack["sizes_list"],
        finite_sizes_list=hist_pack["finite_sizes_list"],
        finite_u_list=hist_pack["finite_u_list"],
        finite_c_list=hist_pack["finite_c_list"],
        connectivity=hist_pack.get("connectivity", np.int32(-1)),
        N_eff=hist_pack.get("N_eff", np.int64(-1)),
    )


def plot_percolation(df, outpath, title):
    theta = df["theta"].values.astype(float)
    G = df["G"].values.astype(float)
    S = df["S_smooth"].values.astype(float) if "S_smooth" in df.columns else df["S"].values.astype(float)
    theta_c_S = float(df.attrs.get("theta_c_S", np.nan))
    pc_method = str(df.attrs.get("pc_method", "unknown"))

    plt.figure(figsize=(8.2, 5.9))
    ax1 = plt.gca()
    ax1.plot(theta, G, marker="o", markersize=4.0)
    ax1.set_xlabel("Threshold θ on corridor-risk field")
    ax1.set_ylabel("Largest passable-cluster fraction G(θ)")
    ax1.grid(alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(theta, S, linewidth=1.2, alpha=0.95)
    ax2.set_ylabel("Susceptibility S(θ) (excl. largest)")

    if np.isfinite(theta_c_S):
        ax1.axvline(theta_c_S, linestyle="--", linewidth=1.4)

    plt.title(f"{title} | pc={pc_method}")
    savefig(outpath)


def log_bin_hist(sizes, bins=22, smin=2, smax=None):
    sizes = np.asarray(sizes, dtype=np.int64)
    sizes = sizes[sizes >= int(smin)]
    if sizes.size == 0:
        return None
    if smax is None:
        smax = int(np.max(sizes))
    smax = int(max(smax, smin))
    if smax <= smin:
        return None

    edges = np.logspace(np.log10(smin), np.log10(smax + 1e-9), int(bins) + 1)
    counts, _ = np.histogram(sizes.astype(float), bins=edges)
    centers = np.sqrt(edges[:-1] * edges[1:])
    widths = edges[1:] - edges[:-1]
    n_s = counts / np.maximum(widths, EPS)
    return centers, n_s, counts, edges


def tau_fit_loglog(centers, n_s, min_points=10):
    centers = np.asarray(centers, dtype=float)
    n_s = np.asarray(n_s, dtype=float)
    m = np.isfinite(centers) & np.isfinite(n_s) & (centers > 0) & (n_s > 0)
    if np.sum(m) < int(min_points):
        return np.nan, np.nan, np.nan, int(np.sum(m))
    x = np.log(centers[m])
    y = np.log(n_s[m])
    A = np.column_stack([np.ones_like(x), x])
    coef, _, _, _ = np.linalg.lstsq(A, y, rcond=None)
    a, b = float(coef[0]), float(coef[1])
    yhat = A @ coef
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2) + EPS)
    r2 = 1.0 - ss_res / ss_tot
    tau = -b
    return float(tau), float(a), float(r2), int(np.sum(m))


def tau_mle_discrete(sizes, smin=2):
    s = np.asarray(sizes, dtype=np.float64)
    s = s[np.isfinite(s) & (s >= float(smin))]
    n = int(s.size)
    if n <= 0:
        return np.nan, 0
    denom = float(np.sum(np.log(s / (float(smin) - 0.5 + EPS))))
    if not np.isfinite(denom) or denom <= 0:
        return np.nan, n
    tau_hat = 1.0 + n / denom
    return float(tau_hat), n


def plot_tau_fit(centers, n_s, tau_lr, outpath, title):
    plt.figure(figsize=(7.6, 6.1))
    m = np.isfinite(centers) & np.isfinite(n_s) & (centers > 0) & (n_s > 0)
    if np.sum(m) > 0:
        plt.loglog(centers[m], n_s[m], marker="o", markersize=4.0, linestyle="None")
        if np.isfinite(tau_lr):
            x = centers[m]
            y = n_s[m]
            xm = float(np.median(x))
            ym = float(np.median(y))
            ref_x = np.array([np.min(x), np.max(x)], dtype=float)
            ref_y = ym * (ref_x / xm) ** (-tau_lr)
            plt.loglog(ref_x, ref_y, linewidth=1.4)
    plt.xlabel("Cluster size s")
    plt.ylabel("n_s (bin-width normalized)")
    plt.title(title)
    plt.grid(alpha=0.25, which="both")
    savefig(outpath)


def tau_fit_from_hist_pack_at_index(hist_pack, idx, bins=22, smin=2, smax_quantile=0.95, min_points=10):
    finite_sizes = hist_pack["finite_sizes_list"][idx]
    finite_sizes = np.asarray(finite_sizes, dtype=np.int64)
    finite_sizes = finite_sizes[finite_sizes >= int(smin)]
    if finite_sizes.size < int(max(30, min_points * 2)):
        return None

    smax = int(np.quantile(finite_sizes, float(smax_quantile))) if finite_sizes.size > 0 else None
    if smax is None or smax <= smin:
        smax = int(np.max(finite_sizes)) if finite_sizes.size > 0 else None
    if smax is None or smax <= smin:
        return None

    hb = log_bin_hist(finite_sizes, bins=int(bins), smin=int(smin), smax=int(smax))
    if hb is None:
        return None
    centers, n_s, counts, edges = hb

    tau_lr, a_lr, r2_lr, n_used = tau_fit_loglog(centers, n_s, min_points=int(min_points))
    tau_mle, n_mle = tau_mle_discrete(finite_sizes, smin=int(smin))

    out = {
        "finite_sizes": finite_sizes,
        "centers": centers,
        "n_s": n_s,
        "counts": counts,
        "edges": edges,
        "tau_lr": tau_lr,
        "a_lr": a_lr,
        "r2_lr": r2_lr,
        "n_used_bins": n_used,
        "tau_mle": tau_mle,
        "n_mle": n_mle,
        "smin": int(smin),
        "smax": int(smax),
    }
    return out


def _fit_loglog(x, y, min_points=8):
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y) & (x > 0) & (y > 0)
    if np.sum(m) < int(min_points):
        return np.nan, np.nan, np.nan, int(np.sum(m))
    lx = np.log(x[m])
    ly = np.log(y[m])
    A = np.column_stack([np.ones_like(lx), lx])
    coef, _, _, _ = np.linalg.lstsq(A, ly, rcond=None)
    a, b = float(coef[0]), float(coef[1])
    yhat = A @ coef
    ss_res = float(np.sum((ly - yhat) ** 2))
    ss_tot = float(np.sum((ly - np.mean(ly)) ** 2) + EPS)
    r2 = 1.0 - ss_res / ss_tot
    return a, b, r2, int(np.sum(m))


def fit_beta_gamma_from_perc_curve_ppc(
    df_perc,
    p_c,
    window_frac=0.25,
    min_points=8,
    r2_min=0.55,
):
    if df_perc is None or len(df_perc) < 10 or (not np.isfinite(p_c)):
        return {
            "beta": np.nan, "beta_r2": np.nan, "beta_n": 0,
            "gamma": np.nan, "gamma_r2": np.nan, "gamma_n": 0,
            "beta_window_lo": np.nan, "beta_window_hi": np.nan,
            "gamma_window_lo": np.nan, "gamma_window_hi": np.nan,
        }

    p = df_perc["occ"].values.astype(float)
    G = df_perc["G"].values.astype(float)
    S = df_perc["S_smooth"].values.astype(float) if "S_smooth" in df_perc.columns else df_perc["S"].values.astype(float)

    span = float(np.nanmax(p) - np.nanmin(p))
    if not np.isfinite(span) or span <= 0:
        return {
            "beta": np.nan, "beta_r2": np.nan, "beta_n": 0,
            "gamma": np.nan, "gamma_r2": np.nan, "gamma_n": 0,
            "beta_window_lo": np.nan, "beta_window_hi": np.nan,
            "gamma_window_lo": np.nan, "gamma_window_hi": np.nan,
        }

    w = float(window_frac) * span
    dp = p - float(p_c)

    mb = (dp > 0) & (np.abs(dp) <= w) & np.isfinite(G) & (G > 0)
    xb = dp[mb]
    yb = G[mb]
    _, b_b, r2_b, n_b = _fit_loglog(xb, yb, min_points=min_points)
    beta = b_b if (np.isfinite(r2_b) and r2_b >= float(r2_min)) else np.nan

    mg = (np.abs(dp) > 0) & (np.abs(dp) <= w) & np.isfinite(S) & (S > 0)
    xg = np.abs(dp[mg])
    yg = S[mg]
    _, b_g, r2_g, n_g = _fit_loglog(xg, yg, min_points=min_points)
    gamma = (-b_g) if (np.isfinite(r2_g) and r2_g >= float(r2_min)) else np.nan

    return {
        "beta": float(beta) if np.isfinite(beta) else np.nan,
        "beta_r2": float(r2_b) if np.isfinite(r2_b) else np.nan,
        "beta_n": int(n_b),
        "gamma": float(gamma) if np.isfinite(gamma) else np.nan,
        "gamma_r2": float(r2_g) if np.isfinite(r2_g) else np.nan,
        "gamma_n": int(n_g),
        "beta_window_lo": float(p_c),
        "beta_window_hi": float(p_c + w),
        "gamma_window_lo": float(max(np.nanmin(p), p_c - w)),
        "gamma_window_hi": float(min(np.nanmax(p), p_c + w)),
    }


def plot_scaling_fits_ppc(df_perc, p_c, outpath, title, window_frac=0.25):
    if df_perc is None or len(df_perc) < 10 or (not np.isfinite(p_c)):
        return
    p = df_perc["occ"].values.astype(float)
    G = df_perc["G"].values.astype(float)
    S = df_perc["S_smooth"].values.astype(float) if "S_smooth" in df_perc.columns else df_perc["S"].values.astype(float)

    span = float(np.nanmax(p) - np.nanmin(p))
    if not np.isfinite(span) or span <= 0:
        return
    w = float(window_frac) * span
    dp = p - float(p_c)

    fig = plt.figure(figsize=(10.2, 4.7))

    ax1 = fig.add_subplot(1, 2, 1)
    mb = (dp > 0) & (np.abs(dp) <= w) & np.isfinite(G) & (G > 0)
    if np.sum(mb) >= 6:
        ax1.loglog(dp[mb], G[mb], marker="o", linestyle="None", markersize=4.0)
    ax1.set_xlabel("(p - pc)")
    ax1.set_ylabel("G(p) = P∞")
    ax1.set_title("β fit window (p-pc)")
    ax1.grid(alpha=0.25, which="both")

    ax2 = fig.add_subplot(1, 2, 2)
    mg = (np.abs(dp) > 0) & (np.abs(dp) <= w) & np.isfinite(S) & (S > 0)
    if np.sum(mg) >= 6:
        ax2.loglog(np.abs(dp[mg]), S[mg], marker="o", linestyle="None", markersize=4.0)
    ax2.set_xlabel("|p - pc|")
    ax2.set_ylabel("S(p)")
    ax2.set_title("γ fit window (p-pc)")
    ax2.grid(alpha=0.25, which="both")

    plt.suptitle(title, fontsize=13)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(outpath, dpi=330)
    plt.close()


# =========================================================
# City occupancy
# =========================================================
def compute_city_critical_band_occupancy(
    city_cache_npz_path,
    models,
    qlo, qhi,
    W_thr,
    support_min_count,
    H_count, xedges, yedges,
    min_city_points_for_eval=1,
):
    z = np.load(city_cache_npz_path)
    H = z["grid_entropy"].astype(np.float64)
    D = z["grid_disp"].astype(np.float64)

    e = H.ravel()
    d = D.ravel()
    mX = np.isfinite(e) & np.isfinite(d)
    n_valid = int(mX.sum())
    if n_valid < int(min_city_points_for_eval):
        return np.nan, 0, n_valid

    X = np.column_stack([e[mX], d[mX]]).astype(np.float64)

    counts = interp_hist_count_on_grid(X[:, 0], X[:, 1], H_count, xedges, yedges)
    support_ok = (counts >= float(support_min_count))

    qlo_pred = predict_quantile(models[qlo], X)
    qhi_pred = predict_quantile(models[qhi], X)
    W = (qhi_pred - qlo_pred).astype(np.float64)

    if not np.isfinite(W_thr):
        return np.nan, 0, int(len(W))

    in_band = (W >= float(W_thr)) & support_ok
    occ = float(np.mean(in_band)) if len(in_band) > 0 else np.nan
    return occ, int(in_band.sum()), int(len(in_band))


# =========================================================
# Cluster-wise mosaics
# =========================================================
def make_clusterwise_mosaics(df_city_key, mosaic_items_risk, mosaic_items_highcorr, fig_corr_dir, vkey, resp, state_group, mosaic_cols=3):
    if df_city_key is None or len(df_city_key) == 0:
        return

    if len(mosaic_items_risk) > 0:
        city_to_item = {it["city"]: it for it in mosaic_items_risk}
        for cl, sub in df_city_key.groupby("cluster"):
            items = [city_to_item[c] for c in sub["city"].values if c in city_to_item]
            if len(items) > 0:
                outp = os.path.join(fig_corr_dir, f"mosaic_cluster{cl}_risk_Wpred_{vkey}__RESP_{resp}__STATE_{state_group}.png")
                mosaic_city_maps(items, outp, ncols=int(mosaic_cols),
                                 title=f"Cluster {cl} risk mosaic (STATE={state_group}) — {vkey}/{resp}")

    if len(mosaic_items_highcorr) > 0:
        city_to_item = {it["city"]: it for it in mosaic_items_highcorr}
        for cl, sub in df_city_key.groupby("cluster"):
            items = [city_to_item[c] for c in sub["city"].values if c in city_to_item]
            if len(items) > 0:
                outp = os.path.join(fig_corr_dir, f"mosaic_cluster{cl}_highcorr_{vkey}__RESP_{resp}__STATE_{state_group}.png")
                mosaic_city_maps(items, outp, ncols=int(mosaic_cols),
                                 title=f"Cluster {cl} high-corridor mosaic (STATE={state_group}) — {vkey}/{resp}")


# =========================================================
# Summary helpers
# =========================================================
def _cluster_summary(df, cluster_col="cluster", agg_cols=None, prefix=""):
    if df is None or len(df) == 0:
        return pd.DataFrame()
    if agg_cols is None:
        agg_cols = []
    out_rows = []
    for cl, sub in df.groupby(cluster_col):
        row = {"cluster": cl, "n": int(len(sub))}
        for c in agg_cols:
            if c not in sub.columns:
                row[f"{prefix}{c}_mean"] = np.nan
                row[f"{prefix}{c}_median"] = np.nan
                continue
            if not np.issubdtype(sub[c].dtype, np.number):
                row[f"{prefix}{c}_mean"] = np.nan
                row[f"{prefix}{c}_median"] = np.nan
                continue
            v = sub[c].values.astype(float)
            v = v[np.isfinite(v)]
            if len(v) == 0:
                row[f"{prefix}{c}_mean"] = np.nan
                row[f"{prefix}{c}_median"] = np.nan
            else:
                row[f"{prefix}{c}_mean"] = float(np.nanmean(v))
                row[f"{prefix}{c}_median"] = float(np.nanmedian(v))
        out_rows.append(row)
    return pd.DataFrame(out_rows).sort_values("cluster")


def write_summary_xlsx(xlsx_path, sheets: Dict[str, pd.DataFrame]):
    ensure_dirs(os.path.dirname(xlsx_path))
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        for name, df in sheets.items():
            if df is None:
                df = pd.DataFrame()
            df.to_excel(writer, sheet_name=str(name)[:31], index=False)


# =========================================================
# Pooled fair sampling
# =========================================================
def stratified_city_sampling(Xm: np.ndarray, ym: np.ndarray, city: str, rng: np.random.Generator, cap: int):
    n = int(Xm.shape[0])
    if cap is None or cap <= 0 or n <= cap:
        return Xm, ym, np.array([city] * n, dtype=object)
    idx = rng.choice(np.arange(n), size=int(cap), replace=False)
    return Xm[idx, :], ym[idx], np.array([city] * int(cap), dtype=object)


# =========================================================
# Main pipeline per state / var / resp
# =========================================================
def run_pipeline_for_var_resp_state(
    era5_root: str,
    city_info: pd.DataFrame,
    cities: List[str],
    target_varspec: VarSpec,
    vkey: str,
    ews_on: str,
    resp: str,
    state_group: str,
    args: argparse.Namespace,
    out_root: str,
):
    out_v = os.path.join(
        out_root,
        f"STATE_{state_group}",
        f"VAR_{vkey}__RESP_{resp}"
    )
    fig_global = os.path.join(out_v, "fig_global")
    fig_corr = os.path.join(out_v, "fig_corridors")
    fig_perc = os.path.join(out_v, "fig_percolation")
    fig_tau = os.path.join(out_v, "fig_tau")
    fig_scaling = os.path.join(out_v, "fig_scaling")
    cache_dir = os.path.join(out_v, "_CACHE_city_arrays")

    ensure_dirs(out_v, fig_global, fig_corr, fig_perc, fig_tau, fig_scaling, cache_dir)

    print(f"\n[STATE] {state_group} | [VAR] {vkey} | [RESP] {resp}")

    floor_out = int(args.city_output_points_floor)
    floor_train_label_only = int(args.min_city_points_floor)
    min_city_points_sig = int(args.min_city_points)

    pass1_rows = []
    pooled_X, pooled_y, pooled_city = [], [], []
    pooled_n = 0
    rng = np.random.default_rng(int(args.seed) + 999)

    for city in cities:
        print(f"  [CITY] {city} :: state-conditioned threshold ...")

        try:
            thr = estimate_city_threshold_state_conditioned(
                era5_root=era5_root,
                city=city,
                target_varspec=target_varspec,
                state_group=state_group,
                tau=float(args.tau),
                year0=int(args.year0),
                year1=int(args.year1),
                max_samples=int(args.max_samples),
                sample_per_file=int(args.sample_per_file),
                seed=int(args.seed) + 11,
                day_hour_start=int(args.day_hour_start),
                day_hour_end=int(args.day_hour_end),
                shear_q=float(args.shear_q),
                shear_low_q=float(args.shear_low_q),
                shear_high_q=float(args.shear_high_q),
                shear_extreme_q=float(args.shear_extreme_q),
                gust_high_q=float(args.gust_high_q),
                gust_extreme_q=float(args.gust_extreme_q),
                blh_low_q=float(args.blh_low_q),
                blh_high_q=float(args.blh_high_q),
                event_lead_hours=int(args.event_lead_hours),
                event_lag_hours=int(args.event_lag_hours),
                event_min_gap_hours=int(args.event_min_gap_hours),
            )
        except Exception as e:
            print(f"    [SKIP] threshold failed: {e}")
            pass1_rows.append({
                "city": city,
                "thr_q_upper": np.nan,
                "cache_path": "",
                "valid_points": 0,
                "qc_flag": "OUT_FAIL",
                "qc_significant": 0,
                "qc_can_output": 0,
                "qc_in_pooled": 0,
                "used_hours_frac": np.nan,
                "used_months": 0,
                "event_hours_total": 0,
            })
            continue

        print(f"    threshold(q={1 - float(args.tau):.2f}) = {thr:.6g}")

        try:
            lat, lon, clim_ex, monthly_series_ews, meta = build_grid_products_state_conditioned(
                era5_root=era5_root,
                city=city,
                target_varspec=target_varspec,
                state_group=state_group,
                thr=thr,
                ews_on=ews_on,
                year0=int(args.year0),
                year1=int(args.year1),
                day_hour_start=int(args.day_hour_start),
                day_hour_end=int(args.day_hour_end),
                shear_q=float(args.shear_q),
                shear_low_q=float(args.shear_low_q),
                shear_high_q=float(args.shear_high_q),
                shear_extreme_q=float(args.shear_extreme_q),
                gust_high_q=float(args.gust_high_q),
                gust_extreme_q=float(args.gust_extreme_q),
                blh_low_q=float(args.blh_low_q),
                blh_high_q=float(args.blh_high_q),
                event_lead_hours=int(args.event_lead_hours),
                event_lag_hours=int(args.event_lag_hours),
                event_min_gap_hours=int(args.event_min_gap_hours),
            )
        except Exception as e:
            print(f"    [SKIP] grid-product failed: {e}")
            pass1_rows.append({
                "city": city,
                "thr_q_upper": float(thr),
                "cache_path": "",
                "valid_points": 0,
                "qc_flag": "OUT_FAIL",
                "qc_significant": 0,
                "qc_can_output": 0,
                "qc_in_pooled": 0,
                "used_hours_frac": np.nan,
                "used_months": 0,
                "event_hours_total": 0,
            })
            continue

        grid_entropy, grid_disp = compute_grid_entropy_and_dispersion(clim_ex, neigh=int(args.neigh))
        ar1_slope, var_slope = compute_grid_ews(monthly_series_ews, roll_win=int(args.roll_win))

        cache_path = os.path.join(cache_dir, f"{city}__cache_{vkey}__STATE_{state_group}.npz")
        np.savez_compressed(
            cache_path,
            lat=lat.astype(np.float32),
            lon=lon.astype(np.float32),
            grid_entropy=grid_entropy.astype(np.float32),
            grid_disp=grid_disp.astype(np.float32),
            ar1_slope=ar1_slope.astype(np.float32),
            var_slope=var_slope.astype(np.float32),
            thr_q_upper=np.float32(thr),
            used_hours_frac=np.float32(meta.get("used_hours_frac", np.nan)),
            used_months=np.int32(meta.get("used_months", 0)),
            event_hours_total=np.int32(meta.get("event_hours_total", 0)),
        )

        e = grid_entropy.ravel().astype(np.float64)
        d = grid_disp.ravel().astype(np.float64)
        y = ar1_slope.ravel().astype(np.float64) if resp == "ar1" else var_slope.ravel().astype(np.float64)

        m = np.isfinite(e) & np.isfinite(d) & np.isfinite(y)
        n_valid = int(m.sum())

        qc_flag = qc_flag_from_points(
            n_valid,
            floor_out=floor_out,
            floor_train_label_only=floor_train_label_only,
            min_city_points=min_city_points_sig,
        )
        qc_significant = bool(n_valid >= min_city_points_sig)
        qc_can_output = bool(n_valid >= floor_out)
        qc_in_pooled = bool(n_valid >= floor_out)

        if qc_in_pooled:
            Xm = np.column_stack([e[m], d[m]]).astype(np.float32)
            ym = y[m].astype(np.float32)
            cap = int(args.per_city_train_cap)
            Xm_take, ym_take, city_take = stratified_city_sampling(Xm, ym, city, rng, cap=cap)

            pooled_X.append(Xm_take)
            pooled_y.append(ym_take)
            pooled_city.append(city_take)
            pooled_n += int(Xm_take.shape[0])

        pass1_rows.append({
            "city": city,
            "thr_q_upper": float(thr),
            "cache_path": cache_path,
            "valid_points": n_valid,
            "qc_flag": qc_flag,
            "qc_significant": int(qc_significant),
            "qc_can_output": int(qc_can_output),
            "qc_in_pooled": int(qc_in_pooled),
            "used_hours_frac": float(meta.get("used_hours_frac", np.nan)),
            "used_months": int(meta.get("used_months", 0)),
            "event_hours_total": int(meta.get("event_hours_total", 0)),
        })

    if pooled_n < int(args.min_pooled_train):
        print(f"[WARN] [{state_group}/{vkey}/{resp}] pooled_n={pooled_n} < min_pooled_train={int(args.min_pooled_train)}; skipping.")
        return {
            "df_city_key": pd.DataFrame(),
            "df_occ": pd.DataFrame(),
            "df_corr": pd.DataFrame(),
            "df_perc": pd.DataFrame(),
            "df_tau": pd.DataFrame(),
            "df_scal": pd.DataFrame(),
            "df_loco": pd.DataFrame(),
            "state_group": state_group,
            "var": vkey,
            "resp": resp,
            "out_v": out_v,
        }

    X_pool = np.vstack(pooled_X).astype(np.float64)
    y_pool = np.concatenate(pooled_y).astype(np.float64)
    city_pool = np.concatenate(pooled_city)

    if X_pool.shape[0] > int(args.global_max_train):
        idx = rng.choice(np.arange(X_pool.shape[0]), size=int(args.global_max_train), replace=False)
        X_pool = X_pool[idx, :]
        y_pool = y_pool[idx]
        city_pool = city_pool[idx]
        pooled_n = int(X_pool.shape[0])

    H_count, xedges, yedges, gx, gy, _, _, mask_on_grid, _ = build_support_mask_on_phase_grid(
        X_pool, int(args.support_bins), int(args.support_min_count), int(args.grid_res)
    )
    fig_support = os.path.join(fig_global, f"fig_support_density_{vkey}__RESP_{resp}__STATE_{state_group}.png")
    plot_support_density(
        H_count, xedges, yedges, fig_support,
        title=f"Training support density in (H,D) — {vkey}/{resp} — STATE={state_group}"
    )

    quantiles = sorted(list(set([float(q) for q in args.quantiles])))
    models = fit_all_quantile_models(
        X_pool, y_pool, quantiles,
        seed=int(args.seed) + 7,
        min_quantile_samples=int(args.min_quantile_samples),
    )
    if models is None:
        raise RuntimeError(f"[{state_group}/{vkey}/{resp}] quantile fitting failed")

    Qsurfs = predict_all_surfaces(models, quantiles, gx, gy)
    for q in quantiles:
        Z = Qsurfs[q]
        p_raw = os.path.join(fig_global, f"fig_phase_Q{q:.2f}_RAW_{vkey}__RESP_{resp}__STATE_{state_group}.png")
        p_msk = os.path.join(fig_global, f"fig_phase_Q{q:.2f}_MASKED_{vkey}__RESP_{resp}__STATE_{state_group}.png")
        plot_phase(
            Z, gx, gy, p_raw,
            title=f"Quantile surface Q{q:.2f}(Slope|H,D) — {vkey}/{resp} — STATE={state_group}",
            cbar_label=f"Q{q:.2f} of slope"
        )
        plot_phase_masked(
            Z, mask_on_grid, gx, gy, p_msk,
            title=f"Q{q:.2f}(Slope|H,D), support-masked — {vkey}/{resp} — STATE={state_group}",
            cbar_label=f"Q{q:.2f} of slope"
        )

    qlo = float(args.critical_lo)
    qhi = float(args.critical_hi)
    if (qlo not in Qsurfs) or (qhi not in Qsurfs):
        raise ValueError("critical_lo/hi must be included in --quantiles")

    Wsurf = (Qsurfs[qhi] - Qsurfs[qlo]).astype(np.float64)
    fig_W_msk = os.path.join(fig_global, f"fig_phase_WIDTH_W_Q{qhi:.2f}-Q{qlo:.2f}_MASKED_{vkey}__RESP_{resp}__STATE_{state_group}.png")
    plot_phase_masked(
        Wsurf, mask_on_grid, gx, gy, fig_W_msk,
        title=f"Width W=Q{qhi:.2f}-Q{qlo:.2f} (masked) — {vkey}/{resp} — STATE={state_group}",
        cbar_label="Width"
    )

    crit_q = float(args.critical_band_q)
    W_thr = safe_quantile_threshold(Wsurf, mask_on_grid, crit_q)

    print(f"  [BOOTSTRAP] B={int(args.bootstrap_B)} ...")
    std_surfs = bootstrap_std_surfaces(
        X_pool, y_pool, quantiles, gx, gy,
        B=int(args.bootstrap_B),
        seed0=int(args.bootstrap_seed),
        min_quantile_samples=int(args.min_quantile_samples),
        max_train=int(args.bootstrap_max_train),
    )
    if std_surfs is None:
        raise RuntimeError(f"[{state_group}/{vkey}/{resp}] bootstrap std failed")

    stdW = np.sqrt(np.maximum(std_surfs[qhi].astype(np.float64) ** 2 + std_surfs[qlo].astype(np.float64) ** 2, 0.0))
    fig_W_std = os.path.join(fig_global, f"fig_phase_WIDTH_W_BOOTSTD_{vkey}__RESP_{resp}__STATE_{state_group}.png")
    plot_phase_masked(
        stdW, mask_on_grid, gx, gy, fig_W_std,
        title=f"Bootstrap std of W (masked) — {vkey}/{resp} — STATE={state_group}",
        cbar_label="Std(W)"
    )

    print("  [LOCO] pinball ...")
    df_loco = loco_pinball_evaluation(
        X_pool, y_pool, city_pool,
        quantiles=quantiles,
        seed=int(args.seed) + 1234,
        min_quantile_samples=int(args.min_quantile_samples),
        loco_max_train=int(args.loco_max_train),
    )
    df_loco["state_group"] = state_group
    df_loco["var"] = vkey
    df_loco["resp"] = resp
    df_loco["ews_on"] = ews_on
    df_loco.to_csv(os.path.join(out_v, f"loco_pinball_{vkey}__RESP_{resp}__STATE_{state_group}.csv"), index=False)

    fig_loco = os.path.join(fig_global, f"fig_LOCO_pinball_{vkey}__RESP_{resp}__STATE_{state_group}.png")
    df_loco_plot = df_loco.dropna(subset=["pinball"])
    if len(df_loco_plot) > 0:
        plot_loco_pinball(df_loco_plot, fig_loco, title=f"LOCO pinball loss — {vkey}/{resp} — STATE={state_group}")

    try:
        import pickle
        np.savez_compressed(
            os.path.join(out_v, "support_pack.npz"),
            H_count=H_count,
            xedges=xedges,
            yedges=yedges,
            support_min_count=np.int32(args.support_min_count),
            qlo=np.float64(qlo),
            qhi=np.float64(qhi),
        )
        with open(os.path.join(out_v, "models.pkl"), "wb") as f:
            pickle.dump(models, f)
    except Exception as e:
        print(f"  [WARN] failed to save support_pack/models.pkl: {e}")

    pass1_df = pd.DataFrame(pass1_rows)
    occ_rows = []

    for _, rr in pass1_df.iterrows():
        city = str(rr["city"])
        cache_path = str(rr["cache_path"])
        thr = float(rr["thr_q_upper"]) if np.isfinite(rr["thr_q_upper"]) else np.nan
        valid_points = int(rr["valid_points"])
        used_hours_frac = float(rr.get("used_hours_frac", np.nan))
        used_months = int(rr.get("used_months", 0))
        event_hours_total = int(rr.get("event_hours_total", 0))

        qc_flag = str(rr["qc_flag"])
        qc_significant = bool(int(rr["qc_significant"]) == 1)
        qc_can_output = bool(int(rr["qc_can_output"]) == 1)
        qc_in_pooled = bool(int(rr["qc_in_pooled"]) == 1)

        extrap_frac_map = np.nan
        if qc_can_output and cache_path != "":
            pack_map = build_city_risk_map_from_cache(
                cache_path=cache_path,
                models=models,
                qlo=qlo, qhi=qhi,
                H_count=H_count, xedges=xedges, yedges=yedges,
                support_min_count=int(args.support_min_count),
                allow_extrapolation=bool(args.allow_extrapolation),
                soft_clip_quantiles=(float(args.soft_clip_qlo), float(args.soft_clip_qhi)),
            )
            if pack_map is not None:
                extrap_frac_map = float(pack_map.get("extrap_frac", np.nan))

            occ, n_in, n_tot = compute_city_critical_band_occupancy(
                cache_path,
                models=models,
                qlo=qlo, qhi=qhi,
                W_thr=W_thr,
                support_min_count=int(args.support_min_count),
                H_count=H_count, xedges=xedges, yedges=yedges,
                min_city_points_for_eval=int(args.city_output_points_floor),
            )
        else:
            occ, n_in, n_tot = (np.nan, 0, valid_points)

        cinfo = city_info[city_info["city"] == city]
        cluster = float(cinfo["cluster"].values[0]) if len(cinfo) else np.nan
        city_entropy = float(cinfo["city_entropy"].values[0]) if len(cinfo) else np.nan

        occ_rows.append({
            "city": city,
            "cluster": cluster,
            "city_entropy": city_entropy,
            "state_group": state_group,
            "thr_q_upper": thr,
            "ews_on": ews_on,
            "var": vkey,
            "resp": resp,
            "valid_points": int(valid_points),
            "used_hours_frac": used_hours_frac,
            "used_months": used_months,
            "event_hours_total": event_hours_total,
            "qc_flag": qc_flag,
            "qc_significant": int(qc_significant),
            "qc_can_output": int(qc_can_output),
            "qc_in_pooled": int(qc_in_pooled),
            "allow_extrapolation_map": int(bool(args.allow_extrapolation)),
            "soft_clip_qlo": float(args.soft_clip_qlo),
            "soft_clip_qhi": float(args.soft_clip_qhi),
            "extrap_frac_map": float(extrap_frac_map) if np.isfinite(extrap_frac_map) else np.nan,
            "W_thr_support_quantile": float(crit_q),
            "W_thr_value": float(W_thr) if np.isfinite(W_thr) else np.nan,
            "critical_band_occupancy": float(occ),
            "n_band": int(n_in),
            "n_eval": int(n_tot),
        })

    df_occ = pd.DataFrame(occ_rows)
    df_occ.to_csv(os.path.join(out_v, f"city_critical_band_occupancy_{vkey}__RESP_{resp}__STATE_{state_group}.csv"), index=False)

    fig_occ = os.path.join(fig_global, f"fig_critical_band_occupancy_vs_city_entropy_{vkey}__RESP_{resp}__STATE_{state_group}.png")
    df_occ_plot = df_occ.dropna(subset=["city_entropy", "critical_band_occupancy"])
    if len(df_occ_plot) > 0:
        plot_scatter_city_entropy(
            df_occ_plot,
            xcol="city_entropy",
            ycol="critical_band_occupancy",
            outpath=fig_occ,
            title=f"Critical-band occupancy vs city entropy — {vkey}/{resp} — STATE={state_group}",
            xlabel="City-level entropy (window_entropy)",
            ylabel="Critical-band occupancy"
        )

    pooled_W = compute_W_for_points(models, qlo, qhi, X_pool[:, 0], X_pool[:, 1])
    vmin_r, vmax_r = safe_vmin_vmax_from_arrays([pooled_W, Wsurf], qlo=0.02, qhi=0.98, fallback=(0.0, 1.0))

    mosaic_items_risk = []
    mosaic_items_highcorr = []
    corr_rows = []
    perc_rows = []
    tau_rows = []
    scaling_rows = []
    city_key_rows = []

    allow_extrap = bool(args.allow_extrapolation)
    soft_q = (float(args.soft_clip_qlo), float(args.soft_clip_qhi))

    for _, rr in pass1_df.iterrows():
        city = str(rr["city"])
        cache_path = str(rr["cache_path"])
        valid_points = int(rr.get("valid_points", 0))
        used_hours_frac = float(rr.get("used_hours_frac", np.nan))
        used_months = int(rr.get("used_months", 0))
        event_hours_total = int(rr.get("event_hours_total", 0))
        qc_can_output = bool(int(rr["qc_can_output"]) == 1)
        qc_significant = bool(int(rr["qc_significant"]) == 1)
        qc_flag = str(rr["qc_flag"])

        cinfo = city_info[city_info["city"] == city]
        cluster = float(cinfo["cluster"].values[0]) if len(cinfo) else np.nan
        city_entropy = float(cinfo["city_entropy"].values[0]) if len(cinfo) else np.nan

        city_key_rows.append({
            "city": city,
            "cluster": cluster,
            "city_entropy": city_entropy,
            "state_group": state_group,
            "var": vkey,
            "resp": resp,
            "ews_on": ews_on,
            "valid_points": int(valid_points),
            "used_hours_frac": used_hours_frac,
            "used_months": used_months,
            "event_hours_total": event_hours_total,
            "qc_flag": qc_flag,
            "qc_significant": int(qc_significant),
            "qc_can_output": int(qc_can_output),
        })

        if (not qc_can_output) or (cache_path == ""):
            continue

        pack = build_city_risk_map_from_cache(
            cache_path=cache_path,
            models=models,
            qlo=qlo, qhi=qhi,
            H_count=H_count, xedges=xedges, yedges=yedges,
            support_min_count=int(args.support_min_count),
            allow_extrapolation=allow_extrap,
            soft_clip_quantiles=soft_q,
        )
        if pack is None:
            continue

        lat = pack["lat"]
        lon = pack["lon"]
        risk_map = pack["risk2d"]
        support_count2d = pack["support_count2d"]
        extrap_mask2d = pack["extrap_mask2d"]
        extrap_frac = float(pack.get("extrap_frac", np.nan))

        if bool(args.make_corridors):
            p_risk = os.path.join(fig_corr, f"fig_city_risk_Wpred_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png")
            plot_city_risk_map(
                lat, lon, risk_map, p_risk,
                title=f"City corridor-risk map — {city} — {vkey}/{resp} — STATE={state_group}",
                cbar_label="Corridor-risk width", vmin=vmin_r, vmax=vmax_r
            )
            mosaic_items_risk.append({"city": city, "lat": lat, "lon": lon, "Z": risk_map, "vmin": vmin_r, "vmax": vmax_r})

            plot_city_support_count(
                lat, lon, support_count2d,
                os.path.join(fig_corr, f"fig_city_support_count_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png"),
                title=f"Support count (H,D) — {city} — {vkey}/{resp} — STATE={state_group}"
            )

            plot_city_extrap_mask(
                lat, lon, extrap_mask2d,
                os.path.join(fig_corr, f"fig_city_extrap_mask_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png"),
                title=f"Extrapolation mask — {city} — {vkey}/{resp} — STATE={state_group} | extrap_frac={extrap_frac:.3f}"
            )

            ph_pack = corridor_ph_backbone(
                W_pred_2d=risk_map,
                support_mask=np.isfinite(risk_map),
                alpha=float(args.ph_alpha),
                top_k=int(args.ph_top_k),
                persistence_min_mode=str(args.ph_persistence_mode),
                persistence_min_value=float(args.ph_persistence_value),
                make_skeleton=bool(args.ph_make_skeleton),
                connectivity=4,
            )

            if ph_pack is not None:
                hi_mask = ph_pack["corridor_mask"].astype(np.uint8)
                sk_mask = ph_pack["skeleton_mask"].astype(np.uint8)

                hi_metrics = corridor_topology_metrics(hi_mask, connectivity=4)
                sk_metrics = corridor_topology_metrics(sk_mask, connectivity=4)

                hi_pca = corridor_pca_anisotropy(
                    sk_mask if int(np.sum(sk_mask)) > 0 else hi_mask,
                    mode="largest"
                )

                corr_rows.append({
                    "city": city,
                    "cluster": cluster,
                    "city_entropy": city_entropy,
                    "state_group": state_group,
                    "var": vkey,
                    "resp": resp,
                    "ews_on": ews_on,
                    "valid_points": int(valid_points),
                    "used_hours_frac": used_hours_frac,
                    "used_months": used_months,
                    "event_hours_total": event_hours_total,
                    "qc_flag": qc_flag,
                    "qc_significant": int(qc_significant),
                    "allow_extrapolation_map": int(allow_extrap),
                    "extrap_frac_map": float(extrap_frac) if np.isfinite(extrap_frac) else np.nan,

                    "corridor_method": ph_pack["method"],
                    "ph_alpha": float(args.ph_alpha),
                    "ph_top_k": int(args.ph_top_k),
                    "ph_persistence_mode": str(args.ph_persistence_mode),
                    "ph_persistence_value": float(args.ph_persistence_value),

                    "PH_n_support": int(ph_pack["n_support"]),
                    "PH_tau": float(ph_pack["tau"]),
                    "PH_theta_star": float(ph_pack["theta_star"]),
                    "PH_selected_birth": float(ph_pack["selected_birth"]),
                    "PH_selected_death": float(ph_pack["selected_death"]),
                    "PH_selected_persistence": float(ph_pack["selected_persistence"]),

                    "CP0_max": float(ph_pack["cp0_max"]),
                    "CP0_sum": float(ph_pack["cp0_sum"]),
                    "CP1_sum": float(ph_pack["cp1_sum"]),
                    "corridor_persistence_index": float(ph_pack["corridor_persistence_index"]),
                    "loop_suppression_index": float(ph_pack["loop_suppression_index"]),

                    "HIGH_area_frac": hi_metrics["area_frac"],
                    "HIGH_n_components": hi_metrics["n_components"],
                    "HIGH_largest_frac": hi_metrics["largest_frac"],
                    "HIGH_size_gini": hi_metrics["size_gini"],
                    "HIGH_perimeter_per_area": hi_metrics["perimeter_per_area"],

                    "SKEL_area_frac": sk_metrics["area_frac"],
                    "SKEL_n_components": sk_metrics["n_components"],
                    "SKEL_largest_frac": sk_metrics["largest_frac"],
                    "SKEL_size_gini": sk_metrics["size_gini"],
                    "SKEL_perimeter_per_area": sk_metrics["perimeter_per_area"],

                    "HIGH_pca_n": hi_pca["pca_n"],
                    "HIGH_pca_lambda1": hi_pca["pca_lambda1"],
                    "HIGH_pca_lambda2": hi_pca["pca_lambda2"],
                    "HIGH_pca_angle_deg": hi_pca["pca_angle_deg"],
                    "HIGH_pca_anisotropy": hi_pca["pca_anisotropy"],
                })

                p_hi = os.path.join(fig_corr, f"fig_city_high_corridor_mask_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png")
                plot_city_mask(
                    lat, lon, hi_mask, p_hi,
                    title=f"Safety-corridor mask (theta*={ph_pack['theta_star']:.4g}) — {city} — {vkey}/{resp} — STATE={state_group}",
                    cbar_label="Passable corridor mask"
                )

                p_sk = os.path.join(fig_corr, f"fig_city_skeleton_corridor_mask_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png")
                plot_city_mask(
                    lat, lon, sk_mask, p_sk,
                    title=f"Safety-corridor skeleton — {city} — {vkey}/{resp} — STATE={state_group}",
                    cbar_label="Corridor skeleton"
                )

                mosaic_items_highcorr.append({
                    "city": city,
                    "lat": lat,
                    "lon": lon,
                    "Z": hi_mask.astype(float),
                    "vmin": 0.0,
                    "vmax": 1.0,
                })

                save_ph_pairs_json(
                    os.path.join(fig_corr, f"ph_pairs_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.json"),
                    ph_pack
                )

        if bool(args.make_percolation):
            dfp, hist_pack = percolation_scan_full(
                risk_map,
                levels=int(args.perc_levels),
                connectivity=int(args.perc_connectivity),
                smooth_win=int(args.perc_smooth_win),
            )
            if dfp is None or hist_pack is None:
                continue

            theta_c_S = float(dfp.attrs.get("theta_c_S", np.nan))
            q_c_S = float(dfp.attrs.get("q_c_S", np.nan))
            p_c_S = float(dfp.attrs.get("p_c_S", np.nan))
            idx_c_S = int(dfp.attrs.get("idx_c_S", -1))
            pc_method = str(dfp.attrs.get("pc_method", "unknown"))
            N_eff = int(dfp["N_eff"].iloc[0]) if "N_eff" in dfp.columns and len(dfp) > 0 else int(hist_pack.get("N_eff", -1))

            dSdp_peak = np.nan
            if "dSdp" in dfp.columns:
                ds = dfp["dSdp"].values.astype(float)
                if np.any(np.isfinite(ds)):
                    dSdp_peak = float(np.nanmax(ds))

            perc_rows.append({
                "city": city,
                "cluster": cluster,
                "city_entropy": city_entropy,
                "state_group": state_group,
                "var": vkey,
                "resp": resp,
                "ews_on": ews_on,
                "valid_points": int(valid_points),
                "used_hours_frac": used_hours_frac,
                "used_months": used_months,
                "event_hours_total": event_hours_total,
                "qc_flag": qc_flag,
                "qc_significant": int(qc_significant),
                "allow_extrapolation_map": int(allow_extrap),
                "extrap_frac_map": float(extrap_frac) if np.isfinite(extrap_frac) else np.nan,

                "theta_c_S": theta_c_S,
                "q_c_S": q_c_S,
                "p_c_S": p_c_S,
                "pc_method": pc_method,
                "dSdp_peak": dSdp_peak,
                "perc_levels": int(args.perc_levels),
                "connectivity": int(args.perc_connectivity),
                "S_smooth_win": int(args.perc_smooth_win),
                "N_eff": int(N_eff),
            })

            curve_csv = os.path.join(fig_perc, f"percolation_curve_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.csv")
            dfp.to_csv(curve_csv, index=False)

            figp = os.path.join(fig_perc, f"fig_percolation_GS_theta_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png")
            plot_percolation(
                dfp,
                figp,
                title=f"Corridor-fragmentation percolation — {city} — {vkey}/{resp} — STATE={state_group}"
            )

            hist_npz = os.path.join(fig_perc, f"cluster_hist_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.npz")
            save_cluster_hist_npz(hist_npz, hist_pack)

            if bool(getattr(args, "perc_tau_fit", False)) and idx_c_S >= 0:
                tau_fit = tau_fit_from_hist_pack_at_index(
                    hist_pack, idx=idx_c_S,
                    bins=int(args.tau_fit_bins),
                    smin=int(args.tau_smin),
                    smax_quantile=float(args.tau_smax_quantile),
                    min_points=int(args.tau_fit_min_points),
                )
                if tau_fit is not None:
                    tau_rows.append({
                        "city": city,
                        "cluster": cluster,
                        "city_entropy": city_entropy,
                        "state_group": state_group,
                        "var": vkey,
                        "resp": resp,
                        "ews_on": ews_on,
                        "valid_points": int(valid_points),
                        "used_hours_frac": used_hours_frac,
                        "used_months": used_months,
                        "event_hours_total": event_hours_total,
                        "qc_flag": qc_flag,
                        "qc_significant": int(qc_significant),
                        "allow_extrapolation_map": int(allow_extrap),
                        "extrap_frac_map": float(extrap_frac) if np.isfinite(extrap_frac) else np.nan,

                        "theta_c_S": theta_c_S,
                        "q_c_S": q_c_S,
                        "p_c_S": p_c_S,
                        "pc_method": pc_method,
                        "tau_lr": float(tau_fit["tau_lr"]),
                        "r2_lr": float(tau_fit["r2_lr"]),
                        "tau_mle": float(tau_fit["tau_mle"]),
                        "n_mle": int(tau_fit["n_mle"]),
                        "smin": int(tau_fit["smin"]),
                        "smax": int(tau_fit["smax"]),
                        "tau_bins": int(args.tau_fit_bins),
                    })
                    fig_tau_city = os.path.join(fig_tau, f"fig_tau_fit_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png")
                    plot_tau_fit(
                        tau_fit["centers"], tau_fit["n_s"], tau_fit["tau_lr"],
                        fig_tau_city,
                        title=f"Finite-cluster size distribution at corridor break-up threshold — {city} — STATE={state_group}"
                    )

            scaling = fit_beta_gamma_from_perc_curve_ppc(
                dfp,
                p_c=p_c_S,
                window_frac=float(args.scaling_window_frac),
                min_points=int(args.scaling_min_points),
                r2_min=float(args.scaling_r2_min),
            )
            scaling_rows.append({
                "city": city,
                "cluster": cluster,
                "city_entropy": city_entropy,
                "state_group": state_group,
                "var": vkey,
                "resp": resp,
                "ews_on": ews_on,
                "valid_points": int(valid_points),
                "used_hours_frac": used_hours_frac,
                "used_months": used_months,
                "event_hours_total": event_hours_total,
                "qc_flag": qc_flag,
                "qc_significant": int(qc_significant),
                "allow_extrapolation_map": int(allow_extrap),
                "extrap_frac_map": float(extrap_frac) if np.isfinite(extrap_frac) else np.nan,

                "theta_c_S": theta_c_S,
                "q_c_S": q_c_S,
                "p_c_S": p_c_S,
                "pc_method": pc_method,
                "beta": scaling["beta"],
                "beta_r2": scaling["beta_r2"],
                "beta_n": scaling["beta_n"],
                "gamma": scaling["gamma"],
                "gamma_r2": scaling["gamma_r2"],
                "gamma_n": scaling["gamma_n"],
                "beta_window_lo": scaling["beta_window_lo"],
                "beta_window_hi": scaling["beta_window_hi"],
                "gamma_window_lo": scaling["gamma_window_lo"],
                "gamma_window_hi": scaling["gamma_window_hi"],
                "scaling_window_frac": float(args.scaling_window_frac),
                "scaling_r2_min": float(args.scaling_r2_min),
            })
            fig_scal = os.path.join(fig_scaling, f"fig_scaling_beta_gamma_{city}_{vkey}__RESP_{resp}__STATE_{state_group}.png")
            plot_scaling_fits_ppc(
                dfp, p_c_S, fig_scal,
                title=f"Scaling fits near corridor break-up threshold — {city} — {vkey}/{resp} — STATE={state_group}",
                window_frac=float(args.scaling_window_frac)
            )

    df_city_key = pd.DataFrame(city_key_rows)

    if bool(args.make_corridors) and len(mosaic_items_risk) > 0:
        mosaic_city_maps(
            mosaic_items_risk,
            os.path.join(fig_corr, f"mosaic_city_risk_Wpred_{vkey}__RESP_{resp}__STATE_{state_group}.png"),
            ncols=int(args.mosaic_cols),
            title=f"City corridor-risk mosaic — {vkey}/{resp} — STATE={state_group}"
        )
    if bool(args.make_corridors) and len(mosaic_items_highcorr) > 0:
        mosaic_city_maps(
            mosaic_items_highcorr,
            os.path.join(fig_corr, f"mosaic_city_high_corridor_{vkey}__RESP_{resp}__STATE_{state_group}.png"),
            ncols=int(args.mosaic_cols),
            title=f"City safety-corridor mosaic — {vkey}/{resp} — STATE={state_group}"
        )
    if bool(args.make_corridors) and len(df_city_key) > 0:
        make_clusterwise_mosaics(
            df_city_key, mosaic_items_risk, mosaic_items_highcorr,
            fig_corr, vkey, resp, state_group, mosaic_cols=int(args.mosaic_cols)
        )

    df_corr = pd.DataFrame(corr_rows) if len(corr_rows) > 0 else pd.DataFrame()
    df_perc = pd.DataFrame(perc_rows) if len(perc_rows) > 0 else pd.DataFrame()
    df_tau = pd.DataFrame(tau_rows) if len(tau_rows) > 0 else pd.DataFrame()
    df_scal = pd.DataFrame(scaling_rows) if len(scaling_rows) > 0 else pd.DataFrame()

    if len(df_corr) > 0:
        df_corr.to_csv(os.path.join(out_v, f"corridor_metrics_city_{vkey}__RESP_{resp}__STATE_{state_group}.csv"), index=False)
    if len(df_perc) > 0:
        df_perc.to_csv(os.path.join(out_v, f"city_percolation_critical_{vkey}__RESP_{resp}__STATE_{state_group}.csv"), index=False)
    if len(df_tau) > 0:
        df_tau.to_csv(os.path.join(out_v, f"tau_fit_city_{vkey}__RESP_{resp}__STATE_{state_group}.csv"), index=False)
    if len(df_scal) > 0:
        df_scal.to_csv(os.path.join(out_v, f"scaling_beta_gamma_city_{vkey}__RESP_{resp}__STATE_{state_group}.csv"), index=False)

    df_occ_cluster = _cluster_summary(df_occ, agg_cols=["critical_band_occupancy", "city_entropy"], prefix="occ_") if len(df_occ) > 0 else pd.DataFrame()
    df_corr_cluster = _cluster_summary(df_corr, agg_cols=[
        "HIGH_area_frac", "HIGH_largest_frac", "HIGH_size_gini", "HIGH_pca_anisotropy",
        "SKEL_area_frac", "SKEL_largest_frac", "SKEL_size_gini",
        "CP0_max", "CP0_sum", "CP1_sum",
        "corridor_persistence_index", "loop_suppression_index"
    ], prefix="corr_") if len(df_corr) > 0 else pd.DataFrame()
    df_perc_cluster = _cluster_summary(df_perc, agg_cols=["theta_c_S", "p_c_S", "dSdp_peak"], prefix="perc_") if len(df_perc) > 0 else pd.DataFrame()
    df_tau_cluster = _cluster_summary(df_tau, agg_cols=["tau_lr", "tau_mle"], prefix="tau_") if len(df_tau) > 0 else pd.DataFrame()
    df_scal_cluster = _cluster_summary(df_scal, agg_cols=["beta", "gamma", "beta_r2", "gamma_r2"], prefix="scal_") if len(df_scal) > 0 else pd.DataFrame()

    xlsx_path = os.path.join(out_v, f"SUMMARY_TABLES_{vkey}__RESP_{resp}__STATE_{state_group}.xlsx")
    write_summary_xlsx(xlsx_path, {
        "CITY_KEY": df_city_key,
        "OCC_CITY": df_occ,
        "CORRIDOR_CITY": df_corr,
        "PERC_CITY": df_perc,
        "TAU_CITY": df_tau,
        "SCALING_CITY": df_scal,
        "LOCO": df_loco,
        "OCC_CLUSTER": df_occ_cluster,
        "CORR_CLUSTER": df_corr_cluster,
        "PERC_CLUSTER": df_perc_cluster,
        "TAU_CLUSTER": df_tau_cluster,
        "SCAL_CLUSTER": df_scal_cluster,
    })
    print(f"[OK] summary xlsx -> {xlsx_path}")

    with open(os.path.join(out_v, f"run_info_{vkey}__RESP_{resp}__STATE_{state_group}.txt"), "w") as f:
        f.write("LOW-ALTITUDE SAFETY CORRIDOR DYNAMICS PIPELINE v2\n")
        f.write(f"State group: {state_group}\n")
        f.write(f"Variable: {vkey}\n")
        f.write(f"EWS_on: {ews_on}\n")
        f.write(f"Response: {resp}\n")
        f.write(f"Pooled_n: {int(pooled_n)}\n")
        f.write(f"W_thr: {float(W_thr) if np.isfinite(W_thr) else np.nan}\n")
        f.write(f"city_output_points_floor: {int(args.city_output_points_floor)}\n")
        f.write(f"min_city_points_floor: {int(args.min_city_points_floor)}\n")
        f.write(f"min_city_points: {int(args.min_city_points)}\n")
        f.write(f"per_city_train_cap: {int(args.per_city_train_cap)}\n")
        f.write(f"allow_extrapolation: {int(bool(args.allow_extrapolation))}\n")
        f.write(f"soft_clip_quantiles: {float(args.soft_clip_qlo)}, {float(args.soft_clip_qhi)}\n")
        f.write(f"make_corridors: {int(bool(args.make_corridors))}\n")
        f.write(f"PH installed: {int(bool(_HAS_GUDHI))}\n")
        f.write(f"PH alpha: {float(args.ph_alpha)}\n")
        f.write(f"PH top_k: {int(args.ph_top_k)}\n")
        f.write(f"PH persistence_mode: {str(args.ph_persistence_mode)}\n")
        f.write(f"PH persistence_value: {float(args.ph_persistence_value)}\n")
        f.write(f"PH skeletonize: {int(bool(args.ph_make_skeleton))}\n")
        f.write(f"make_percolation: {int(bool(args.make_percolation))}\n")
        f.write(f"perc_tau_fit: {int(bool(args.perc_tau_fit))}\n")
        f.write(f"scaling_window_frac: {float(args.scaling_window_frac)}\n")
        f.write(f"scaling_min_points: {int(args.scaling_min_points)}\n")
        f.write(f"scaling_r2_min: {float(args.scaling_r2_min)}\n")
        f.write(f"day_hour_start: {int(args.day_hour_start)}\n")
        f.write(f"day_hour_end: {int(args.day_hour_end)}\n")
        f.write(f"shear_q: {float(args.shear_q)}\n")
        f.write(f"shear_low_q: {float(args.shear_low_q)}\n")
        f.write(f"shear_high_q: {float(args.shear_high_q)}\n")
        f.write(f"shear_extreme_q: {float(args.shear_extreme_q)}\n")
        f.write(f"gust_high_q: {float(args.gust_high_q)}\n")
        f.write(f"gust_extreme_q: {float(args.gust_extreme_q)}\n")
        f.write(f"blh_low_q: {float(args.blh_low_q)}\n")
        f.write(f"blh_high_q: {float(args.blh_high_q)}\n")
        f.write(f"event_lead_hours: {int(args.event_lead_hours)}\n")
        f.write(f"event_lag_hours: {int(args.event_lag_hours)}\n")
        f.write(f"event_min_gap_hours: {int(args.event_min_gap_hours)}\n")

    print(f"[DONE] STATE={state_group} | {vkey}/{resp} -> {out_v}")
    return {
        "df_city_key": df_city_key,
        "df_occ": df_occ,
        "df_corr": df_corr,
        "df_perc": df_perc,
        "df_tau": df_tau,
        "df_scal": df_scal,
        "df_loco": df_loco,
        "state_group": state_group,
        "var": vkey,
        "resp": resp,
        "xlsx_path": xlsx_path,
        "out_v": out_v,
    }


# =========================================================
# Global summary
# =========================================================
def aggregate_global_summaries(results_list, out_dir):
    ensure_dirs(out_dir)
    city_key_all, occ_all, corr_all, perc_all, tau_all, scal_all, loco_all = [], [], [], [], [], [], []

    for r in results_list:
        if r is None:
            continue
        for k, acc in [
            ("df_city_key", city_key_all),
            ("df_occ", occ_all),
            ("df_corr", corr_all),
            ("df_perc", perc_all),
            ("df_tau", tau_all),
            ("df_scal", scal_all),
            ("df_loco", loco_all),
        ]:
            if (k in r) and (r[k] is not None) and (len(r[k]) > 0):
                acc.append(r[k])

    df_city_key = pd.concat(city_key_all, ignore_index=True) if len(city_key_all) else pd.DataFrame()
    df_occ = pd.concat(occ_all, ignore_index=True) if len(occ_all) else pd.DataFrame()
    df_corr = pd.concat(corr_all, ignore_index=True) if len(corr_all) else pd.DataFrame()
    df_perc = pd.concat(perc_all, ignore_index=True) if len(perc_all) else pd.DataFrame()
    df_tau = pd.concat(tau_all, ignore_index=True) if len(tau_all) else pd.DataFrame()
    df_scal = pd.concat(scal_all, ignore_index=True) if len(scal_all) else pd.DataFrame()
    df_loco = pd.concat(loco_all, ignore_index=True) if len(loco_all) else pd.DataFrame()

    key_cols = [c for c in ["city", "var", "resp", "ews_on", "state_group"] if c in df_city_key.columns]
    merged_key = df_city_key.copy()

    if len(df_occ) > 0 and len(key_cols) > 0:
        occ_cols = [c for c in [
            "city", "var", "resp", "ews_on", "state_group",
            "critical_band_occupancy", "W_thr_value",
            "valid_points", "qc_significant", "qc_flag",
            "extrap_frac_map", "used_hours_frac", "used_months", "event_hours_total"
        ] if c in df_occ.columns]
        if len(occ_cols) >= 2:
            merged_key = merged_key.merge(df_occ[occ_cols], on=key_cols, how="left")

    if len(df_corr) > 0 and len(key_cols) > 0:
        corr_cols = [c for c in [
            "city", "var", "resp", "ews_on", "state_group",
            "corridor_persistence_index",
            "loop_suppression_index",
            "CP0_max", "CP0_sum", "CP1_sum",
            "HIGH_pca_anisotropy",
            "HIGH_largest_frac"
        ] if c in df_corr.columns]
        if len(corr_cols) >= 2:
            merged_key = merged_key.merge(df_corr[corr_cols], on=key_cols, how="left")

    if len(df_perc) > 0 and len(key_cols) > 0:
        perc_cols = [c for c in [
            "city", "var", "resp", "ews_on", "state_group",
            "theta_c_S", "q_c_S", "p_c_S", "pc_method", "dSdp_peak"
        ] if c in df_perc.columns]
        if len(perc_cols) >= 2:
            merged_key = merged_key.merge(df_perc[perc_cols], on=key_cols, how="left")

    if len(df_scal) > 0 and len(key_cols) > 0:
        scal_cols = [c for c in [
            "city", "var", "resp", "ews_on", "state_group",
            "beta", "beta_r2", "gamma", "gamma_r2"
        ] if c in df_scal.columns]
        if len(scal_cols) >= 2:
            merged_key = merged_key.merge(df_scal[scal_cols], on=key_cols, how="left")

    merged_csv = os.path.join(out_dir, "GLOBAL_MERGED_CITY_KEY.csv")
    merged_key.to_csv(merged_csv, index=False)

    xlsx_path = os.path.join(out_dir, "GLOBAL_SUMMARY_ALL.xlsx")
    write_summary_xlsx(xlsx_path, {
        "CITY_KEY_ALL": df_city_key,
        "OCC_ALL": df_occ,
        "CORRIDOR_ALL": df_corr,
        "PERC_ALL": df_perc,
        "TAU_ALL": df_tau,
        "SCALING_ALL": df_scal,
        "LOCO_ALL": df_loco,
        "MERGED_CITY_KEY": merged_key,
    })
    print(f"[OK] global summary xlsx -> {xlsx_path}")
    print(f"[OK] merged key csv -> {merged_csv}")


# =========================================================
# Main
# =========================================================
def main():
    set_topjournal_rcparams()

    parser = argparse.ArgumentParser()

    parser.add_argument("--era5_root", required=True)
    parser.add_argument("--city_level_root", required=True)

    parser.add_argument("--cities", nargs="*", default=None)
    parser.add_argument("--state_group", nargs="+", required=True, choices=sorted(list(VALID_STATE_GROUPS)))
    parser.add_argument("--responses", nargs="+", default=["var", "ar1"], choices=["var", "ar1"])
    parser.add_argument("--ews_on", type=str, default="raw_mean", choices=["exceed", "raw_mean", "raw_p95"])

    parser.add_argument("--year0", type=int, default=2015)
    parser.add_argument("--year1", type=int, default=2025)
    parser.add_argument("--tau", type=float, default=0.10)
    parser.add_argument("--roll_win", type=int, default=24)
    parser.add_argument("--neigh", type=int, default=3)

    parser.add_argument("--sample_per_file", type=int, default=12000)
    parser.add_argument("--max_samples", type=int, default=1500000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--global_max_train", type=int, default=800000)

    parser.add_argument("--support_bins", type=int, default=70)
    parser.add_argument("--support_min_count", type=int, default=5)
    parser.add_argument("--grid_res", type=int, default=180)

    parser.add_argument("--bootstrap_B", type=int, default=80)
    parser.add_argument("--bootstrap_seed", type=int, default=2026)
    parser.add_argument("--bootstrap_max_train", type=int, default=250000)

    parser.add_argument("--quantiles", nargs="+", type=float,
                        default=[0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95])
    parser.add_argument("--critical_lo", type=float, default=0.10)
    parser.add_argument("--critical_hi", type=float, default=0.90)
    parser.add_argument("--critical_band_q", type=float, default=0.90)

    parser.add_argument("--city_output_points_floor", type=int, default=1)
    parser.add_argument("--min_city_points_floor", type=int, default=2)
    parser.add_argument("--min_city_points", type=int, default=200)

    parser.add_argument("--per_city_train_cap", type=int, default=20000)
    parser.add_argument("--min_pooled_train", type=int, default=600)
    parser.add_argument("--min_quantile_samples", type=int, default=250)
    parser.add_argument("--loco_max_train", type=int, default=200000)

    parser.add_argument("--allow_extrapolation", action="store_true")
    parser.add_argument("--soft_clip_qlo", type=float, default=0.01)
    parser.add_argument("--soft_clip_qhi", type=float, default=0.99)

    parser.add_argument("--make_corridors", action="store_true")
    parser.add_argument("--mosaic_cols", type=int, default=3)

    parser.add_argument("--ph_alpha", type=float, default=0.65)
    parser.add_argument("--ph_top_k", type=int, default=1)
    parser.add_argument("--ph_persistence_mode", type=str, default="quantile", choices=["quantile", "absolute"])
    parser.add_argument("--ph_persistence_value", type=float, default=0.50)
    parser.add_argument("--ph_make_skeleton", action="store_true")

    parser.add_argument("--make_percolation", action="store_true")
    parser.add_argument("--perc_levels", type=int, default=31)
    parser.add_argument("--perc_connectivity", type=int, default=4, choices=[4, 8])
    parser.add_argument("--perc_smooth_win", type=int, default=5)

    parser.add_argument("--perc_tau_fit", action="store_true")
    parser.add_argument("--tau_fit_bins", type=int, default=22)
    parser.add_argument("--tau_smin", type=int, default=2)
    parser.add_argument("--tau_smax_quantile", type=float, default=0.95)
    parser.add_argument("--tau_fit_min_points", type=int, default=10)

    parser.add_argument("--scaling_window_frac", type=float, default=0.25)
    parser.add_argument("--scaling_min_points", type=int, default=8)
    parser.add_argument("--scaling_r2_min", type=float, default=0.55)

    parser.add_argument("--day_hour_start", type=int, default=8)
    parser.add_argument("--day_hour_end", type=int, default=18)

    parser.add_argument("--shear_q", type=float, default=0.50)
    parser.add_argument("--shear_low_q", type=float, default=0.30)
    parser.add_argument("--shear_high_q", type=float, default=0.70)
    parser.add_argument("--shear_extreme_q", type=float, default=0.90)

    parser.add_argument("--gust_high_q", type=float, default=0.70)
    parser.add_argument("--gust_extreme_q", type=float, default=0.90)

    parser.add_argument("--blh_low_q", type=float, default=0.30)
    parser.add_argument("--blh_high_q", type=float, default=0.70)

    parser.add_argument("--event_lead_hours", type=int, default=6)
    parser.add_argument("--event_lag_hours", type=int, default=6)
    parser.add_argument("--event_min_gap_hours", type=int, default=6)

    args = parser.parse_args()

    if (args.make_corridors or args.make_percolation) and (cc_label is None):
        raise RuntimeError(
            "SciPy is required for connected components (corridor/percolation). Install:\n"
            "  conda install -c conda-forge scipy\n"
        )

    era5_root = args.era5_root
    city_level_root = args.city_level_root

    city_metrics_path = os.path.join(city_level_root, "_ANALYSIS_v45_metrics", "metrics_city_table.csv")
    city_cluster_path = os.path.join(city_level_root, "_ANALYSIS_v45_metrics", "cluster_assignments.csv")
    if not os.path.exists(city_metrics_path):
        raise FileNotFoundError(f"City metrics not found: {city_metrics_path}")
    if not os.path.exists(city_cluster_path):
        raise FileNotFoundError(f"City clusters not found: {city_cluster_path}")

    city_metrics = pd.read_csv(city_metrics_path)
    city_clusters = pd.read_csv(city_cluster_path)
    city_info = city_metrics.merge(city_clusters[["city", "cluster"]], on="city", how="left")
    city_info = city_info[["city", "window_entropy", "cluster"]].rename(columns={"window_entropy": "city_entropy"})

    if args.cities is None or len(args.cities) == 0:
        cities = find_all_cities(era5_root)
    else:
        cities = args.cities

    cities = [c for c in cities if c in set(city_info["city"].values)]
    if len(cities) == 0:
        raise RuntimeError("No cities matched between ERA5 folders and city-level cluster table.")

    var_specs = build_var_specs()
    vars_to_run = ["wind10", "wind100"]

    out_root = os.path.join(
        city_level_root,
        "_ANALYSIS_v45_metrics",
        "_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR"
    )
    ensure_dirs(out_root)

    results_list = []
    for state_group in args.state_group:
        for vkey in vars_to_run:
            target_varspec = var_specs[vkey]
            for resp in args.responses:
                r = run_pipeline_for_var_resp_state(
                    era5_root=era5_root,
                    city_info=city_info,
                    cities=cities,
                    target_varspec=target_varspec,
                    vkey=vkey,
                    ews_on=str(args.ews_on),
                    resp=resp,
                    state_group=state_group,
                    args=args,
                    out_root=out_root,
                )
                results_list.append(r)

    summary_out_dir = os.path.join(out_root, "_SUMMARY_TABLES")
    aggregate_global_summaries(results_list, summary_out_dir)

    print("\n[ALL DONE]")
    print(f"Outputs root: {out_root}")


if __name__ == "__main__":
    try:
        import multiprocessing as mp
        mp.set_start_method("spawn", force=True)
    except Exception:
        pass
    main()