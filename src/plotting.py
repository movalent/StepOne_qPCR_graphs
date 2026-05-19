from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

def create_amplification_plots(df, target_names, thresholds, plot_prop, date, data_paths) -> plt:
    GRAPH_LINEWIDTH = 0.75
    GRAPH_FONTNAME = 'Cambria'

    TITLE_FONTSIZE = 16
    AXIS_FONTSIZE = 14
    LEGEND_FONTSIZE = 9

    DISP_CYCLE_START = 0
    DISP_CYCLE_END = 40
    DISP_CYCLE_INTERVAL = 2

    DISP_RN_MIN = 0.01
    DISP_RN_MAX = 5

    THRESHOLD_LINE_COL = 'red'
    THRESHOLD_LINE_STYLE = 'dashed'

    OUTPUT_FORMATS = ['png', 'tiff', 'pdf']

    for target in target_names:

        slice_df = df.loc[(df['Target Name'] == target) &
                          (df['include'] == 1)
                          ]

        if slice_df.empty:
            continue

        targets = slice_df.groupby(by='sample_name')

        try:
            threshold = thresholds[target]
        except KeyError:
            threshold = input(f'No threshold specified for {target}. Input the threshold manually, or add to the configuration file and restart the script: ')

        for sample_name, group in targets:

            x_values = group['Cycle']
            y_values = group['ΔRn']

            plt.plot(x_values, y_values,
                    color=group['color'].iloc[0],
                    linewidth=GRAPH_LINEWIDTH,
                    label=sample_name if sample_name not in plt.gca().get_legend_handles_labels()[1] else ''
                    )
            # HINT: https://stackoverflow.com/a/47949224

        # Graph style
        plt.title(f'Amplification plot for {target} {date}' , fontname=GRAPH_FONTNAME, fontsize=TITLE_FONTSIZE)
        plt.xlabel('Cycle', fontname=GRAPH_FONTNAME, fontsize=AXIS_FONTSIZE)
        plt.ylabel('ΔRn', fontname=GRAPH_FONTNAME, fontsize=AXIS_FONTSIZE)

        plt.grid(True, color='grey', axis='y')
        plt.hlines(y=threshold, xmin=DISP_CYCLE_START, xmax=DISP_CYCLE_END,
                   color=THRESHOLD_LINE_COL, linestyles=THRESHOLD_LINE_STYLE, label='Threshold'
                   )

        plt.xlim([DISP_CYCLE_START, DISP_CYCLE_END])
        plt.gca().xaxis.set_major_locator(plt.MultipleLocator(DISP_CYCLE_INTERVAL))

        plt.ylim([DISP_RN_MIN, DISP_RN_MAX])
        plt.yscale('log')
        plt.gca().yaxis.set_major_formatter(ScalarFormatter())

        handles, labels = plt.gca().get_legend_handles_labels()
        handles, labels = zip(* sorted(zip(handles, labels), key=lambda x: x[1]))

        plt.legend(handles, labels, fontsize=LEGEND_FONTSIZE, loc='upper left')
        # HINT: https://www.sqlpey.com/python/top-2-methods-to-control-legend-order-in-matplotlib/

        now = datetime.now()
        fmt_datetime = now.strftime('%Y-%m-%d %H-%M-%S')

        for file_type in OUTPUT_FORMATS :
            plt.savefig(data_paths['OUTPUT'] / f'{date}_{target}_{fmt_datetime}.{file_type}',
                        transparent=plot_prop['transparent'],
                        dpi=plot_prop['dpi']
                        )
        plt.close()

