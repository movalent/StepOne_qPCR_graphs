from datetime import datetime
from pathlib import Path

import openpyxl
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

pd.options.display.width = 0
pd.options.display.max_columns = 15

BASE_DIR = Path(__file__).resolve().parent
path_input_file = BASE_DIR / 'data' / 'input' / 'Results.xls'
path_layout_file = BASE_DIR / 'data' / 'metadata' / 'Template_plate_layout.xlsx'

# Create dataframe to hold sample's info
df_sample_info = pd.DataFrame(columns=['Well', 'Sample_name', 'Color', 'Include'])

# Process the sample name
df_name_color = pd.read_excel(path_layout_file)
df_name_color.set_index('Unnamed: 0', inplace=True)
column_names = list(range(1,13))

for row_letter_1, row in df_name_color.iloc[:8,].iterrows():  # Without iloc dataframe spans to the 2nd include-dataframe
    for col_name_1, cell_value in zip(column_names, row):
        cell_position = f'{row_letter_1}{col_name_1}'
        row = pd.DataFrame([{'Well':cell_position, 'Sample_name':cell_value, 'Color': '', 'Include': ''}])
        df_sample_info = pd.concat([df_sample_info, row])

df_sample_info.dropna(inplace=True)

# Extracting cell color via openpyxl
workbook = openpyxl.load_workbook(path_layout_file)
sheet = workbook.active
for row_c in sheet.iter_rows():
    for cell in row_c:
        color = cell.fill.start_color.index
        df_sample_info.loc[df_sample_info['Sample_name'] == cell.value, 'Color'] = f'#{color[2:]}'  # TIP: openpyxl returns color in format where first two hex symbols must be axed to be read by matplotlib

# Select which wells to be used
df_include_cell = pd.read_excel(path_layout_file, skiprows=10)
df_include_cell.set_index('Unnamed: 0', inplace=True)

for row_letter_2, row in df_include_cell.iterrows():
    for col_name_2, cell_value in zip(column_names, row):
        cell_position = f'{row_letter_2}{col_name_2}'
        df_sample_info.loc[df_sample_info['Well'] == cell_position, 'Include'] = cell_value

# Read experiment date from metadata
df_data = pd.read_excel(path_input_file, sheet_name='Amplification Data')
experiment_date = datetime.strptime(df_data.iloc[2, 1][:10], '%Y-%m-%d')
experiment_date_formatted = experiment_date.strftime('%d %b %Y')

# Load amplification data
df_results = pd.read_excel(path_input_file, sheet_name='Amplification Data', skiprows=7)
detected_targets = df_results['Target Name'].dropna().unique()

# Select if housekeeping is first or second on the target list
print('Detected amplification targets: ', detected_targets)

for target_name in detected_targets:
    if target_name in ['ACTB', 'GAPDH', 'RNAseP']:
        ref_idx = list(detected_targets).index(target_name)
        ref_status = 1
        continue
    goi_prompt = input(f'Is {target_name} a GoI: y/n ')
    if goi_prompt == 'y':
        goi_idx = list(detected_targets).index(target_name)
        goi_status = 1
        continue
    ref_prompt = input(f'Is {target_name} a housekeeping: y/n ')
    if ref_prompt == 'y':
        ref_idx = list(detected_targets).index(target_name)
        ref_status = 1

columns_to_keep = df_sample_info[df_sample_info['Include'] == 1.0]['Well']
columns_to_keep = list(columns_to_keep)

# Separate results based on target name & removing unwanted cells (not to keep)
# TODO: If result file has only one target, script will crash as list of targets has only one item.
targets = []
if goi_status:
    df_goi = df_results[(df_results['Target Name'] == detected_targets[goi_idx]) & (df_results['Well'].isin(columns_to_keep))]
    df_goi_piv = df_goi.pivot_table(index='Cycle', columns='Well', values='ΔRn')
    targets.append((df_goi_piv, detected_targets[goi_idx]))
if ref_status:
    df_ref = df_results[(df_results['Target Name'] == detected_targets[ref_idx]) & (df_results['Well'].isin(columns_to_keep))]
    df_ref_piv = df_ref.pivot_table(index='Cycle', columns='Well', values='ΔRn')
    targets.append((df_ref_piv, detected_targets[ref_idx]))

# Dictionary that holds sample info
df_sample_info.set_index('Well', inplace=True)

legend_dict = {}
for index, row in df_sample_info.iterrows():
    legend_dict[index] = (row['Sample_name'], row['Color'])

# Create graph
def create_graph(targets, date):
    for target, target_name in targets:
        x_values = target.index[1:]  # Index of dataframe is cycle number for x values
        threshold = float(input(f'Threshold for {target_name}: '))
        for well_coordinates, y_values in target.items():  # Column name is well coordinate, column values are y_values for graph
            color_temp = legend_dict[well_coordinates][1]  # Retrieve well color and label based on the legend and well position
            label_temp = legend_dict[well_coordinates][0]
            plt.plot(x_values, y_values[1:], color=color_temp, linewidth=0.75,
                     label=label_temp if label_temp not in plt.gca().get_legend_handles_labels()[1] else '')
            # HINT: https://stackoverflow.com/a/47949224

        # Graph style
        plt.title(f'Amplification plot for {target_name} {date}' , fontname='Cambria', fontsize=16)
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
        # TIP: https://www.sqlpey.com/python/top-2-methods-to-control-legend-order-in-matplotlib/
        plt.show()

create_graph(targets, experiment_date_formatted)