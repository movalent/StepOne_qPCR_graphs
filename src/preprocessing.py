import re

import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet

def extract_date(raw_data: pd.DataFrame) -> str:
    """
    Extract the experiment date from a fixed location in the StepOne Excel export.

    Args:
        raw_data (pd.DataFrame): DataFrame representing the raw StepOne Excel export.

    Returns:
        str: Formatted date string (e.g. 01 Jan 2021)

    Notes:
        Assumes the date is located at a fixed position in the input DataFrame,
        defined by DATE_ROW_IDX and DATE_COL_IDX. BST time zone information is
        removed.
    """
    DATE_ROW_IDX = 2
    DATE_COL_IDX = 1

    experiment_date = re.sub(r'\s?(AM|PM|BST)', '', raw_data.iloc[DATE_ROW_IDX, DATE_COL_IDX])
    experiment_date = pd.to_datetime(experiment_date)
    experiment_date_formatted = experiment_date.strftime('%d %b %Y')

    return experiment_date_formatted

def preprocess_raw_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Remove header rows from the raw DataFrame, rename columns, and set the index to well position.

    Args:
        raw_data (pd.DataFrame): DataFrame representing the raw StepOne Excel export.

    Returns:
        pd.DataFrame: Processed DataFrame with header rows removed, columns renamed,
        and index set to well positions.

    Notes:
        The StepOne export Excel file containts metadata rows above the data table.
        PLATE_ROW_START defines the index of the first row containing amplification data.
    """
    PLATE_ROW_START = 6

    df = raw_data.copy()
    df = df.iloc[PLATE_ROW_START:,]
    df = df.rename(columns=df.iloc[0]).iloc[1:]
    df = df.set_index('Well')

    return df

def preprocess_mapping_data(mapping_data: pd.DataFrame, raw_data: pd.DataFrame) -> pd.DataFrame:
    """
    Add an 'include' column to the raw data indicating which samples should be included in downstream visualization, based on plate mapping.

    Args:
        mapping_data (pd.DataFrame): Plate layout DataFrame containing inclusion flags.
        raw_data (pd.DataFrame): Preprocessed qPCR data indexed by well position.

    Returns:
        pd.DataFrame: Updated DataFrame with added 'include' column indicating which wells should be visualized.

    Notes:
        The mapping Excel workbook contains two plate layouts:
            - Top: sample names + colors
            - Bottom: inclusion flags for each well

        PLATE_ROW_START, PLATE_ROW_END, and PLATE_COL_END define the location of the bottom plate
        within the worksheet
    """
    PLATE_ROW_START = 10
    PLATE_ROW_END = 18
    PLATE_COL_END = 13

    df = raw_data.copy()
    to_include = mapping_data.iloc[PLATE_ROW_START:PLATE_ROW_END, :PLATE_COL_END]
    to_include = to_include.set_index(to_include.columns[0])
    to_include_long = to_include.stack()

    for (row_letter, col_idx), value in to_include_long.items():
        cell_coord = f'{row_letter}{col_idx}'
        df.loc[cell_coord, 'include'] = value

    return df

def preprocess_name_color(sheet: Worksheet, raw_data: pd.DataFrame) -> tuple:
    """
    Add sample metadata (name and color) to raw data, and extract target names.

    Args:
        sheet (Worksheet): Sheet object containing the sample name and sample color data.
        raw_data (DataFrame): Preprocessed qPCR data indexed by well position.

    Returns:
        tuple[pd.DataFrame, np.array]:
            - pd.DataFrame: Updated DataFrame with added sample_name and sample_color columns
            - np.array: List of unique target names (e.g. eGFP, RNAseP, GAPDH, Spike)

    Notes:
        The mapping workbook contains two plate layouts:
            - Top: sample names + colors
            - Bottom: inclusion flags for each well

        PLATE_ROW_START, PLATE_ROW_END, and PLATE_COL_OFFSET define the location of the top plate
        within the worksheet.
        Openpyxl reads cell background color as ARGB values, and matplotlib requires RGB format.
        The alpha channel is stripped during conversion.
    """
    PLATE_ROW_START = 2
    PLATE_ROW_END = 9
    PLATE_COL_OFFSET = 1

    df = raw_data.copy()

    for row in sheet.iter_rows(min_row=PLATE_ROW_START, max_row=PLATE_ROW_END):
        row_letter = row[0].value

        for col_idx, cell in enumerate(row[PLATE_COL_OFFSET:], start=PLATE_COL_OFFSET):
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

            df.loc[cell_coord, 'sample_name'] = value
            df.loc[cell_coord, 'color'] = color

    target_names = df['Target Name'].dropna().unique()

    return df, target_names
