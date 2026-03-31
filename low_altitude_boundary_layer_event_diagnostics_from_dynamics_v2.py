#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 16:30:56 2026



/opt/anaconda3/envs/raynode/bin/python "<PROJECT_ROOT>/low_altitude_boundary_layer_event_diagnostics_from_dynamics_v2.py" \
  --era5_root "<ERA5_ROOT>" \
  --dynamics_root "<ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR" \
  --merged_csv "<ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR/_SUMMARY_TABLES/GLOBAL_MERGED_CITY_KEY.csv" \
  --output_root "<ERA5_ROOT>/_GLOBAL/AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR/_BOUNDARY_LAYER_EVENT_DIAGNOSTICS"
"""

#!/opt/anaconda3/envs/raynode/bin/python
# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import glob
import json
import math
import zipfile
import argparse
import warnings
import tempfile
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

try:
    from scipy.ndimage import gaussian_filter1d
    from scipy.stats import spearmanr
except Exception:
    gaussian_filter1d = None
    spearmanr = None

try:
    from sklearn.linear_model import LinearRegression, Ridge
    from sklearn.metrics import r2_score
    from sklearn.preprocessing import SplineTransformer
    from sklearn.pipeline import make_pipeline
    _HAS_SKLEARN = True
except Exception:
    LinearRegression = None
    Ridge = None
    r2_score = None
    SplineTransformer = None
    make_pipeline = None
    _HAS_SKLEARN = False


EPS = 1e-12

# =========================================================
# DEFAULT PATHS
# =========================================================
DEFAULT_ERA5_ROOT = (
    "<ERA5_ROOT>"
)

DEFAULT_DYNAMICS_ROOT = (
    "<ERA5_ROOT>/_GLOBAL/"
    "AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/"
    "_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR"
)

DEFAULT_MERGED_CSV = (
    "<ERA5_ROOT>/_GLOBAL/"
    "AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/"
    "_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR/_SUMMARY_TABLES/GLOBAL_MERGED_CITY_KEY.csv"
)

DEFAULT_OUTPUT_ROOT = (
    "<ERA5_ROOT>/_GLOBAL/"
    "AI_dispersion_v45_TOPJOURNAL/_ANALYSIS_v45_metrics/"
    "_GRID_INTERNAL_QREG_DYNAMICS_CORRIDOR/_BOUNDARY_LAYER_EVENT_DIAGNOSTICS"
)

REGIME_STATES = [
    "day",
    "night",
    "stable_like",
    "unstable_like",
    "shear_weak",
    "shear_moderate",
    "shear_extreme",
    "gust_high",
    "gust_extreme",
    "stable_shear_high",
    "gust_shear_compound",
]

EVENT_STATES = [
    "event_gust_lead",
    "event_gust_core",
    "event_gust_lag",
    "event_gust_leadlag",
    "event_shear_lead",
    "event_shear_core",
    "event_shear_lag",
    "event_shear_leadlag",
]

ALL_TARGET_STATES = REGIME_STATES + EVENT_STATES

EVENT_ROLE_ORDER = ["lead", "core", "lag", "leadlag"]


# =========================================================
# PLOT STYLE
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
        "legend.fontsize": 9.2,
        "legend.frameon": False,
        "figure.dpi": 130,
        "savefig.dpi": 350,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.05,
        "axes.grid": False,
        "lines.linewidth": 1.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
    })


# =========================================================
# BASIC UTILS
# =========================================================
def ensure_dirs(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def savefig(path: str, dpi: int = 350):
    plt.tight_layout()
    plt.savefig(path, dpi=dpi)
    plt.close()


def safe_div(a, b, fill=np.nan):
    a = float(a)
    b = float(b)
    if (not np.isfinite(a)) or (not np.isfinite(b)) or (abs(b) <= EPS):
        return float(fill)
    return float(a / b)


def month_iter(year0=2015, year1=2025):
    for y in range(year0, year1 + 1):
        for m in range(1, 13):
            yield y, m


def zip_nc_path(city_dir, city, y, m):
    return os.path.join(city_dir, f"ERA5_{city}_{y}{m:02d}_low_altitude_RLCC.zip")


def sem(x: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) <= 1:
        return np.nan
    return float(np.std(x, ddof=1) / np.sqrt(len(x)))


def mean_ci95(x: np.ndarray) -> Tuple[float, float]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if len(x) == 0:
        return np.nan, np.nan
    m = float(np.mean(x))
    s = sem(x)
    if not np.isfinite(s):
        return m, np.nan
    return m, float(1.96 * s)


def smooth_1d(x, win=7):
    x = np.asarray(x, dtype=float)
    if len(x) == 0:
        return x.copy()
    if win <= 1:
        return x.copy()

    if gaussian_filter1d is not None:
        sigma = max(0.5, float(win) / 3.0)
        xf = x.copy()
        m = np.isfinite(xf)
        if not np.any(m):
            return x.copy()
        fill = np.nanmedian(xf[m])
        xf[~m] = fill
        ys = gaussian_filter1d(xf, sigma=sigma, mode="nearest")
        ys[~m] = np.nan
        return ys

    out = np.full_like(x, np.nan, dtype=float)
    for i in range(len(x)):
        lo = max(0, i - win // 2)
        hi = min(len(x), i + win // 2 + 1)
        seg = x[lo:hi]
        seg = seg[np.isfinite(seg)]
        if len(seg) > 0:
            out[i] = float(np.mean(seg))
    return out


def rename_metric(metric: str) -> str:
    mp = {
        "vd_occ": "Vertical decoupling in occupancy",
        "vd_persistence": "Vertical decoupling in persistence",
        "vd_largest_frac": "Vertical decoupling in largest corridor fraction",
        "vd_pc": "Vertical decoupling in percolation threshold",
        "vd_anis": "Vertical decoupling in anisotropy",
        "blh_mean": "Boundary-layer height",
        "shear_mean": "Vertical shear (U100-U10)",
        "gust_mean": "10 m gust",
        "wind10_mean": "10 m mean wind speed",
        "wind100_mean": "100 m mean wind speed",
    }
    return mp.get(metric, metric)


# =========================================================
# XARRAY / ZIP READER
# =========================================================
def _import_xarray():
    try:
        import xarray as xr
        return xr
    except Exception as e:
        raise RuntimeError(
            "xarray is required. Install with:\n"
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
                ds = None
                last_err = e

        if ds is None:
            raise RuntimeError(f"Failed to open nc from zip. Last error: {last_err}")

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
    if tmp_path and os.path.exists(tmp_path):
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
        raise ValueError("Latitude/longitude not found")

    tname = None
    for cand in ["time", "valid_time"]:
        if cand in ds.coords:
            tname = cand
            break
    if tname is None:
        raise ValueError("Time coordinate not found")

    ds_vars = list(ds.data_vars.keys())

    if varspec.kind == "single":
        arr = None
        for cand in varspec.candidates:
            if cand in ds_vars:
                arr = ds[cand].values.astype(np.float32)
                break
        if arr is None:
            raise ValueError(f"Variable {var_key} not found. Candidates={varspec.candidates}")
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
            raise ValueError(f"Wind components missing for {var_key}")
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
# DYNAMICS MERGED TABLE LOADER + DIRECT VERTICAL DECOUPLING
# =========================================================
def load_dynamics_merged_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Dynamics merged CSV not found: {path}")

    df = pd.read_csv(path)
    df.columns = [str(c).strip() for c in df.columns]

    need = ["city", "var", "state_group"]
    for c in need:
        if c not in df.columns:
            raise ValueError(f"Required column missing in merged csv: {c}")

    if "resp" not in df.columns and "response" in df.columns:
        df = df.rename(columns={"response": "resp"})
    if "resp" not in df.columns:
        raise ValueError("Merged csv must contain 'resp' or 'response' column")

    numeric_cols = [
        "critical_band_occupancy",
        "corridor_persistence_index",
        "HIGH_largest_frac",
        "p_c_S",
        "HIGH_pca_anisotropy",
        "used_hours_frac",
        "used_months",
        "event_hours_total",
        "valid_points",
        "critical_band_occupancy_x",
        "critical_band_occupancy_y",
    ]
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


def build_direct_vertical_decoupling_from_merged(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build direct vertical decoupling from dynamics v2 merged summary:
      vd_occ         = occ_100 - occ_10
      vd_persistence = cpi_100 - cpi_10
      vd_largest_frac= largest_frac_100 - largest_frac_10
      vd_pc          = pc_100 - pc_10
      vd_anis        = anis_100 - anis_10
    """
    keep_cols = [
        "city", "state_group", "resp", "var",
        "critical_band_occupancy",
        "corridor_persistence_index",
        "HIGH_largest_frac",
        "p_c_S",
        "HIGH_pca_anisotropy",
        "cluster",
        "city_entropy",
        "used_hours_frac",
        "used_months",
        "event_hours_total",
        "valid_points",
    ]
    keep_cols = [c for c in keep_cols if c in df.columns]

    d = df[keep_cols].copy()

    wide = d.pivot_table(
        index=["city", "state_group", "resp"],
        columns="var",
        values=[c for c in [
            "critical_band_occupancy",
            "corridor_persistence_index",
            "HIGH_largest_frac",
            "p_c_S",
            "HIGH_pca_anisotropy",
            "used_hours_frac",
            "used_months",
            "event_hours_total",
            "valid_points",
            "cluster",
            "city_entropy",
        ] if c in d.columns],
        aggfunc="first"
    )

    wide.columns = [f"{m}__{v}" for (m, v) in wide.columns]
    wide = wide.reset_index()

    out = wide.copy()

    def diff_if_exists(base: str, newc: str):
        c10 = f"{base}__wind10"
        c100 = f"{base}__wind100"
        if c10 in out.columns and c100 in out.columns:
            out[newc] = out[c100] - out[c10]
        else:
            out[newc] = np.nan

    diff_if_exists("critical_band_occupancy", "vd_occ")
    diff_if_exists("corridor_persistence_index", "vd_persistence")
    diff_if_exists("HIGH_largest_frac", "vd_largest_frac")
    diff_if_exists("p_c_S", "vd_pc")
    diff_if_exists("HIGH_pca_anisotropy", "vd_anis")

    # carry city-level meta
    meta_cols_pref = [
        "cluster__wind10", "cluster__wind100",
        "city_entropy__wind10", "city_entropy__wind100"
    ]
    if "cluster__wind10" in out.columns:
        out["cluster"] = out["cluster__wind10"]
    elif "cluster__wind100" in out.columns:
        out["cluster"] = out["cluster__wind100"]
    else:
        out["cluster"] = np.nan

    if "city_entropy__wind10" in out.columns:
        out["city_entropy"] = out["city_entropy__wind10"]
    elif "city_entropy__wind100" in out.columns:
        out["city_entropy"] = out["city_entropy__wind100"]
    else:
        out["city_entropy"] = np.nan

    # average state meta across heights if both exist
    for base in ["used_hours_frac", "used_months", "event_hours_total", "valid_points"]:
        c10 = f"{base}__wind10"
        c100 = f"{base}__wind100"
        if c10 in out.columns and c100 in out.columns:
            out[base] = np.nanmean(np.column_stack([out[c10], out[c100]]), axis=1)
        elif c10 in out.columns:
            out[base] = out[c10]
        elif c100 in out.columns:
            out[base] = out[c100]
        else:
            out[base] = np.nan

    out = out.rename(columns={"resp": "response"})
    out["city"] = out["city"].astype(str)
    out["state_group"] = out["state_group"].astype(str)
    out["response"] = out["response"].astype(str)

    return out


