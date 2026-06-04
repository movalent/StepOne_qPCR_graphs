import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import openpyxl
from openpyxl.worksheet.worksheet import Worksheet

@dataclass(frozen=True)
class Config:
    target_thresholds: dict[str, float]
    ref_genes: list[str]
    plot_properties: dict[str, Any]
    results_file_name: str
    output_file_format: list[str]

def validate_thresholds(thresholds: dict[str, Any]) -> dict[str, float]:

    if not isinstance(thresholds, dict):
        raise ValueError('"Thresholds" must be a dictionary of target names and numeric values.')

    validated_thresholds = {}

    for target, value in thresholds.items():
        if value is None:
            raise ValueError(f'Threshold for target {target} is not set in config.yaml. '
                             'Please provide a value for ΔRn threshold.')

        try:
            validated_thresholds[target] = float(value)
        except (TypeError, ValueError) as e:
            raise ValueError(f'Threshold for target {target} must be numeric. Current value: {value}')

    return validated_thresholds


def load_config(config_path: Path) -> Config:
    """
    Load configuration from config.yaml

    Args:
        config_path (Path): Path to configuration file

    Returns:
        Config object containing:
            - target_thresholds (float): ΔRn threshold values per target
            - ref_genes (str): Lowercased housekeeping genes
            - plot_properties (Any): Plot settings (dpi, transparency, etc.)
            - results_file_name (str): Raw data file name
            - output_file_format (list): File formats of the saved figure
    """

    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        # print(config)

        if config is None:
            raise ValueError(f'Configuration file is empty. File localization: {config_path}')

        ref_genes = [x.lower() for x in config['housekeeping_genes']]
        target_thresholds = validate_thresholds(config['thresholds'])

        return Config(
            target_thresholds = target_thresholds,
            ref_genes = ref_genes,
            plot_properties = config['plot_properties'],
            results_file_name = config['input_file_name'],
            output_file_format = config['output_file_format']
            )


def load_raw_data(raw_path: Path, mapping_path: Path) -> tuple:
    """
    Load raw qPCR amplification data and plate mapping from Excel files.

    Args:
        raw_path (Path): Path to the StepOne qPCR results Excel file.
        mapping_path (Path): Path to the plate mapping Excel file.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]:
            - raw_data: Raw amplification data
            - mapping_data: Plate layout data defining sample inclusion and positions
    """
    raw_data = pd.read_excel(raw_path)
    mapping_data = pd.read_excel(mapping_path)

    if raw_data.empty:
        raise ValueError(f'Raw qPCR results file contains no data.')

    if mapping_data.empty:
        raise ValueError(f'Plate mapping file contains no data.')

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
    workbook.close()

    return sheet
