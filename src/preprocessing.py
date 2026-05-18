from datetime import datetime
import re

import pandas as pd

def extract_date(raw_data: pd.DataFrame) -> pd.DatetimeIndex:
    experiment_date = re.sub(r'\s?(AM|PM|BST)', '', raw_data.iloc[2, 1])
    experiment_date = pd.to_datetime(experiment_date)
    experiment_date_formatted = experiment_date.strftime('%d %b %Y')

    return experiment_date_formatted

def preprocess_raw_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    raw_data = raw_data.iloc[6:,]
    raw_data = raw_data.rename(columns=raw_data.iloc[0]).iloc[1:]
    raw_data = raw_data.set_index('Well')

    return raw_data

def preprocess_mapping_data(mapping_data: pd.DataFrame, raw_data: pd.DataFrame) -> pd.Dataframe:
    to_include = mapping_data.iloc[10:18, :13]
    to_include = to_include.set_index(to_include.columns[0])
    to_include_long = to_include.stack()

    for (row_letter, col_idx), value in to_include_long.items():
        cell_coord = f'{row_letter}{col_idx}'
        raw_data.loc[cell_coord, 'include'] = value

    return raw_data

def preprocess_name_color(sheet, raw_data) -> pd.DataFrame:

    for row in sheet.iter_rows(min_row=2, max_row=9):
        row_letter = row[0].value

        for col_idx, cell in enumerate(row[1:], start=1):
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

            raw_data.loc[cell_coord, 'sample_name'] = value
            raw_data.loc[cell_coord, 'color'] = color

    target_names = raw_data['Target Name'].dropna().unique()

    return raw_data, target_names
