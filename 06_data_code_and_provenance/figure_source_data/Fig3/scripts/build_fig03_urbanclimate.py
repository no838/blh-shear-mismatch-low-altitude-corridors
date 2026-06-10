#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def annotate(ax, label: str) -> None:
    ax.text(-0.12, 1.03, label, transform=ax.transAxes, fontsize=12, fontweight='bold', ha='left', va='bottom')


def build() -> Path:
    fig_dir = Path(__file__).resolve().parents[1]
    source = fig_dir / 'source_tables'
    out_dir = fig_dir / 'figure_output'
    out_dir.mkdir(parents=True, exist_ok=True)

    contrasts = pd.read_csv(source / 'hotspot_vs_nonhotspot_summary.csv')
    pred = pd.read_csv(source / 'fig3_predictive_cv.csv')
    capture = pd.read_csv(source / 'fig3_capture_curve.csv')
    enrich = pd.read_csv(source / 'hotspot_enrichment_state_group.csv')

    contrasts = contrasts.sort_values('signed_effect_size')
    pred = pred.sort_values('auc_mean')
    enrich = enrich.sort_values('log2_enrichment', ascending=False).head(8)

    fig = plt.figure(figsize=(11.0, 7.6), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.0, 1.0])
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    y = np.arange(len(contrasts))
    colors = ['#2c7fb8' if v < 0 else '#d95f02' for v in contrasts['signed_effect_size']]
    ax1.hlines(y, 0, contrasts['signed_effect_size'], color=colors, linewidth=2.0)
    ax1.scatter(contrasts['signed_effect_size'], y, color=colors, s=36, zorder=3)
    ax1.axvline(0.0, linestyle='--', color='0.55', linewidth=0.9)
    ax1.set_yticks(y)
    ax1.set_yticklabels(contrasts['variable'].str.replace('_', ' '), fontsize=8)
    ax1.set_xlabel('Signed effect size', fontsize=8)
    ax1.set_title('Hotspot versus non-hotspot contrasts', fontsize=9)
    ax1.grid(axis='x', color='0.92', linewidth=0.7)
    annotate(ax1, 'A')

    y2 = np.arange(len(pred))
    ax2.errorbar(pred['auc_mean'], y2, xerr=pred['auc_sd'], fmt='o', color='#4c78a8', ecolor='0.55', elinewidth=1.0, capsize=2)
    ax2.set_yticks(y2)
    ax2.set_yticklabels(pred['model'], fontsize=7)
    ax2.set_xlabel('Cross-validated ROC AUC', fontsize=8)
    ax2.set_title('Predictive benchmark models', fontsize=9)
    ax2.grid(axis='x', color='0.92', linewidth=0.7)
    annotate(ax2, 'B')

    ax3.plot(capture['k'], capture['mismatch_capture'], color='#d95f02', marker='o', label='Mismatch-ranked sectors')
    ax3.plot(capture['k'], capture['intensity_capture'], color='#7570b3', marker='o', label='Intensity-ranked sectors')
    ax3.set_xlabel('Top-k sectors', fontsize=8)
    ax3.set_ylabel('Captured hotspot share', fontsize=8)
    ax3.set_ylim(-0.02, 1.05)
    ax3.set_title('Top-k hotspot capture', fontsize=9)
    ax3.grid(color='0.92', linewidth=0.7)
    ax3.legend(frameon=False, fontsize=7, loc='lower right')
    annotate(ax3, 'C')

    y4 = np.arange(len(enrich))
    ax4.barh(y4, enrich['log2_enrichment'], color='#2a9d8f')
    ax4.set_yticks(y4)
    ax4.set_yticklabels(enrich['category'].str.replace('_', ' '), fontsize=8)
    ax4.invert_yaxis()
    ax4.set_xlabel('log2 enrichment', fontsize=8)
    ax4.set_title('Hotspot-enriched state groups', fontsize=9)
    ax4.grid(axis='x', color='0.92', linewidth=0.7)
    annotate(ax4, 'D')

    out_base = out_dir / 'Figure_3'
    fig.savefig(out_base.with_suffix('.png'), dpi=320, bbox_inches='tight')
    fig.savefig(out_base.with_suffix('.pdf'), bbox_inches='tight')
    fig.savefig(out_base.with_suffix('.svg'), bbox_inches='tight')
    plt.close(fig)
    return out_base


if __name__ == '__main__':
    out = build()
    print(f'Wrote {out.with_suffix(".png")}')
