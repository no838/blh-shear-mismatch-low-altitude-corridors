#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import TwoSlopeNorm

REGIME_ORDER_OCC = [
    'stable_shear_high', 'gust_shear_compound', 'shear_weak', 'day', 'night',
    'unstable_like', 'stable_like', 'shear_moderate', 'gust_extreme',
    'shear_extreme', 'gust_high',
]
REGIME_ORDER_PERSIST = [
    'unstable_like', 'gust_shear_compound', 'stable_shear_high', 'shear_weak',
    'gust_high', 'stable_like', 'shear_moderate', 'gust_extreme',
    'night', 'shear_extreme', 'day',
]
STATE_LABELS = {
    'stable_like': 'Stable',
    'unstable_like': 'Unstable',
    'day': 'Day',
    'night': 'Night',
    'shear_weak': 'Weak shear',
    'shear_moderate': 'Mod shear',
    'shear_extreme': 'Ext shear',
    'gust_high': 'High gust',
    'gust_extreme': 'Ext gust',
    'stable_shear_high': 'Stable+shear',
    'gust_shear_compound': 'Gust+shear',
}
PHASE_LABEL_OFFSETS = {
    'stable_like': (10, 0.05),
    'unstable_like': (10, 0.02),
    'day': (10, -0.05),
    'night': (10, 0.03),
    'shear_weak': (10, -0.05),
    'shear_moderate': (10, 0.05),
    'shear_extreme': (10, 0.04),
    'gust_high': (10, 0.02),
    'gust_extreme': (10, 0.03),
    'stable_shear_high': (10, 0.04),
    'gust_shear_compound': (10, 0.04),
}


def label_state(x: str) -> str:
    return STATE_LABELS.get(str(x), str(x))


def annotate(ax, label: str) -> None:
    ax.text(-0.12, 1.03, label, transform=ax.transAxes, fontsize=12, fontweight='bold', ha='left', va='bottom')


