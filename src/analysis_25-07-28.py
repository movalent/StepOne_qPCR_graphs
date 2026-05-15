# Author: KlaudiaK
# Creation date: 28 July 2025

from datetime import datetime
from pathlib import Path
import re
import yaml

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import openpyxl
import pandas as pd

# Options for pandas dataframe print
pd.options.display.width = 0
pd.options.display.max_columns = 15

# Create graph
def create_graph(df, target_names, thresholds, date):

    for target in target_names:

        slice_df = df.loc[(df['Target Name'] == target) &
                          (df['include'] == 1)
                          ]

        if slice_df.empty:
            continue

        targets = slice_df.groupby(by='sample_name')

        threshold = thresholds[target]

        for sample_name, group in targets:

            x_values = group['Cycle']
            y_values = group['ΔRn']

            plt.plot(x_values, y_values,
                    color=group['color'].iloc[0],
                    linewidth=0.75,
                    label=sample_name if sample_name not in plt.gca().get_legend_handles_labels()[1] else ''
                    )
            # HINT: https://stackoverflow.com/a/47949224

        # Graph style
        plt.title(f'Amplification plot for {target} {date}' , fontname='Cambria', fontsize=16)
        plt.xlabel('Cycle', fontname='Cambria', fontsize=14)
        plt.ylabel('ΔRn', fontname='Cambria', fontsize=14)

        plt.grid(True, color='grey', axis='y')
        plt.hlines(y=threshold, xmin=0, xmax=40, color='red', linestyles='dashed', label='Threshold')

        plt.xlim([0,40])
        plt.gca().xaxis.set_major_locator(plt.MultipleLocator(2))

        plt.ylim([0.01, 5])
        plt.yscale('log')
        plt.gca().yaxis.set_major_formatter(ScalarFormatter())

        handles, labels = plt.gca().get_legend_handles_labels()
        handles, labels = zip(* sorted(zip(handles, labels), key=lambda x: x[1]))

        plt.legend(handles, labels, fontsize=9, loc='upper left')
        # HINT: https://www.sqlpey.com/python/top-2-methods-to-control-legend-order-in-matplotlib/

        plt.show()


# Resolve the file paths
MAIN_DIR = Path(__file__).resolve(strict=True).parent.parent
INPUT = MAIN_DIR / 'data' / 'input' / 'Results.xls'
LEGEND = MAIN_DIR / 'data' / 'metadata' / 'Plate_layout.xlsx'
OUTPUT = MAIN_DIR / 'data' / 'output'
CONFIG = MAIN_DIR / 'config' / 'config.yaml'

# Load the config
with open(CONFIG) as file:
    config = yaml.safe_load(file)

    REF_GENES = config['housekeeping_genes']
    REF_GENES = [x.lower() for x in REF_GENES]

    target_thresholds = config['thresholds']

# Load data
raw_data = pd.read_excel(INPUT)
mapping_data = pd.read_excel(LEGEND)

# Experimental date
experiment_date = re.sub(r'\s?(AM|PM|BST)', '', raw_data.iloc[2, 1])
experiment_date = pd.to_datetime(experiment_date)
experiment_date_formatted = experiment_date.strftime('%d %b %Y')

# Pre-prepare the raw data dataframe
raw_data = raw_data.iloc[6:,]
raw_data = raw_data.rename(columns=raw_data.iloc[0]).iloc[1:]
raw_data = raw_data.set_index('Well')

# Load information if well should be included
mapping_data = pd.read_excel(LEGEND)
to_include = mapping_data.iloc[10:18, :13]
to_include = to_include.set_index(to_include.columns[0])
to_include_long = to_include.stack()

for (row_letter, col_idx), value in to_include_long.items():
    cell_coord = f'{row_letter}{col_idx}'
    raw_data.loc[cell_coord, 'include'] = value

# Load name and color metadata
workbook = openpyxl.load_workbook(LEGEND)
sheet = workbook.active

for row in sheet.iter_rows(min_row=2, max_row=9):
    row_letter = row[0].value

    for col_idx, cell in enumerate(row[1:], start=1):
        cell_coord = f'{row_letter}{col_idx}'
        value = cell.value

        fill = cell.fill
        color = None

        # Get fill color
        if fill.patternType == 'solid':
            fg = fill.fgColor

            if fg.type == 'rgb' and fg.rgb is not None:
                color = fg.rgb
                color = f'#{color[-6:]}'  # Openpyxl returns ARGB and matplotlib accepts RGB

        raw_data.loc[cell_coord, 'sample_name'] = value
        raw_data.loc[cell_coord, 'color'] = color

target_names = raw_data['Target Name'].dropna().unique()

create_graph(raw_data, target_names, target_thresholds, experiment_date_formatted)
