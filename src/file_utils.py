import yaml
from pathlib import Path

import pandas as pd
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

def load_config(config_path: Path) -> tuple:
    """
    Load configuration from config.yaml

    Args:
        config_path (Path): Path to configuration file

    Returns:
        tuple: Tuple with parsed configuration
            - target_thresholds (float): ΔRn threshold values per target
            - ref_genes (str): Lowercased housekeeping genes
            - plot_properties (Any): Plot settings (dpi, transparency, etc.)
            - result_file_name (str): Raw data file name
    """

    with open(config_path) as file:
        config = yaml.safe_load(file)
        # print(config)

        ref_genes = config['housekeeping_genes']
        ref_genes = [x.lower() for x in ref_genes]

        target_thresholds = config['thresholds']

        plot_properties = config['plot_properties']

        results_file_name = config['input_file_name']

        return target_thresholds, ref_genes, plot_properties, results_file_name

def load_raw_data(raw_path: Path, mapping_path: Path) -> tuple:
    """
    Load raw qPCR amplification data and plate mapping from Excel files.

    Args:
        raw_path (Path): Path to the StepOne qPCR results Excel file.
        mapping_path (Path): Path to the plate mapping Excel file.

    Returns:
        Tuple[pd.Dataframe, pd.Dataframe]:
            - raw_data: Raw amplification data
            - mapping_data: Plate layout data defining sample inclusion and positions
    """
    raw_data = pd.read_excel(raw_path)
    mapping_data = pd.read_excel(mapping_path)

    return raw_data, mapping_data

def load_plate_layout(mapping_path: Path) -> Worksheet:
    """
    Load the plate layout Excel sheet using Openpyxl.

    Args:
        mapping_path (Path): Path to the plate layout Excel file.

    Returns:
        Worksheet: Active worksheet containing plate layout, including cell formatting (e.g. fill colors)
    """

    workbook = openpyxl.load_workbook(mapping_path)
    sheet = workbook.active

    return sheet
