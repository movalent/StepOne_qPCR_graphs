# Author: KlaudiaK
# Creation date: 28 July 2025

import pandas as pd

import file_utils
import preprocessing
import plotting
from paths import CONFIG, create_paths


def main() -> None:
    # Load configuation
    target_thresholds, ref_genes, plot_properties, results_file_name = file_utils.load_config(CONFIG)

    # Resolve paths
    data_paths = create_paths(results_file_name)

    # Load raw data and plate mapping
    raw_data, mapping_data = file_utils.load_raw_data(data_paths['INPUT'], data_paths['LEGEND'])
    openpyxl_sheet = file_utils.load_plate_layout(data_paths['LEGEND'])

    # Process the data
    experiment_date_formatted = preprocessing.extract_date(raw_data)
    raw_data = preprocessing.preprocess_raw_data(raw_data)
    raw_data = preprocessing.preprocess_mapping_data(mapping_data, raw_data)

    raw_data, target_names,  = preprocessing.preprocess_name_color(openpyxl_sheet, raw_data)
    # print(raw_data)

    # Generate and save the plots
    plotting.create_amplification_plots(raw_data, target_names,
                          target_thresholds, plot_properties,
                          experiment_date_formatted, data_paths)

if __name__ == '__main__':
    main()
