#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

CITY_SHORT = {
    'Australia_Sydney': 'Sydney',
    'Brazil_SaoPaulo': 'Sao Paulo',
    'China_GBA': 'GBA',
    'China_JJJ': 'JJJ',
    'China_YRD': 'YRD',
    'Germany_RhineRuhr': 'Rhine-Ruhr',
    'India_DelhiNCR': 'Delhi NCR',
    'Japan_Kanto': 'Kanto',
    'Nigeria_Lagos': 'Lagos',
    'Singapore_Johor_Riau': 'Singapore',
    'UAE_Dubai_AbuDhabi': 'Dubai-AbuDhabi',
    'UK_London': 'London',
    'USA_NYC': 'NYC',
}
TYPOLOGY_COLORS = {
    '100m_amplified_disordered': '#d95f02',
    '100m_amplified_structured': '#1b9e77',
    '10m_response_advantage': '#377eb8',
    '10m_response_advantage_but_100m_fragmented': '#984ea3',
}


def annotate(ax, label: str) -> None:
    ax.text(-0.12, 1.03, label, transform=ax.transAxes, fontsize=12, fontweight='bold', ha='left', va='bottom')


def build() -> Path:
    fig_dir = Path(__file__).resolve().parents[1]
    source = fig_dir / 'source_tables' / 'per_city_typology_table.csv'
    out_dir = fig_dir / 'figure_output'
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(source)
    df['city_short'] = df['city'].map(CITY_SHORT).fillna(df['city'])
    df['color'] = df['grid_mechanism_typology'].map(TYPOLOGY_COLORS).fillna('#7f7f7f')
    df = df.sort_values('city_entropy').reset_index(drop=True)

    fig = plt.figure(figsize=(11.0, 7.6), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.0, 1.0])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    ax1.scatter(df['city_entropy'], df['mean_delta_resp'], c=df['color'], s=90, edgecolor='white', linewidth=0.8)
    for _, row in df.iterrows():
        ax1.text(row['city_entropy'] + 0.0025, row['mean_delta_resp'] + 0.00005, row['city_short'], fontsize=7, color='0.3')
    ax1.axhline(0.0, linestyle='--', color='0.65', linewidth=0.9)
    ax1.set_xlabel('City entropy', fontsize=8)
    ax1.set_ylabel('Mean response shift', fontsize=8)
    ax1.set_title('Cross-city structure space', fontsize=9)
    ax1.grid(color='0.92', linewidth=0.7)
    annotate(ax1, 'A')

    y = np.arange(len(df))
    ax2.hlines(y, 0, df['strongest_regime_vd_occ'], color=df['color'], linewidth=2.0)
    ax2.scatter(df['strongest_regime_vd_occ'], y, color=df['color'], s=36, zorder=3)
    ax2.axvline(0.0, linestyle='--', color='0.55', linewidth=0.9)
    ax2.set_yticks(y)
    ax2.set_yticklabels(df['city_short'], fontsize=8)
    ax2.set_xlabel('Strongest regime occupancy difference', fontsize=8)
    ax2.set_title('Occupancy-persistence contrast: occupancy arm', fontsize=9)
    ax2.grid(axis='x', color='0.92', linewidth=0.7)
    annotate(ax2, 'B')

    ax3.hlines(y, 0, df['strongest_regime_vd_persistence'], color=df['color'], linewidth=2.0)
    ax3.scatter(df['strongest_regime_vd_persistence'], y, color=df['color'], s=36, zorder=3)
    ax3.axvline(0.0, linestyle='--', color='0.55', linewidth=0.9)
    ax3.set_yticks(y)
    ax3.set_yticklabels(df['city_short'], fontsize=8)
    ax3.set_xlabel('Strongest regime persistence difference', fontsize=8)
    ax3.set_title('Occupancy-persistence contrast: persistence arm', fontsize=9)
    ax3.grid(axis='x', color='0.92', linewidth=0.7)
    annotate(ax3, 'C')

    ax4.barh(y, df['mean_hotspot_jaccard'], color=df['color'])
    ax4.set_yticks(y)
    ax4.set_yticklabels(df['city_short'], fontsize=8)
    ax4.set_xlabel('Mean hotspot Jaccard', fontsize=8)
    ax4.set_title('City signature similarity', fontsize=9)
    ax4.grid(axis='x', color='0.92', linewidth=0.7)
    annotate(ax4, 'D')

    handles = []
    for key, color in TYPOLOGY_COLORS.items():
        handles.append(plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markeredgecolor='white', markersize=7, label=key.replace('_', ' ')))
    ax1.legend(handles=handles, frameon=False, fontsize=6.5, loc='best')

    out_base = out_dir / 'Figure_4'
    fig.savefig(out_base.with_suffix('.png'), dpi=320, bbox_inches='tight')
    fig.savefig(out_base.with_suffix('.pdf'), bbox_inches='tight')
    fig.savefig(out_base.with_suffix('.svg'), bbox_inches='tight')
    plt.close(fig)
    return out_base


if __name__ == '__main__':
    out = build()
    print(f'Wrote {out.with_suffix(".png")}')
