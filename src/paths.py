from pathlib import Path

MAIN_DIR = Path(__file__).resolve(strict=True).parent.parent
CONFIG = MAIN_DIR / 'config' / 'config.yaml'

def create_paths(results_input: str):
    return {
        'INPUT': MAIN_DIR / 'data' / 'input' / f'{results_input}',
        'LEGEND': MAIN_DIR / 'data' / 'metadata' / 'Plate_layout.xlsx',
        'OUTPUT': MAIN_DIR / 'data' / 'output'
    }
