from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve(strict=True).parent.parent
CONFIG = PROJECT_ROOT / 'config' / 'config.yaml'

def create_paths(results_input: str, plate_layout: str = 'Plate_layout.xlsx') -> dict[str, Path]:
    """
    Construct file system paths used in the qPCR analysis.

    Args:
        results_input (str): File name of the raw qPCR results file
        plate_layout (str): File name of the Excel plate layout

    Returns:
        Dict[str, Path]: Dictionary containing resolved paths with keys:
                    - "INPUT": Path to raw results file
                    - "LEGEND": Path to plate layout Excel file
                    - "OUTPUT": Folder for saving generated plots
    """

    output_dir = PROJECT_ROOT / 'data' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    return {
        'INPUT': PROJECT_ROOT / 'data' / 'input' / results_input,
        'LEGEND': PROJECT_ROOT / 'data' / 'metadata' / plate_layout,
        'OUTPUT': output_dir
    }
