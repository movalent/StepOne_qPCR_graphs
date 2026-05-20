from pathlib import Path

MAIN_DIR = Path(__file__).resolve(strict=True).parent.parent
CONFIG = MAIN_DIR / 'config' / 'config.yaml'

def create_paths(results_input: str) -> dict[str, Path]:
    """
    Construct file system paths used in the qPCR analysis.

    Args:
        results_input (str): File name of the raw qPCR results file

    Returns:
        Dict[str, Path]: Dictionary containing resolved paths with keys:
                    - "INPUT": Path to raw results file
                    - "LEGEND": Path to plate layout Excel file
                    - "OUTPUT": Folder for saving generated plots
    """

    return {
        'INPUT': MAIN_DIR / 'data' / 'input' / f'{results_input}',
        'LEGEND': MAIN_DIR / 'data' / 'metadata' / 'Plate_layout.xlsx',
        'OUTPUT': MAIN_DIR / 'data' / 'output'
    }