# =========================================================
# CITY DISCOVERY
# =========================================================
def find_all_cities_on_disk(era5_root: str, year0: int, year1: int) -> List[str]:
    exclude_prefixes = ("_", "GLOBAL", "Global", "processed", "Z_")
    out = []
    for d in sorted(glob.glob(os.path.join(era5_root, "*"))):
        if not os.path.isdir(d):
            continue
        city = os.path.basename(d)
        if city.startswith(exclude_prefixes):
            continue

        found_zip = False
        for y in range(year0, year1 + 1):
            for m in range(1, 13):
                zp = os.path.join(d, f"ERA5_{city}_{y}{m:02d}_low_altitude_RLCC.zip")
                if os.path.exists(zp):
                    found_zip = True
                    break
            if found_zip:
                break
        if found_zip:
            out.append(city)
    return out


# =========================================================
# HOURLY RAW METEOROLOGY
# =========================================================
def compute_city_hourly_mean_timeseries(
    era5_root: str,
    city: str,
    year0: int,
    year1: int,
) -> pd.DataFrame:
    city_dir = os.path.join(era5_root, city)
    var_specs = build_var_specs()

    rows = []
    for y, m in month_iter(year0, year1):
        zp = zip_nc_path(city_dir, city, y, m)
        if not os.path.exists(zp):
            continue

        ds, _ = open_zip_dataset(zp)
        if ds is None:
            continue

        try:
            arr_w10, _, _, hours, times = extract_value_array(ds, "wind10", var_specs["wind10"])
            arr_w100, _, _, _, _ = extract_value_array(ds, "wind100", var_specs["wind100"])
            arr_blh, _, _, _, _ = extract_value_array(ds, "blh", var_specs["blh"])
            try:
                arr_gust, _, _, _, _ = extract_value_array(ds, "gust", var_specs["gust"])
            except ValueError as e:
                if "Variable gust not found" not in str(e):
                    raise
                print(
                    f"[WARN] Missing gust variable for {city} {y}{m:02d}; "
                    "filling gust_mean with NaN for this month.",
                    flush=True,
                )
                arr_gust = np.full(arr_w10.shape, np.nan, dtype=np.float32)

            dfm = pd.DataFrame({
                "time": pd.to_datetime(times),
                "city": city,
                "year": int(y),
                "month": int(m),
                "hour": hours.astype(int),
                "wind10_mean": np.nanmean(arr_w10, axis=(1, 2)).astype(float),
                "wind100_mean": np.nanmean(arr_w100, axis=(1, 2)).astype(float),
                "blh_mean": np.nanmean(arr_blh, axis=(1, 2)).astype(float),
                "gust_mean": np.nanmean(arr_gust, axis=(1, 2)).astype(float),
            })
            dfm["shear_mean"] = dfm["wind100_mean"] - dfm["wind10_mean"]
            rows.append(dfm)

        finally:
            close_dataset_and_cleanup(ds)

    if len(rows) == 0:
        return pd.DataFrame(columns=[
            "time", "city", "year", "month", "hour",
            "wind10_mean", "wind100_mean", "blh_mean", "gust_mean", "shear_mean"
        ])

    out = pd.concat(rows, ignore_index=True).sort_values("time").reset_index(drop=True)
    return out


# =========================================================
# STATE DEFINITIONS (CONSISTENT WITH DYNAMICS V2, BUT ON CITY-MEAN HOURLY SERIES)
# =========================================================
def is_day_hour(hour_arr: np.ndarray, day_hour_start: int = 8, day_hour_end: int = 18) -> np.ndarray:
    h = np.asarray(hour_arr).astype(int)
    return (h >= int(day_hour_start)) & (h < int(day_hour_end))


def _monthly_quantile_mask(x: np.ndarray, q: float, side: str) -> np.ndarray:
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


def _detect_event_core_mask(x: np.ndarray, q_extreme: float, min_gap_hours: int = 6) -> np.ndarray:
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


