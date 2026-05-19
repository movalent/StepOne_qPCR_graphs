import yaml
from pathlib import Path

import pandas as pd
import openpyxl


def load_config(config_path: Path) -> tuple:
    with open(config_path) as file:
        config = yaml.safe_load(file)
        # print(config)

        REF_GENES = config['housekeeping_genes']
        REF_GENES = [x.lower() for x in REF_GENES]

        target_thresholds = config['thresholds']

        plot_properties = config['plot_properties']

        results_file_name = config['input_file_name']

        return target_thresholds, REF_GENES, plot_properties, results_file_name

def load_data(raw_path: Path, mapping_path: Path) -> tuple:
    raw_data = pd.read_excel(raw_path)
    mapping_data = pd.read_excel(mapping_path)

    return raw_data, mapping_data

def load_data_openpyxl(mapping_path: Path) -> pd.Dataframe:

    workbook = openpyxl.load_workbook(mapping_path)
    sheet = workbook.active

    return sheet
