# Author: KlaudiaK
# Creation date: 28 July 2025

from pathlib import Path
import re

import numpy as np
import pandas as pd

from paths import CONFIG, INPUT, LEGEND
import file_utils
import preprocessing
import plotting

# Options for pandas dataframe print
pd.options.display.width = 0
pd.options.display.max_columns = 15

def main() -> None:
    # Load configuation
    target_thresholds, REF_GENES = file_utils.load_config(CONFIG)
    # Load raw data and plate mapping
    raw_data, mapping_data = file_utils.load_data(INPUT, LEGEND)
    openpyxl_sheet = file_utils.load_data_openpyxl(LEGEND)

    # Process the data
    experiment_date_formatted = preprocessing.extract_date(raw_data)
    raw_data = preprocessing.preprocess_raw_data(raw_data)
    mapping_data = preprocessing.preprocess_mapping_data(mapping_data, raw_data)

    raw_data, target_names = preprocessing.preprocess_name_color(openpyxl_sheet, raw_data)

    # print(raw_data)

    plotting.create_graph(raw_data, target_names, target_thresholds, experiment_date_formatted)


if __name__ == '__main__':
    main()
