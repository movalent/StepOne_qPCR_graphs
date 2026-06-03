from pathlib import Path

MAIN_DIR = Path(__file__).resolve(strict=True).parent.parent
CONFIG = MAIN_DIR / 'config' / 'config.yaml'

def create_paths(results_input: str, plate_layout: str = 'Plate_layout.xlsx') -> dict[str, Path]:
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

    output_dir = MAIN_DIR / 'data' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    return {
        'INPUT': MAIN_DIR / 'data' / 'input' / results_input,
        'LEGEND': MAIN_DIR / 'data' / 'metadata' / plate_layout,
        'OUTPUT': output_dir
    }
