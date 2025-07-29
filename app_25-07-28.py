import pandas as pd
import matplotlib.pyplot as plt

import openpyxl

pd.options.display.width = 0
pd.options.display.max_columns = 15

# Process plate layout into legend dataframe
df_legend_input = pd.read_excel('Plate_layout.xlsx')
df_legend_input.set_index('Unnamed: 0', inplace=True)

legend = pd.DataFrame(columns=['Well', 'Sample_name', 'Color'])
column_names = [x for x in df_legend_input.columns]
for letter, cols in df_legend_input.iterrows():
    for col_name, value in zip(column_names, cols):
        cell_position = f'{letter}{col_name}'
        row = pd.DataFrame([{'Well':cell_position, 'Sample_name':value, 'Color':''}])
        legend = pd.concat([legend, row])

# Extracting cell color with openpyxl
workbook = openpyxl.load_workbook('Plate_layout.xlsx')
sheet = workbook.active
for row_c in sheet.iter_rows():
    for cell in row_c:
        color = cell.fill.start_color.index
        for index, row in legend.iterrows():
            if row['Sample_name'] == cell.value:
                legend.loc[legend['Sample_name'] == cell.value, 'Color'] = f'#{color[2:]}'  # TIP: openpyxl returns color in format where first two hex symbols must be axed to be read by matplotlib

# Load data to graph
df_results = pd.read_excel('Results.xls', sheet_name='Amplification Data', skiprows=7)

targets = df_results['Target Name'].dropna().unique()

print('Detected targets: ', targets)
goi_prompt = input(f'Is {targets[0]} a GoI: y/n ')
if goi_prompt == 'y':
    goi_idx = 0
    ref_idx = 1
else:
    goi_idx = 1
    ref_idx = 0

df_goi = df_results[df_results['Target Name'] == targets[goi_idx]]
df_ref = df_results[df_results['Target Name'] == targets[ref_idx]]

df_goi_piv = df_goi.pivot_table(index='Cycle', columns='Well', values='ΔRn')
df_ref_piv = df_ref.pivot_table(index='Cycle', columns='Well', values='ΔRn')

legend.set_index('Well', inplace=True)
legend_dict = {}
for index, row in legend.iterrows():
    legend_dict[index] = (row['Sample_name'], row['Color'])

date = input('Graph for data from: ')

# Create graph
def create_graph(targets, date):
    for target, target_name in targets:
        x = target.index[1:]
        threshold = float(input(f'Threshold for {target_name}: '))
        for col_name, col in target.items():
            color_temp = legend_dict[col_name][1]
            label_temp = legend_dict[col_name][0]
            plt.plot(x, col[1:], color=color_temp, linewidth=0.75,
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


        handles, labels = plt.gca().get_legend_handles_labels()
        handles, labels = zip(* sorted(zip(handles, labels), key=lambda x: x[1]))
        plt.gca().legend(handles, labels)
        plt.legend(fontsize=9, loc='upper left')
        # TIP: https://www.sqlpey.com/python/top-2-methods-to-control-legend-order-in-matplotlib/
        plt.show()

create_graph([(df_goi_piv, targets[goi_idx]), (df_ref_piv, targets[ref_idx])], date)