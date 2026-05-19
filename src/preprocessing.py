from datetime import datetime
import re

import pandas as pd

def extract_date(raw_data: pd.DataFrame) -> pd.DatetimeIndex:
    experiment_date = re.sub(r'\s?(AM|PM|BST)', '', raw_data.iloc[2, 1])
    experiment_date = pd.to_datetime(experiment_date)
    experiment_date_formatted = experiment_date.strftime('%d %b %Y')

    return experiment_date_formatted

def preprocess_raw_data(raw_data: pd.DataFrame) -> pd.DataFrame:
    df = raw_data.copy()
    df = df.iloc[6:,]
    df = df.rename(columns=df.iloc[0]).iloc[1:]
    df = df.set_index('Well')

    return df

def preprocess_mapping_data(mapping_data: pd.DataFrame, raw_data: pd.DataFrame) -> pd.Dataframe:
    df = raw_data.copy()
    to_include = mapping_data.iloc[10:18, :13]
    to_include = to_include.set_index(to_include.columns[0])
    to_include_long = to_include.stack()

    for (row_letter, col_idx), value in to_include_long.items():
        cell_coord = f'{row_letter}{col_idx}'
        df.loc[cell_coord, 'include'] = value

    return df

def preprocess_name_color(sheet, raw_data) -> pd.DataFrame:

    df = raw_data.copy()

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

            df.loc[cell_coord, 'sample_name'] = value
            df.loc[cell_coord, 'color'] = color

    target_names = df['Target Name'].dropna().unique()

    return df, target_names