def compute_state_mask_month_citymean(
    state_group: str,
    hour_arr: np.ndarray,
    blh: np.ndarray,
    gust: np.ndarray,
    shear: np.ndarray,
    day_hour_start: int = 8,
    day_hour_end: int = 18,
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
    day_mask = is_day_hour(hour_arr, day_hour_start=day_hour_start, day_hour_end=day_hour_end)
    night_mask = ~day_mask

    if state_group == "day":
        return day_mask
    if state_group == "night":
        return night_mask
    if state_group == "stable_like":
        return night_mask & _monthly_quantile_mask(blh, blh_low_q, side="low")
    if state_group == "unstable_like":
        return day_mask & _monthly_quantile_mask(blh, blh_high_q, side="high")

    if state_group in ["shear_weak", "shear_moderate", "shear_extreme"]:
        weak, moderate, extreme = _monthly_three_way_mask(shear, qlo=shear_low_q, qhi=shear_extreme_q)
        if state_group == "shear_weak":
            return weak
        if state_group == "shear_moderate":
            return moderate
        return extreme

    if state_group == "gust_high":
        return _monthly_quantile_mask(gust, gust_high_q, side="high")
    if state_group == "gust_extreme":
        return _monthly_quantile_mask(gust, gust_extreme_q, side="high")

    if state_group == "stable_shear_high":
        stable = night_mask & _monthly_quantile_mask(blh, blh_low_q, side="low")
        shigh = _monthly_quantile_mask(shear, shear_high_q, side="high")
        return stable & shigh

    if state_group == "gust_shear_compound":
        gext = _monthly_quantile_mask(gust, gust_extreme_q, side="high")
        sext = _monthly_quantile_mask(shear, shear_extreme_q, side="high")
        return gext & sext

    if state_group in [
        "event_gust_lead", "event_gust_core", "event_gust_lag", "event_gust_leadlag"
    ]:
        ev = _derive_event_masks(
            x=gust,
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

    if state_group in [
        "event_shear_lead", "event_shear_core", "event_shear_lag", "event_shear_leadlag"
    ]:
        ev = _derive_event_masks(
            x=shear,
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

    return np.zeros_like(hour_arr, dtype=bool)


def summarize_state_level_meteorology_all_states(
    df_hourly_all: pd.DataFrame,
    target_states: List[str],
    day_hour_start: int = 8,
    day_hour_end: int = 18,
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
) -> pd.DataFrame:
    rows = []
    if df_hourly_all is None or len(df_hourly_all) == 0:
        return pd.DataFrame()

    for city, sub_city in df_hourly_all.groupby("city"):
        sub_city = sub_city.sort_values("time").reset_index(drop=True)

        for (yy, mm), sub_m in sub_city.groupby(["year", "month"]):
            sub_m = sub_m.sort_values("time").reset_index(drop=True)

            hour_arr = sub_m["hour"].values.astype(int)
            blh = sub_m["blh_mean"].values.astype(float)
            gust = sub_m["gust_mean"].values.astype(float)
            shear = sub_m["shear_mean"].values.astype(float)
            w10 = sub_m["wind10_mean"].values.astype(float)
            w100 = sub_m["wind100_mean"].values.astype(float)

            for state_group in target_states:
                mask = compute_state_mask_month_citymean(
                    state_group=state_group,
                    hour_arr=hour_arr,
                    blh=blh,
                    gust=gust,
                    shear=shear,
                    day_hour_start=day_hour_start,
                    day_hour_end=day_hour_end,
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
                if np.sum(mask) == 0:
                    continue

                rows.append({
                    "city": city,
                    "year": int(yy),
                    "month": int(mm),
                    "state_group": state_group,
                    "n_hours": int(np.sum(mask)),
                    "blh_mean": float(np.nanmean(blh[mask])),
                    "gust_mean": float(np.nanmean(gust[mask])),
                    "shear_mean": float(np.nanmean(shear[mask])),
                    "wind10_mean": float(np.nanmean(w10[mask])),
                    "wind100_mean": float(np.nanmean(w100[mask])),
                })

    if len(rows) == 0:
        return pd.DataFrame()

    dm = pd.DataFrame(rows)

    # aggregate to city-state mean
    out_rows = []
    for (city, state_group), ss in dm.groupby(["city", "state_group"]):
        out_rows.append({
            "city": city,
            "state_group": state_group,
            "n_months_with_state": int(len(ss)),
            "n_hours": int(np.sum(ss["n_hours"].values)),
            "blh_mean": float(np.nanmean(ss["blh_mean"].values)),
            "gust_mean": float(np.nanmean(ss["gust_mean"].values)),
            "shear_mean": float(np.nanmean(ss["shear_mean"].values)),
            "wind10_mean": float(np.nanmean(ss["wind10_mean"].values)),
            "wind100_mean": float(np.nanmean(ss["wind100_mean"].values)),
        })
    return pd.DataFrame(out_rows)


# =========================================================
# MERGE DIRECT VD WITH CONTINUOUS DRIVERS
# =========================================================
def build_vd_continuous_controls(
    df_vd: pd.DataFrame,
    df_state_met: pd.DataFrame
) -> pd.DataFrame:
    if df_vd is None or len(df_vd) == 0:
        return pd.DataFrame()
    if df_state_met is None or len(df_state_met) == 0:
        return pd.DataFrame()

    d = df_vd.merge(
        df_state_met,
        on=["city", "state_group"],
        how="left"
    )

    d["vd_quadrant"] = np.where(
        ~np.isfinite(d["vd_occ"]) | ~np.isfinite(d["vd_persistence"]),
        "NA",
        np.where(
            (d["vd_occ"] >= 0) & (d["vd_persistence"] >= 0), "Q1_100m_occ_100m_persist",
            np.where(
                (d["vd_occ"] < 0) & (d["vd_persistence"] >= 0), "Q2_10m_occ_100m_persist",
                np.where(
                    (d["vd_occ"] < 0) & (d["vd_persistence"] < 0), "Q3_10m_occ_10m_persist",
                    "Q4_100m_occ_10m_persist"
                )
            )
        )
    )

    d["state_class"] = np.where(d["state_group"].isin(EVENT_STATES), "event", "regime")
    return d


# =========================================================
# CONTINUOUS CONTROL FITS
# =========================================================
def simple_linear_fit(x: np.ndarray, y: np.ndarray) -> Dict[str, float]:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]
    y = y[m]

    out = {
        "n": int(len(x)),
        "slope": np.nan,
        "intercept": np.nan,
        "r2": np.nan,
        "spearman_r": np.nan,
        "spearman_p": np.nan,
    }
    if len(x) < 4:
        return out

    if LinearRegression is not None:
        X = x.reshape(-1, 1)
        mdl = LinearRegression()
        mdl.fit(X, y)
        pred = mdl.predict(X)
        out["slope"] = float(mdl.coef_[0])
        out["intercept"] = float(mdl.intercept_)
        if r2_score is not None:
            out["r2"] = float(r2_score(y, pred))

    if spearmanr is not None:
        try:
            sr = spearmanr(x, y, nan_policy="omit")
            out["spearman_r"] = float(sr.correlation)
            out["spearman_p"] = float(sr.pvalue)
        except Exception:
            pass

    return out


def nonlinear_spline_fit(
    x: np.ndarray,
    y: np.ndarray,
    n_knots: int = 4,
    degree: int = 3,
    alpha: float = 1.0
) -> Dict[str, object]:
    out = {
        "n": 0,
        "r2": np.nan,
        "x_grid": np.array([]),
        "y_hat_grid": np.array([]),
        "model_ok": False,
    }

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    m = np.isfinite(x) & np.isfinite(y)
    x = x[m]
    y = y[m]
    out["n"] = int(len(x))

    if len(x) < 10 or (not _HAS_SKLEARN):
        return out

    try:
        X = x.reshape(-1, 1)
        model = make_pipeline(
            SplineTransformer(n_knots=int(n_knots), degree=int(degree), include_bias=False),
            Ridge(alpha=float(alpha))
        )
        model.fit(X, y)
        pred = model.predict(X)
        r2 = float(r2_score(y, pred)) if r2_score is not None else np.nan

        xg = np.linspace(np.nanmin(x), np.nanmax(x), 200).reshape(-1, 1)
        yg = model.predict(xg)

        out["r2"] = r2
        out["x_grid"] = xg.ravel()
        out["y_hat_grid"] = yg.ravel()
        out["model_ok"] = True
        return out
    except Exception:
        return out


def fit_continuous_controls(df_cont: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if df_cont is None or len(df_cont) == 0:
        return pd.DataFrame()

    # continuous control analysis only on regime states
    sub0 = df_cont[df_cont["state_class"] == "regime"].copy()
    if len(sub0) == 0:
        return pd.DataFrame()

    for response in sorted(sub0["response"].dropna().unique()):
        sub = sub0[sub0["response"] == response].copy()

        for ycol in ["vd_occ", "vd_persistence", "vd_largest_frac", "vd_pc", "vd_anis"]:
            if ycol not in sub.columns:
                continue
            for xcol in ["blh_mean", "shear_mean", "gust_mean", "wind10_mean", "wind100_mean"]:
                if xcol not in sub.columns:
                    continue

                fit_lin = simple_linear_fit(sub[xcol].values, sub[ycol].values)
                fit_nl = nonlinear_spline_fit(sub[xcol].values, sub[ycol].values)

                rows.append({
                    "response": response,
                    "state_class": "regime",
                    "y_metric": ycol,
                    "x_driver": xcol,
                    "n": fit_lin["n"],
                    "linear_slope": fit_lin["slope"],
                    "linear_intercept": fit_lin["intercept"],
                    "linear_r2": fit_lin["r2"],
                    "spearman_r": fit_lin["spearman_r"],
                    "spearman_p": fit_lin["spearman_p"],
                    "spline_r2": fit_nl["r2"],
                    "nonlinear_gain_r2": (
                        float(fit_nl["r2"] - fit_lin["r2"])
                        if np.isfinite(fit_nl["r2"]) and np.isfinite(fit_lin["r2"])
                        else np.nan
                    ),
                    "spline_model_ok": int(bool(fit_nl["model_ok"])),
                })
    return pd.DataFrame(rows)


def build_2d_response_surface(
    df: pd.DataFrame,
    response: str,
    ycol: str,
    x1: str = "blh_mean",
    x2: str = "shear_mean",
    bins1: int = 10,
    bins2: int = 10,
) -> Tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    sub = df[(df["state_class"] == "regime") & (df["response"] == response)].copy()
    sub = sub[np.isfinite(sub[x1]) & np.isfinite(sub[x2]) & np.isfinite(sub[ycol])].copy()
    if len(sub) == 0:
        return pd.DataFrame(), np.array([]), np.array([]), np.array([[]])

    x = sub[x1].values.astype(float)
    y = sub[x2].values.astype(float)
    z = sub[ycol].values.astype(float)

    x_edges = np.quantile(x, np.linspace(0, 1, int(bins1) + 1))
    y_edges = np.quantile(y, np.linspace(0, 1, int(bins2) + 1))

    x_edges = np.unique(x_edges)
    y_edges = np.unique(y_edges)
    if len(x_edges) < 3 or len(y_edges) < 3:
        return pd.DataFrame(), np.array([]), np.array([]), np.array([[]])

    rows = []
    mat = np.full((len(y_edges) - 1, len(x_edges) - 1), np.nan, dtype=float)

    for i in range(len(x_edges) - 1):
        for j in range(len(y_edges) - 1):
            if i < len(x_edges) - 2:
                mx = (x >= x_edges[i]) & (x < x_edges[i + 1])
            else:
                mx = (x >= x_edges[i]) & (x <= x_edges[i + 1])

            if j < len(y_edges) - 2:
                my = (y >= y_edges[j]) & (y < y_edges[j + 1])
            else:
                my = (y >= y_edges[j]) & (y <= y_edges[j + 1])

            mm = mx & my
            if np.sum(mm) == 0:
                continue

            val = float(np.nanmean(z[mm]))
            mat[j, i] = val
            rows.append({
                "response": response,
                "y_metric": ycol,
                "x1_driver": x1,
                "x2_driver": x2,
                "x1_lo": float(x_edges[i]),
                "x1_hi": float(x_edges[i + 1]),
                "x2_lo": float(y_edges[j]),
                "x2_hi": float(y_edges[j + 1]),
                "n": int(np.sum(mm)),
                "mean_response": val,
            })

    return pd.DataFrame(rows), x_edges, y_edges, mat


# =========================================================
# EVENT DIRECT SUMMARY FROM REAL EVENT STATES
# =========================================================
def build_direct_event_state_summary(df_cont: pd.DataFrame) -> pd.DataFrame:
    if df_cont is None or len(df_cont) == 0:
        return pd.DataFrame()

    sub = df_cont[df_cont["state_group"].isin(EVENT_STATES)].copy()
    if len(sub) == 0:
        return pd.DataFrame()

    rows = []
    for event_type in ["gust", "shear"]:
        prefix = f"event_{event_type}_"
        ss0 = sub[sub["state_group"].str.startswith(prefix)].copy()
        if len(ss0) == 0:
            continue

        ss0["window_role"] = ss0["state_group"].str.replace(prefix, "", regex=False)
        for response in sorted(ss0["response"].dropna().unique()):
            for role in EVENT_ROLE_ORDER:
                ss = ss0[(ss0["response"] == response) & (ss0["window_role"] == role)].copy()
                if len(ss) == 0:
                    continue
                rows.append({
                    "event_type": event_type,
                    "response": response,
                    "window_role": role,
                    "n_rows": int(len(ss)),
                    "n_cities": int(ss["city"].nunique()),
                    "vd_occ_mean": float(np.nanmean(ss["vd_occ"].values)),
                    "vd_occ_ci95": float(1.96 * sem(ss["vd_occ"].values)) if np.sum(np.isfinite(ss["vd_occ"].values)) > 1 else np.nan,
                    "vd_persistence_mean": float(np.nanmean(ss["vd_persistence"].values)),
                    "vd_persistence_ci95": float(1.96 * sem(ss["vd_persistence"].values)) if np.sum(np.isfinite(ss["vd_persistence"].values)) > 1 else np.nan,
                    "vd_largest_frac_mean": float(np.nanmean(ss["vd_largest_frac"].values)),
                    "vd_pc_mean": float(np.nanmean(ss["vd_pc"].values)),
                    "vd_anis_mean": float(np.nanmean(ss["vd_anis"].values)),
                    "blh_mean": float(np.nanmean(ss["blh_mean"].values)),
                    "gust_mean": float(np.nanmean(ss["gust_mean"].values)),
                    "shear_mean": float(np.nanmean(ss["shear_mean"].values)),
                    "wind10_mean": float(np.nanmean(ss["wind10_mean"].values)),
                    "wind100_mean": float(np.nanmean(ss["wind100_mean"].values)),
                })
    return pd.DataFrame(rows)


def build_event_city_table(df_cont: pd.DataFrame) -> pd.DataFrame:
    if df_cont is None or len(df_cont) == 0:
        return pd.DataFrame()

    sub = df_cont[df_cont["state_group"].isin(EVENT_STATES)].copy()
    if len(sub) == 0:
        return pd.DataFrame()

    sub["event_type"] = np.where(sub["state_group"].str.contains("gust"), "gust", "shear")
    sub["window_role"] = np.where(
        sub["state_group"].str.endswith("_lead"), "lead",
        np.where(
            sub["state_group"].str.endswith("_core"), "core",
            np.where(
                sub["state_group"].str.endswith("_lag"), "lag",
                "leadlag"
            )
        )
    )
    return sub.reset_index(drop=True)


# =========================================================
# HOURLY EVENT PHASE TRAJECTORIES FROM RAW ERA5
# =========================================================
def find_event_episodes(mask: np.ndarray, min_len: int = 1) -> List[Tuple[int, int]]:
    m = np.asarray(mask).astype(bool)
    episodes = []
    n = len(m)
    i = 0
    while i < n:
        if not m[i]:
            i += 1
            continue
        j = i
        while j + 1 < n and m[j + 1]:
            j += 1
        if (j - i + 1) >= int(min_len):
            episodes.append((i, j))
        i = j + 1
    return episodes


def build_event_phase_trajectory_hourly(
    df_hourly_all: pd.DataFrame,
    target_col: str,
    event_q: float = 0.95,
    phase_hours: int = 12,
    min_event_len: int = 1,
) -> pd.DataFrame:
    rows = []
    if df_hourly_all is None or len(df_hourly_all) == 0:
        return pd.DataFrame()

    for city, sub in df_hourly_all.groupby("city"):
        sub = sub.sort_values("time").reset_index(drop=True)
        x = sub[target_col].values.astype(float)
        mf = np.isfinite(x)
        if np.sum(mf) < 100:
            continue

        thr = float(np.nanquantile(x[mf], float(event_q)))
        core_mask = np.isfinite(x) & (x >= thr)
        episodes = find_event_episodes(core_mask, min_len=min_event_len)
        if len(episodes) == 0:
            continue

        for eid, (s, e) in enumerate(episodes, start=1):
            center = int(np.floor((s + e) / 2.0))
            lo = max(0, center - int(phase_hours))
            hi = min(len(sub) - 1, center + int(phase_hours))

            for ii in range(lo, hi + 1):
                rr = sub.iloc[ii]
                rows.append({
                    "city": city,
                    "event_type": target_col.replace("_mean", ""),
                    "event_id": f"{city}_{target_col}_{eid}",
                    "relative_hour": int(ii - center),
                    "is_core": int((ii >= s) and (ii <= e)),
                    "time": rr["time"],
                    "blh_mean": float(rr["blh_mean"]),
                    "gust_mean": float(rr["gust_mean"]),
                    "shear_mean": float(rr["shear_mean"]),
                    "wind10_mean": float(rr["wind10_mean"]),
                    "wind100_mean": float(rr["wind100_mean"]),
                    "deltaU_mean": float(rr["wind100_mean"] - rr["wind10_mean"]),
                })

    if len(rows) == 0:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def summarize_event_phase_trajectory(df_phase: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if df_phase is None or len(df_phase) == 0:
        return pd.DataFrame()

    for (event_type, relative_hour), sub in df_phase.groupby(["event_type", "relative_hour"]):
        rows.append({
            "event_type": event_type,
            "relative_hour": int(relative_hour),
            "n_records": int(len(sub)),
            "n_events": int(sub["event_id"].nunique()),
            "blh_mean": float(np.nanmean(sub["blh_mean"].values)),
            "blh_se": float(sem(sub["blh_mean"].values)),
            "gust_mean": float(np.nanmean(sub["gust_mean"].values)),
            "gust_se": float(sem(sub["gust_mean"].values)),
            "shear_mean": float(np.nanmean(sub["shear_mean"].values)),
            "shear_se": float(sem(sub["shear_mean"].values)),
            "wind10_mean": float(np.nanmean(sub["wind10_mean"].values)),
            "wind100_mean": float(np.nanmean(sub["wind100_mean"].values)),
            "deltaU_mean": float(np.nanmean(sub["deltaU_mean"].values)),
        })

    return pd.DataFrame(rows).sort_values(["event_type", "relative_hour"]).reset_index(drop=True)


# =========================================================
# FIGURES
# =========================================================
def plot_driver_vs_vd_scatter(
    df: pd.DataFrame,
    response: str,
    xcol: str,
    ycol: str,
    outpath: str,
    color_col: Optional[str] = None,
):
    sub = df[(df["state_class"] == "regime") & (df["response"] == response)].copy()
    sub = sub[np.isfinite(sub[xcol]) & np.isfinite(sub[ycol])].copy()
    if len(sub) == 0:
        return

    x = sub[xcol].values.astype(float)
    y = sub[ycol].values.astype(float)

    ord_idx = np.argsort(x)
    xs = x[ord_idx]
    ys = y[ord_idx]
    ys_s = smooth_1d(ys, win=max(3, min(9, len(ys) // 2 if len(ys) >= 6 else 3)))

    plt.figure(figsize=(7.2, 5.8))
    if color_col is not None and color_col in sub.columns:
        sc = plt.scatter(
            sub[xcol].values,
            sub[ycol].values,
            c=sub[color_col].values,
            s=76,
            edgecolor="k",
            linewidths=0.6,
            alpha=0.92,
        )
        cb = plt.colorbar(sc)
        cb.set_label(rename_metric(color_col))
    else:
        plt.scatter(
            sub[xcol].values,
            sub[ycol].values,
            s=76,
            edgecolor="k",
            linewidths=0.6,
            alpha=0.92,
        )

    plt.plot(xs, ys_s, linewidth=2.1)
    plt.axhline(0.0, linestyle="--", linewidth=1.0)
    plt.xlabel(rename_metric(xcol))
    plt.ylabel(rename_metric(ycol))
    plt.title(f"{response.upper()} | {rename_metric(xcol)} control on {rename_metric(ycol).lower()}")
    savefig(outpath)


def plot_quadrant_with_driver(df: pd.DataFrame, response: str, driver: str, outpath: str):
    sub = df[(df["state_class"] == "regime") & (df["response"] == response)].copy()
    sub = sub[np.isfinite(sub["vd_occ"]) & np.isfinite(sub["vd_persistence"])].copy()
    if len(sub) == 0:
        return

    plt.figure(figsize=(7.0, 6.3))
    if driver in sub.columns:
        sc = plt.scatter(
            sub["vd_occ"].values,
            sub["vd_persistence"].values,
            c=sub[driver].values,
            s=92,
            edgecolor="k",
            linewidths=0.6,
            alpha=0.93
        )
        cb = plt.colorbar(sc)
        cb.set_label(rename_metric(driver))
    else:
        plt.scatter(
            sub["vd_occ"].values,
            sub["vd_persistence"].values,
            s=92,
            edgecolor="k",
            linewidths=0.6,
            alpha=0.93
        )

    for _, r in sub.iterrows():
        try:
            plt.text(float(r["vd_occ"]), float(r["vd_persistence"]), str(r["city"]), fontsize=8.0)
        except Exception:
            pass

    plt.axhline(0.0, linestyle="--", linewidth=1.0)
    plt.axvline(0.0, linestyle="--", linewidth=1.0)
    plt.xlabel(rename_metric("vd_occ"))
    plt.ylabel(rename_metric("vd_persistence"))
    plt.title(f"{response.upper()} | Mechanism quadrants colored by {rename_metric(driver).lower()}")
    savefig(outpath)


def plot_nonlinear_spline_fit(
    df: pd.DataFrame,
    response: str,
    ycol: str,
    xcol: str,
    outpath: str
):
    sub = df[(df["state_class"] == "regime") & (df["response"] == response)].copy()
    sub = sub[np.isfinite(sub[xcol]) & np.isfinite(sub[ycol])].copy()
    if len(sub) < 10:
        return

    x = sub[xcol].values.astype(float)
    y = sub[ycol].values.astype(float)

    fit_nl = nonlinear_spline_fit(x, y)
    fit_lin = simple_linear_fit(x, y)

    plt.figure(figsize=(7.4, 5.8))
    plt.scatter(x, y, s=60, edgecolor="k", linewidths=0.55, alpha=0.82)

    ord_idx = np.argsort(x)
    xs = x[ord_idx]
    if fit_nl["model_ok"]:
        plt.plot(
            fit_nl["x_grid"],
            fit_nl["y_hat_grid"],
            linewidth=2.3,
            label=f"Spline fit (R2={fit_nl['r2']:.3f})"
        )

    if np.isfinite(fit_lin["slope"]) and np.isfinite(fit_lin["intercept"]):
        yl = fit_lin["intercept"] + fit_lin["slope"] * xs
        plt.plot(xs, yl, linewidth=1.4, linestyle="--", label=f"Linear fit (R2={fit_lin['r2']:.3f})")

    plt.axhline(0.0, linestyle="--", linewidth=1.0)
    plt.xlabel(rename_metric(xcol))
    plt.ylabel(rename_metric(ycol))
    plt.title(f"{response.upper()} | Nonlinear control: {rename_metric(xcol)} → {rename_metric(ycol)}")
    plt.legend()
    savefig(outpath)


def plot_2d_response_surface(
    x_edges: np.ndarray,
    y_edges: np.ndarray,
    mat: np.ndarray,
    response: str,
    y_metric: str,
    outpath: str
):
    if mat is None or mat.size == 0:
        return

    plt.figure(figsize=(7.4, 6.1))
    extent = [x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]]
    plt.imshow(mat, origin="lower", aspect="auto", extent=extent)
    cb = plt.colorbar()
    cb.set_label(f"Mean {rename_metric(y_metric)}")
    plt.xlabel(rename_metric("blh_mean"))
    plt.ylabel(rename_metric("shear_mean"))
    plt.title(f"{response.upper()} | 2D response surface of {rename_metric(y_metric).lower()}")
    savefig(outpath)


def plot_state_heatmap(df_cont: pd.DataFrame, response: str, metric: str, outpath: str):
    sub = df_cont[df_cont["response"] == response].copy()
    if len(sub) == 0 or metric not in sub.columns:
        return

    state_order = [s for s in ALL_TARGET_STATES if s in set(sub["state_group"].astype(str))]
    city_order = sorted(sub["city"].dropna().astype(str).unique().tolist())

    hm = sub.pivot_table(index="city", columns="state_group", values=metric, aggfunc="first")
    hm = hm.reindex(index=city_order, columns=state_order)
    if hm.shape[0] == 0 or hm.shape[1] == 0:
        return

    plt.figure(figsize=(max(8.0, 0.45 * hm.shape[1] + 3), max(5.5, 0.35 * hm.shape[0] + 2)))
    plt.imshow(hm.values.astype(float), aspect="auto")
    cb = plt.colorbar()
    cb.set_label(rename_metric(metric))
    plt.xticks(np.arange(hm.shape[1]), hm.columns.tolist(), rotation=40, ha="right")
    plt.yticks(np.arange(hm.shape[0]), hm.index.tolist())
    plt.xlabel("State group")
    plt.ylabel("City")
    plt.title(f"{response.upper()} | City-state heatmap of {rename_metric(metric).lower()}")
    savefig(outpath)


def plot_event_window_bars(df_event_summary: pd.DataFrame, event_type: str, response: str, outpath: str):
    sub = df_event_summary[
        (df_event_summary["event_type"] == event_type) &
        (df_event_summary["response"] == response)
    ].copy()
    if len(sub) == 0:
        return

    sub["window_role"] = pd.Categorical(sub["window_role"], categories=EVENT_ROLE_ORDER, ordered=True)
    sub = sub.sort_values("window_role").reset_index(drop=True)

    x = np.arange(len(sub))
    width = 0.34

    plt.figure(figsize=(8.4, 5.8))
    plt.bar(
        x - width / 2,
        sub["vd_occ_mean"].values,
        width=width,
        yerr=sub["vd_occ_ci95"].values,
        capsize=4,
        label="Occupancy decoupling"
    )
    plt.bar(
        x + width / 2,
        sub["vd_persistence_mean"].values,
        width=width,
        yerr=sub["vd_persistence_ci95"].values,
        capsize=4,
        label="Persistence decoupling"
    )
    plt.axhline(0.0, linestyle="--", linewidth=1.0)
    plt.xticks(x, sub["window_role"].astype(str).tolist())
    plt.xlabel("Event window role")
    plt.ylabel("Direct vertical decoupling")
    plt.title(f"{response.upper()} | Lead-core-lag direct decoupling during {event_type} extremes")
    plt.legend()
    savefig(outpath)


def plot_event_driver_evolution(df_event_summary: pd.DataFrame, event_type: str, response: str, outpath: str):
    sub = df_event_summary[
        (df_event_summary["event_type"] == event_type) &
        (df_event_summary["response"] == response)
    ].copy()
    if len(sub) == 0:
        return

    sub["window_role"] = pd.Categorical(sub["window_role"], categories=EVENT_ROLE_ORDER, ordered=True)
    sub = sub.sort_values("window_role").reset_index(drop=True)

    x = np.arange(len(sub))

    fig = plt.figure(figsize=(9.0, 5.8))
    ax1 = plt.gca()
    ax1.plot(x, sub["blh_mean"].values, marker="o", linewidth=1.8, label="BLH")
    ax1.plot(x, sub["shear_mean"].values, marker="s", linewidth=1.8, label="Shear")
    ax1.set_xticks(x)
    ax1.set_xticklabels(sub["window_role"].astype(str).tolist())
    ax1.set_xlabel("Event window role")
    ax1.set_ylabel("BLH / Shear")
    ax1.grid(alpha=0.25)

    ax2 = ax1.twinx()
    ax2.plot(x, sub["gust_mean"].values, marker="^", linewidth=1.8, label="Gust")
    ax2.set_ylabel("Gust")

    l1, lab1 = ax1.get_legend_handles_labels()
    l2, lab2 = ax2.get_legend_handles_labels()
    ax1.legend(l1 + l2, lab1 + lab2, loc="best")

    plt.title(f"{response.upper()} | Boundary-layer driver evolution during {event_type} extremes")
    savefig(outpath)


def plot_event_phase_trajectory(df_phase_summary: pd.DataFrame, event_type: str, outpath: str):
    sub = df_phase_summary[df_phase_summary["event_type"] == event_type].copy()
    if len(sub) == 0:
        return

    x = sub["relative_hour"].values.astype(int)

    fig = plt.figure(figsize=(10.0, 7.1))
    ax1 = plt.subplot(2, 1, 1)
    ax1.plot(x, sub["blh_mean"].values, marker="o", linewidth=1.7, label="BLH")
    ax1.plot(x, sub["shear_mean"].values, marker="s", linewidth=1.7, label="Shear")
    ax1.plot(x, sub["gust_mean"].values, marker="^", linewidth=1.7, label="Gust")
    ax1.axvline(0, linestyle="--", linewidth=1.0)
    ax1.set_xlabel("Relative hour from event center")
    ax1.set_ylabel("Driver magnitude")
    ax1.set_title(f"{event_type} event phase trajectory: boundary-layer drivers")
    ax1.legend()
    ax1.grid(alpha=0.25)

    ax2 = plt.subplot(2, 1, 2)
    ax2.plot(x, sub["wind10_mean"].values, marker="o", linewidth=1.7, label="10 m wind")
    ax2.plot(x, sub["wind100_mean"].values, marker="s", linewidth=1.7, label="100 m wind")
    ax2.plot(x, sub["deltaU_mean"].values, marker="^", linewidth=1.7, label="U100-U10")
    ax2.axvline(0, linestyle="--", linewidth=1.0)
    ax2.set_xlabel("Relative hour from event center")
    ax2.set_ylabel("Wind diagnostics")
    ax2.set_title(f"{event_type} event phase trajectory: layer wind evolution")
    ax2.legend()
    ax2.grid(alpha=0.25)

    savefig(outpath)


# =========================================================
# DISCOVERY SUMMARY
# =========================================================
def build_discovery_summary(
    df_fit: pd.DataFrame,
    df_event_direct: pd.DataFrame,
    df_phase_sum: pd.DataFrame
) -> pd.DataFrame:
    rows = []

    if df_fit is not None and len(df_fit) > 0:
        for _, r in df_fit.iterrows():
            rows.append({
                "module": "continuous_control",
                "response": r.get("response", ""),
                "target_metric": r.get("y_metric", ""),
                "driver": r.get("x_driver", ""),
                "n": r.get("n", np.nan),
                "effect_1": r.get("linear_slope", np.nan),
                "effect_2": r.get("linear_r2", np.nan),
                "effect_3": r.get("spline_r2", np.nan),
                "effect_4": r.get("nonlinear_gain_r2", np.nan),
                "effect_5": r.get("spearman_r", np.nan),
                "effect_6": r.get("spearman_p", np.nan),
            })

    if df_event_direct is not None and len(df_event_direct) > 0:
        for _, r in df_event_direct.iterrows():
            rows.append({
                "module": "direct_event_state",
                "response": r.get("response", ""),
                "target_metric": f"{r.get('event_type', '')}_{r.get('window_role', '')}",
                "driver": r.get("event_type", ""),
                "n": r.get("n_cities", np.nan),
                "effect_1": r.get("vd_occ_mean", np.nan),
                "effect_2": r.get("vd_persistence_mean", np.nan),
                "effect_3": r.get("blh_mean", np.nan),
                "effect_4": r.get("gust_mean", np.nan),
                "effect_5": r.get("shear_mean", np.nan),
                "effect_6": r.get("wind100_mean", np.nan),
            })

    if df_phase_sum is not None and len(df_phase_sum) > 0:
        for event_type in sorted(df_phase_sum["event_type"].dropna().unique()):
            core0 = df_phase_sum[
                (df_phase_sum["event_type"] == event_type) &
                (df_phase_sum["relative_hour"] == 0)
            ]
            if len(core0) == 0:
                continue
            rr = core0.iloc[0]
            rows.append({
                "module": "hourly_phase_center",
                "response": "raw_hourly",
                "target_metric": f"{event_type}_center",
                "driver": event_type,
                "n": rr.get("n_events", np.nan),
                "effect_1": rr.get("blh_mean", np.nan),
                "effect_2": rr.get("gust_mean", np.nan),
                "effect_3": rr.get("shear_mean", np.nan),
                "effect_4": rr.get("wind10_mean", np.nan),
                "effect_5": rr.get("wind100_mean", np.nan),
                "effect_6": rr.get("deltaU_mean", np.nan),
            })

    return pd.DataFrame(rows)


# =========================================================
# MAIN
# =========================================================
def main():
    set_topjournal_rcparams()

    parser = argparse.ArgumentParser(
        description="Boundary-layer and event diagnostics directly based on DYNAMICS_CORRIDOR merged summary"
    )
    parser.add_argument("--era5_root", type=str, default=DEFAULT_ERA5_ROOT)
    parser.add_argument("--dynamics_root", type=str, default=DEFAULT_DYNAMICS_ROOT)
    parser.add_argument("--merged_csv", type=str, default=DEFAULT_MERGED_CSV)
    parser.add_argument("--output_root", type=str, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--cities", nargs="*", default=None)

    parser.add_argument("--year0", type=int, default=2015)
    parser.add_argument("--year1", type=int, default=2025)

    parser.add_argument("--day_hour_start", type=int, default=8)
    parser.add_argument("--day_hour_end", type=int, default=18)
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

    parser.add_argument("--phase_event_q", type=float, default=0.95)
    parser.add_argument("--phase_hours", type=int, default=12)
    parser.add_argument("--phase_min_event_len", type=int, default=1)

    parser.add_argument("--surface_bins_blh", type=int, default=10)
    parser.add_argument("--surface_bins_shear", type=int, default=10)

    args = parser.parse_args()

    out_root = args.output_root
    table_root = os.path.join(out_root, "tables")
    fig_root = os.path.join(out_root, "figures")
    fig_ctrl_root = os.path.join(fig_root, "continuous_controls")
    fig_surface_root = os.path.join(fig_root, "response_surfaces")
    fig_event_root = os.path.join(fig_root, "direct_event_states")
    fig_phase_root = os.path.join(fig_root, "hourly_phase")
    cache_root = os.path.join(out_root, "cache")

    ensure_dirs(
        out_root,
        table_root,
        fig_root,
        fig_ctrl_root,
        fig_surface_root,
        fig_event_root,
        fig_phase_root,
        cache_root
    )

    print("[INFO] Loading dynamics merged summary:")
    print(args.merged_csv)

    df_merged = load_dynamics_merged_csv(args.merged_csv)
    print(f"[INFO] merged rows = {len(df_merged)}")
    print(f"[INFO] merged cities = {df_merged['city'].nunique()}")
    print(f"[INFO] merged states = {df_merged['state_group'].nunique()}")

    df_vd = build_direct_vertical_decoupling_from_merged(df_merged)
    df_vd.to_csv(os.path.join(table_root, "direct_vertical_decoupling_from_dynamics_merged.csv"), index=False)

    # city selection
    if args.cities is None or len(args.cities) == 0:
        cities_from_table = sorted(df_vd["city"].dropna().astype(str).unique().tolist())
        cities_from_disk = find_all_cities_on_disk(args.era5_root, int(args.year0), int(args.year1))
        cities = [c for c in cities_from_table if c in set(cities_from_disk)]
    else:
        cities = args.cities

    print(f"[INFO] selected cities = {len(cities)}")
    print(cities)

    if len(cities) == 0:
        raise RuntimeError("No valid cities after merged-table and disk filtering.")

    # filter vd to selected cities
    df_vd = df_vd[df_vd["city"].isin(cities)].reset_index(drop=True)

    # report missing states
    states_present = sorted(df_vd["state_group"].dropna().astype(str).unique().tolist())
    missing_target_states = [s for s in ALL_TARGET_STATES if s not in states_present]
    pd.DataFrame({
        "target_state": ALL_TARGET_STATES,
        "present_in_merged_csv": [int(s in states_present) for s in ALL_TARGET_STATES],
    }).to_csv(os.path.join(table_root, "target_state_coverage.csv"), index=False)

    print("[INFO] target-state coverage written.")
    if len(missing_target_states) > 0:
        print("[WARN] Missing target states in merged csv:")
        print(missing_target_states)

    # raw hourly city mean meteorology
    all_hourly = []
    failed_cities = []

    for city in cities:
        print(f"[INFO] Building hourly city-mean meteorology: {city}")
        try:
            dfh = compute_city_hourly_mean_timeseries(
                era5_root=args.era5_root,
                city=city,
                year0=int(args.year0),
                year1=int(args.year1),
            )
            if len(dfh) == 0:
                failed_cities.append({"city": city, "reason": "no_hourly_data"})
                continue
            all_hourly.append(dfh)
            dfh.to_csv(
                os.path.join(cache_root, f"{city}_hourly_citymean_{args.year0}_{args.year1}.csv"),
                index=False
            )
        except Exception as e:
            failed_cities.append({"city": city, "reason": str(e)})

    pd.DataFrame(failed_cities).to_csv(
        os.path.join(table_root, "failed_cities_hourly_meteorology.csv"),
        index=False
    )

    if len(all_hourly) == 0:
        raise RuntimeError("No hourly ERA5 city-mean data could be built.")

    df_hourly_all = pd.concat(all_hourly, ignore_index=True).sort_values(["city", "time"]).reset_index(drop=True)
    df_hourly_all.to_csv(os.path.join(table_root, "city_hourly_mean_meteorology.csv"), index=False)

    # state-level meteorology summary for both regime states and event states
    df_state_met = summarize_state_level_meteorology_all_states(
        df_hourly_all=df_hourly_all,
        target_states=[s for s in ALL_TARGET_STATES if s in states_present],
        day_hour_start=int(args.day_hour_start),
        day_hour_end=int(args.day_hour_end),
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
    df_state_met.to_csv(os.path.join(table_root, "state_level_meteorology_all_states.csv"), index=False)

    # direct vd + continuous controls
    df_cont = build_vd_continuous_controls(df_vd, df_state_met)
    df_cont.to_csv(os.path.join(table_root, "vd_with_continuous_controls_from_dynamics_v2.csv"), index=False)

    # continuous control fits
    df_fit = fit_continuous_controls(df_cont)
    df_fit.to_csv(os.path.join(table_root, "continuous_control_fits.csv"), index=False)

    # figures: continuous controls
    responses = sorted(df_cont["response"].dropna().unique().tolist())

    for response in responses:
        plot_driver_vs_vd_scatter(
            df_cont, response, "blh_mean", "vd_occ",
            os.path.join(fig_ctrl_root, f"fig_BLH_vs_vd_occ_{response}.png"),
            color_col="shear_mean"
        )
        plot_driver_vs_vd_scatter(
            df_cont, response, "blh_mean", "vd_persistence",
            os.path.join(fig_ctrl_root, f"fig_BLH_vs_vd_persistence_{response}.png"),
            color_col="shear_mean"
        )
        plot_driver_vs_vd_scatter(
            df_cont, response, "shear_mean", "vd_occ",
            os.path.join(fig_ctrl_root, f"fig_shear_vs_vd_occ_{response}.png"),
            color_col="blh_mean"
        )
        plot_driver_vs_vd_scatter(
            df_cont, response, "shear_mean", "vd_persistence",
            os.path.join(fig_ctrl_root, f"fig_shear_vs_vd_persistence_{response}.png"),
            color_col="blh_mean"
        )
        plot_driver_vs_vd_scatter(
            df_cont, response, "gust_mean", "vd_occ",
            os.path.join(fig_ctrl_root, f"fig_gust_vs_vd_occ_{response}.png"),
            color_col="shear_mean"
        )
        plot_driver_vs_vd_scatter(
            df_cont, response, "gust_mean", "vd_persistence",
            os.path.join(fig_ctrl_root, f"fig_gust_vs_vd_persistence_{response}.png"),
            color_col="shear_mean"
        )
        plot_quadrant_with_driver(
            df_cont, response, "blh_mean",
            os.path.join(fig_ctrl_root, f"fig_quadrant_colored_by_BLH_{response}.png")
        )
        plot_quadrant_with_driver(
            df_cont, response, "shear_mean",
            os.path.join(fig_ctrl_root, f"fig_quadrant_colored_by_shear_{response}.png")
        )

        for xcol in ["blh_mean", "shear_mean", "gust_mean", "wind10_mean", "wind100_mean"]:
            for ycol in ["vd_occ", "vd_persistence"]:
                plot_nonlinear_spline_fit(
                    df_cont, response, ycol, xcol,
                    os.path.join(fig_ctrl_root, f"fig_nonlinear_{response}_{xcol}_to_{ycol}.png")
                )

        for metric in ["vd_occ", "vd_persistence", "vd_largest_frac", "vd_pc", "vd_anis"]:
            plot_state_heatmap(
                df_cont, response, metric,
                os.path.join(fig_ctrl_root, f"fig_city_state_heatmap_{response}_{metric}.png")
            )

    # 2D response surfaces
    surface_rows_all = []
    for response in responses:
        for ycol in ["vd_occ", "vd_persistence", "vd_largest_frac", "vd_pc", "vd_anis"]:
            df_surface, x_edges, y_edges, mat = build_2d_response_surface(
                df=df_cont,
                response=response,
                ycol=ycol,
                x1="blh_mean",
                x2="shear_mean",
                bins1=int(args.surface_bins_blh),
                bins2=int(args.surface_bins_shear),
            )
            if len(df_surface) > 0:
                surface_rows_all.append(df_surface)
                plot_2d_response_surface(
                    x_edges=x_edges,
                    y_edges=y_edges,
                    mat=mat,
                    response=response,
                    y_metric=ycol,
                    outpath=os.path.join(fig_surface_root, f"fig_surface_{response}_{ycol}.png")
                )

    df_surface_all = pd.concat(surface_rows_all, ignore_index=True) if len(surface_rows_all) > 0 else pd.DataFrame()
    df_surface_all.to_csv(os.path.join(table_root, "response_surface_blh_shear.csv"), index=False)

    # direct event state summary from actual dynamics event states
    df_event_direct = build_direct_event_state_summary(df_cont)
    df_event_direct.to_csv(os.path.join(table_root, "direct_event_state_summary.csv"), index=False)

    df_event_city = build_event_city_table(df_cont)
    df_event_city.to_csv(os.path.join(table_root, "direct_event_state_city_table.csv"), index=False)

    for response in responses:
        for event_type in ["gust", "shear"]:
            plot_event_window_bars(
                df_event_direct, event_type, response,
                os.path.join(fig_event_root, f"fig_{event_type}_lead_core_lag_direct_vd_{response}.png")
            )
            plot_event_driver_evolution(
                df_event_direct, event_type, response,
                os.path.join(fig_event_root, f"fig_{event_type}_driver_evolution_direct_states_{response}.png")
            )

    # hourly raw event phase trajectories
    df_gust_phase = build_event_phase_trajectory_hourly(
        df_hourly_all=df_hourly_all,
        target_col="gust_mean",
        event_q=float(args.phase_event_q),
        phase_hours=int(args.phase_hours),
        min_event_len=int(args.phase_min_event_len),
    )
    df_shear_phase = build_event_phase_trajectory_hourly(
        df_hourly_all=df_hourly_all,
        target_col="shear_mean",
        event_q=float(args.phase_event_q),
        phase_hours=int(args.phase_hours),
        min_event_len=int(args.phase_min_event_len),
    )

    if len(df_gust_phase) > 0:
        df_gust_phase.to_csv(os.path.join(table_root, "gust_event_phase_hourly.csv"), index=False)
    if len(df_shear_phase) > 0:
        df_shear_phase.to_csv(os.path.join(table_root, "shear_event_phase_hourly.csv"), index=False)

    df_gust_phase_sum = summarize_event_phase_trajectory(df_gust_phase)
    df_shear_phase_sum = summarize_event_phase_trajectory(df_shear_phase)

    if len(df_gust_phase_sum) > 0:
        df_gust_phase_sum.to_csv(os.path.join(table_root, "gust_event_phase_summary.csv"), index=False)
        plot_event_phase_trajectory(
            df_gust_phase_sum, "gust",
            os.path.join(fig_phase_root, "fig_gust_event_phase_trajectory.png")
        )
    if len(df_shear_phase_sum) > 0:
        df_shear_phase_sum.to_csv(os.path.join(table_root, "shear_event_phase_summary.csv"), index=False)
        plot_event_phase_trajectory(
            df_shear_phase_sum, "shear",
            os.path.join(fig_phase_root, "fig_shear_event_phase_trajectory.png")
        )

    # discovery summary
    df_phase_combined = pd.concat(
        [df_gust_phase_sum, df_shear_phase_sum],
        ignore_index=True
    ) if (len(df_gust_phase_sum) > 0 or len(df_shear_phase_sum) > 0) else pd.DataFrame()

    df_discovery = build_discovery_summary(
        df_fit=df_fit,
        df_event_direct=df_event_direct,
        df_phase_sum=df_phase_combined
    )
    df_discovery.to_csv(os.path.join(table_root, "boundary_layer_event_discovery_summary.csv"), index=False)

    # excel summary
    xlsx_path = os.path.join(out_root, "BOUNDARY_LAYER_EVENT_DIAGNOSTICS_FROM_DYNAMICS_V2.xlsx")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        df_merged.to_excel(writer, sheet_name="DYNAMICS_MERGED_RAW", index=False)
        df_vd.to_excel(writer, sheet_name="DIRECT_VERTICAL_DECOUPLING", index=False)
        df_state_met.to_excel(writer, sheet_name="STATE_MET_ALL", index=False)
        df_cont.to_excel(writer, sheet_name="VD_CONTINUOUS_CONTROLS", index=False)
        df_fit.to_excel(writer, sheet_name="CONTINUOUS_FITS", index=False)
        df_surface_all.to_excel(writer, sheet_name="RESPONSE_SURFACES", index=False)
        df_event_direct.to_excel(writer, sheet_name="DIRECT_EVENT_SUMMARY", index=False)
        df_event_city.to_excel(writer, sheet_name="DIRECT_EVENT_CITY", index=False)
        df_gust_phase_sum.to_excel(writer, sheet_name="GUST_PHASE_SUMMARY", index=False)
        df_shear_phase_sum.to_excel(writer, sheet_name="SHEAR_PHASE_SUMMARY", index=False)
        df_discovery.to_excel(writer, sheet_name="DISCOVERY", index=False)
        pd.DataFrame(failed_cities).to_excel(writer, sheet_name="FAILED_CITIES", index=False)

    run_info = {
        "era5_root": args.era5_root,
        "dynamics_root": args.dynamics_root,
        "merged_csv": args.merged_csv,
        "output_root": args.output_root,
        "cities": cities,
        "year0": int(args.year0),
        "year1": int(args.year1),
        "regime_states_target": REGIME_STATES,
        "event_states_target": EVENT_STATES,
        "day_hour_start": int(args.day_hour_start),
        "day_hour_end": int(args.day_hour_end),
        "shear_low_q": float(args.shear_low_q),
        "shear_high_q": float(args.shear_high_q),
        "shear_extreme_q": float(args.shear_extreme_q),
        "gust_high_q": float(args.gust_high_q),
        "gust_extreme_q": float(args.gust_extreme_q),
        "blh_low_q": float(args.blh_low_q),
        "blh_high_q": float(args.blh_high_q),
        "event_lead_hours": int(args.event_lead_hours),
        "event_lag_hours": int(args.event_lag_hours),
        "event_min_gap_hours": int(args.event_min_gap_hours),
        "phase_event_q": float(args.phase_event_q),
        "phase_hours": int(args.phase_hours),
        "phase_min_event_len": int(args.phase_min_event_len),
        "surface_bins_blh": int(args.surface_bins_blh),
        "surface_bins_shear": int(args.surface_bins_shear),
        "missing_target_states": missing_target_states,
    }
    with open(os.path.join(out_root, "run_info.json"), "w", encoding="utf-8") as f:
        json.dump(run_info, f, ensure_ascii=False, indent=2)

    print("[ALL DONE]")
    print(f"Output root: {out_root}")
    print(f"Summary xlsx: {xlsx_path}")


if __name__ == "__main__":
    main()
