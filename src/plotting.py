from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

from paths import OUTPUT

def create_graph(df, target_names, thresholds, plot_prop, date) -> plt:

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

        now = datetime.now()
        fmt_datetime = now.strftime('%Y-%m-%d %H-%M-%S')

        for file_type in ['png', 'tiff']:
            plt.savefig(OUTPUT / f'{date}_{target}_{fmt_datetime}.{file_type}',
                        transparent=plot_prop['transparent'],
                        dpi=plot_prop['dpi']
                        )

