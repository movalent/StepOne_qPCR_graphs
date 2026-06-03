import re
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

import pandas as pd

def nat_keys(string: str) -> list:
    """
    Split string into text and numbers for natural sorting

    Args:
        string (str): Sample name.

    Returns:
        list: List containing only samples with numbers
    """
    parts = re.split(r'(\d*\.?\d*)', string)
    key = []

    for part in parts:
        if re.fullmatch(r'\d+\.\d+', part):
            key.append(float(part))
        elif part.isdigit():
            key.append(int(part))
        else:
            key.append(part.lower())

    return key

def sort_key(name: str) -> tuple:
    """
    Create custom sort key.

    Args:
        name (str): String to be asessed.

    Returns:
        tuple: Tuple with position.

    Notes:
        Legend is hard-coded to place numeric values first (0, ), then any text (1, ) and Mock samples at the bottom
        (2, ).
    """
    if name.lower().startswith('mock'):
        return (2, nat_keys(name))

    match = re.match(r'^(\d+(?:\.\d+)?)%', name)
    if match:
        numeric_value = float(match.group(1))
        return (0, numeric_value, nat_keys(name))

    return (1, nat_keys(name))


def create_amplification_plots(
        df: pd.DataFrame,
        target_names: list[str],
        thresholds: dict[str, float],
        plot_prop: dict[str, Any],
        date: str,
        data_paths: dict[str, Path]
        ) -> None:
    """
    Generate amplification plots for each target using processed qPCR data. Filters data by target and inclusion flag before plotting. Plots are saved to disk in output folder in multiple formats.

    Args:
        df (pd.DataFrame): Processed DataFrame used to generate the plots.
        target_names (list[str]): List of unique target names detected in the processed DataFrame.
        thresholds (dict[str, float]): ΔRn threshold values per target.
        plot_prop (dict[str, Any]): Plot configuration parameters (e.g. DPI, transparency)
        date (str): Experiment date.
        data_paths (dict[str, Path]): Dictionary containing resolved file paths.

    Returns:
        None

    Notes:
        If a threshold is not defined for a given target, the user is prompted to provide a value interactively.
    """
    GRAPH_LINEWIDTH = 0.75
    GRAPH_FONTNAME = 'Cambria'

    TITLE_FONTSIZE = 16
    AXIS_FONTSIZE = 14
    LEGEND_FONTSIZE = 7
    THRESHOLD_LABEL_FONTSIZE = 10

    DISP_CYCLE_START = 0
    DISP_CYCLE_END = 40
    DISP_CYCLE_INTERVAL = 2

    DISP_RN_MIN = 0.01
    DISP_RN_MAX = 5

    THRESHOLD_LINE_COL = 'red'
    THRESHOLD_LINE_STYLE = 'dashed'

    OUTPUT_FORMATS = ['png', 'tiff', 'pdf']

    for target in target_names:

        slice_df = df.loc[
            (df['Target Name'] == target) &
            (df['include'] == 1)
            ]

        if slice_df.empty:
            continue

        try:
            threshold = float(thresholds[target])
        except KeyError:
            threshold = float(input(f'No threshold specified for {target}. Input the threshold manually, or add to the configuration file and restart the script: '))

        fig, ax = plt.subplots(figsize=(8,5))

        targets = slice_df.groupby(by='sample_name')

        for sample_name, group in targets:
            ax.plot(
                group['Cycle'],
                group['ΔRn'],
                color=group['color'].iloc[0],
                linewidth=GRAPH_LINEWIDTH,
                label=sample_name
            )

        # Graph style
        ax.set_title(
            f'Amplification plot for {target} {date}',
            fontname=GRAPH_FONTNAME,
            fontsize=TITLE_FONTSIZE
            )
        ax.set_xlabel('Cycle', fontname=GRAPH_FONTNAME, fontsize=AXIS_FONTSIZE)
        ax.set_ylabel('ΔRn', fontname=GRAPH_FONTNAME, fontsize=AXIS_FONTSIZE)

        ax.grid(True, color='grey', axis='y')

        # Threshold line
        ax.hlines(
            y=threshold,
            xmin=DISP_CYCLE_START,
            xmax=DISP_CYCLE_END,
            color=THRESHOLD_LINE_COL,
            linestyles=THRESHOLD_LINE_STYLE,
            linewidth=1
            )

        # Threshold label
        ax.text(
            DISP_CYCLE_END * 0.98,
            threshold * 1.05,
            'Threshold',
            color=THRESHOLD_LINE_COL,
            fontsize=THRESHOLD_LABEL_FONTSIZE,
            ha='right',
            va='bottom'
            )

        # Axes formatting
        ax.set_xlim([DISP_CYCLE_START, DISP_CYCLE_END])
        ax.xaxis.set_major_locator(plt.MultipleLocator(DISP_CYCLE_INTERVAL))

        ax.set_ylim([DISP_RN_MIN, DISP_RN_MAX])
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(ScalarFormatter())

        # Legend
        handles, labels = ax.get_legend_handles_labels()
        sorted_pairs = sorted(zip(labels, handles), key=lambda x: sort_key(x[0]))
        labels_sorted, handles_sorted = zip(*sorted_pairs)

        ax.legend(
            handles_sorted,
            labels_sorted,
            fontsize=LEGEND_FONTSIZE,
            loc='upper left'
        )

        now = datetime.now()
        fmt_datetime = now.strftime('%Y-%m-%d %H-%M-%S')

        for file_type in OUTPUT_FORMATS :
            plt.savefig(
                data_paths['OUTPUT'] / f'{date}_{target}_{fmt_datetime}.{file_type}',
                transparent=plot_prop['transparent'],
                dpi=plot_prop['dpi']
                )

        plt.close()

