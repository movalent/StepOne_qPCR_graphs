from pathlib import Path

MAIN_DIR = Path(__file__).resolve(strict=True).parent.parent
INPUT = MAIN_DIR / 'data' / 'input' / 'Results.xls'
LEGEND = MAIN_DIR / 'data' / 'metadata' / 'Plate_layout.xlsx'
OUTPUT = MAIN_DIR / 'data' / 'output'
CONFIG = MAIN_DIR / 'config' / 'config.yaml'
