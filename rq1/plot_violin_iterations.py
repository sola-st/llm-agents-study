#!/usr/bin/env python3

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# === CONFIGURATION ===
config = {
    'files': [
        {'path': 'rq1_stats/repairagent_iterations.csv', 'name': 'RepairAgent'},
        {'path': 'rq1_stats/codeact_iterations.csv', 'name': 'OpenHands'},
        {'path': 'rq1_stats/acr_iterations.csv', 'name': 'AutoCodeRover'}
    ],
    'status_column': 'is_resolved',
    'raw_status_variants': ['is_resolved'],
    'metric_column': 'n_iterations',
    'metric_title': 'Number of Iterations',
    'fig': {
        'figsize': (8, 5),
        'title_fontsize': 16,
        'axis_label_fontsize': 16,
        'tick_label_fontsize': 16,
        'subplot_title_fontsize': 16
    },
    'colors': {
        True:  '#2ca02c',  # Success (green)
        False: '#d62728'   # Failure (red)
    },
    'labels': {
        True:  'Success',
        False: 'Failure'
    },
    'output_file': 'rq1_stats/iterations_violinplot.png',
}
# === END CONFIGURATION ===

def read_and_prepare(path, cfg):
    df = pd.read_csv(path)
    for raw in cfg['raw_status_variants']:
        if raw in df.columns and raw != cfg['status_column']:
            df = df.rename(columns={raw: cfg['status_column']})
            break
    return df

def plot_three_panel(cfg):
    n = len(cfg['files'])
    fig, axes = plt.subplots(1, n, figsize=cfg['fig']['figsize'])

    for ax, file_info in zip(axes, cfg['files']):
        df = read_and_prepare(file_info['path'], cfg)
        series = df[cfg['metric_column']]

        data_success = series[df[cfg['status_column']] == True]
        data_failure = series[df[cfg['status_column']] == False]

        parts = ax.violinplot([data_success, data_failure], positions=[1, 2], widths=0.6, showmeans=False, showextrema=False, showmedians=False)

        for i, pc in enumerate(parts['bodies']):
            pc.set_facecolor(cfg['colors'][bool(i == 0)])
            pc.set_edgecolor('black')
            pc.set_alpha(0.7)

        medians = [np.median(data_success), np.median(data_failure)]
        means = [np.mean(data_success), np.mean(data_failure)]

        for x, (median, mean) in zip([1, 2], zip(medians, means)):
            ax.hlines(median, x - 0.3, x + 0.3, colors='black', linewidth=2)
            ax.hlines(mean, x - 0.3, x + 0.3, colors='black', linestyles='dashed', linewidth=1.5)

            offset = 0.03 * (max(median, mean) if max(median, mean) != 0 else 1)
            if abs(median - mean) < offset * 3:
                ax.text(x - 0.15, median + offset, f"{median:.1f}", ha='right', va='bottom', fontsize=12, color='black')
                ax.text(x + 0.15, mean - offset, f"{mean:.1f}", ha='left', va='top', fontsize=12, color='black')
            else:
                ax.text(x, median, f"{median:.1f}", ha='center', va='bottom', fontsize=12, color='black')
                ax.text(x, mean, f"{mean:.1f}", ha='center', va='top', fontsize=12, color='black')

        ax.set_xticks([1, 2])
        ax.set_xticklabels([cfg['labels'][True], cfg['labels'][False]], fontsize=cfg['fig']['tick_label_fontsize'])
        ax.set_title(file_info['name'], fontsize=cfg['fig']['subplot_title_fontsize'])
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        ax.tick_params(axis='both', which='major', labelsize=cfg['fig']['tick_label_fontsize'])
        ax.set_ylabel("Iterations", fontsize=cfg['fig']['axis_label_fontsize'])
        ax.set_ylim(bottom=0)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='black', linewidth=2, label='Median'),
        Line2D([0], [0], color='black', linestyle='--', linewidth=1.5, label='Mean')
    ]

    fig.legend(handles=legend_elements, loc='upper right', fontsize=12)
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])

    if cfg['output_file']:
        plt.savefig(cfg['output_file'], dpi=300)
        print(f"Saved figure to {cfg['output_file']}")
    else:
        plt.show()

if __name__ == '__main__':
    plot_three_panel(config)