def draw_paired(ax, df: pd.DataFrame, metric: str, ci: str, order: list[str], title: str) -> None:
    sub = df[df['state_group'].isin(order)].copy()
    y_map = {s: i for i, s in enumerate(order)}
    sub['y'] = sub['state_group'].map(y_map).astype(float)
    colors = {'ar1': '#1f78b4', 'var': '#ff7f00'}
    offsets = {'ar1': -0.14, 'var': 0.14}
    for resp in ['ar1', 'var']:
        s = sub[sub['response'] == resp].copy()
        ax.hlines(
            s['y'] + offsets[resp],
            s[metric].astype(float) - s[ci].astype(float),
            s[metric].astype(float) + s[ci].astype(float),
            color=colors[resp], linewidth=1.8, alpha=0.95,
        )
        ax.scatter(s[metric], s['y'] + offsets[resp], s=30, color=colors[resp], edgecolor='white', linewidth=0.5, label=resp.upper() if metric == 'vd_occ_mean' else None, zorder=3)
    for state in order:
        s = sub[sub['state_group'] == state].set_index('response')
        if {'ar1', 'var'}.issubset(s.index):
            ax.plot([s.loc['ar1', metric], s.loc['var', metric]], [y_map[state] + offsets['ar1'], y_map[state] + offsets['var']], color='0.78', linewidth=0.9, zorder=1)
    ax.axvline(0.0, linestyle='--', linewidth=0.9, color='0.55')
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels([label_state(s) for s in order], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Diagnostic difference (100 m minus 10 m)', fontsize=8)
    ax.set_title(title, fontsize=9)
    ax.grid(axis='x', color='0.9', linewidth=0.7)
    ax.tick_params(axis='x', labelsize=8)


def build() -> Path:
    root = Path(__file__).resolve().parents[1]
    source = root / 'data' / 'figure_1' / 'regime_state_summary_table.csv'
    out_dir = root / 'figures'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(source)

    fig = plt.figure(figsize=(10.8, 7.6), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.0, 1.0])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    draw_paired(ax1, df, 'vd_occ_mean', 'vd_occ_ci95', REGIME_ORDER_OCC, 'Occupancy response hierarchy')
    draw_paired(ax2, df, 'vd_persistence_mean', 'vd_persistence_ci95', REGIME_ORDER_PERSIST, 'Persistence response hierarchy')
    annotate(ax1, 'A')
    annotate(ax2, 'B')
    ax1.legend(frameon=False, fontsize=8, loc='lower right')

    phase_df = df[df['response'] == 'ar1'].copy()
    phase_df = phase_df[phase_df['state_group'].isin(sorted(STATE_LABELS))].copy()
    norm = TwoSlopeNorm(vcenter=0.0, vmin=float(phase_df['vd_occ_mean'].min()), vmax=float(phase_df['vd_occ_mean'].max()))
    size = 120 + 500 * np.clip(phase_df['abs_vd_occ_mean'].astype(float), 0, None)
    sc = ax3.scatter(
        phase_df['blh_mean'], phase_df['shear_mean'], c=phase_df['vd_occ_mean'], s=size,
        cmap='coolwarm', norm=norm, edgecolor='white', linewidth=0.8, alpha=0.95,
    )
    for _, row in phase_df.iterrows():
        dx, dy = PHASE_LABEL_OFFSETS.get(row['state_group'], (8, 0.02))
        ax3.text(row['blh_mean'] + dx, row['shear_mean'] + dy, label_state(row['state_group']), fontsize=7, color='0.3')
    ax3.set_xlabel('Boundary-layer height (m)', fontsize=8)
    ax3.set_ylabel('Shear proxy (m s$^{-1}$)', fontsize=8)
    ax3.set_title('Regime phase space for occupancy difference', fontsize=9)
    ax3.grid(color='0.92', linewidth=0.7)
    ax3.tick_params(labelsize=8)
    cb = fig.colorbar(sc, ax=ax3, fraction=0.046, pad=0.04)
    cb.set_label('Occupancy diagnostic difference', fontsize=8)
    cb.ax.tick_params(labelsize=7)
    annotate(ax3, 'C')

    rows = REGIME_ORDER_OCC
    heat = []
    for state in rows:
        row = []
        for response, metric in [('ar1', 'vd_occ_mean'), ('var', 'vd_occ_mean'), ('ar1', 'vd_persistence_mean'), ('var', 'vd_persistence_mean')]:
            sub = df[(df['state_group'] == state) & (df['response'] == response)]
            row.append(float(sub.iloc[0][metric]) if len(sub) else np.nan)
        heat.append(row)
    heat = np.array(heat, dtype=float)
    hm = ax4.imshow(heat, cmap='coolwarm', aspect='auto', norm=TwoSlopeNorm(vcenter=0.0, vmin=np.nanmin(heat), vmax=np.nanmax(heat)))
    for i in range(heat.shape[0]):
        for j in range(heat.shape[1]):
            if np.isfinite(heat[i, j]):
                ax4.text(j, i, f'{heat[i, j]:.2f}', ha='center', va='center', fontsize=6, color='black')
    ax4.set_xticks(range(4))
    ax4.set_xticklabels(['Occ | AR1', 'Occ | VAR', 'Per | AR1', 'Per | VAR'], rotation=25, ha='right', fontsize=7)
    ax4.set_yticks(range(len(rows)))
    ax4.set_yticklabels([label_state(s) for s in rows], fontsize=7)
    ax4.set_title('Cross-response regime signature matrix', fontsize=9)
    fig.colorbar(hm, ax=ax4, fraction=0.046, pad=0.04)
    annotate(ax4, 'D')

    out_base = out_dir / 'Figure_1'
    fig.savefig(out_base.with_suffix('.png'), dpi=320, bbox_inches='tight')
    fig.savefig(out_base.with_suffix('.pdf'), bbox_inches='tight')
    fig.savefig(out_base.with_suffix('.svg'), bbox_inches='tight')
    plt.close(fig)
    return out_base


if __name__ == '__main__':
    out = build()
    print(f'Wrote {out.with_suffix(".png")}')
