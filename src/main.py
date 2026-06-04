# Author: KlaudiaK
# Creation date: 28 July 2025

import logging
import sys

import file_utils
import preprocessing
import plotting
from paths import CONFIG, create_paths

logger = logging.getLogger(__name__)

def run_pipeline() -> None:
    """
    Run the StepOne qPCR amplification visualization pipeline.
    """

    # Load configuration
    logger.info('Loading configuration')
    config = file_utils.load_config(CONFIG)

    # Resolve paths
    logger.info('Resolving paths')
    data_paths = create_paths(config.results_file_name)

    # Load raw data and plate mapping
    logger.info('Loading raw data')
    raw_data, mapping_data = file_utils.load_raw_data(data_paths['INPUT'], data_paths['LEGEND'])

    logger.info('Loading plate mapping') # Pandas does not support extracting color from Excell cells
    openpyxl_sheet = file_utils.load_plate_layout(data_paths['LEGEND'])

    # Process the data
    logger.info('Preprocessing')
    experiment_date_formatted = preprocessing.extract_date(raw_data)

    processed_data = preprocessing.preprocess_raw_data(raw_data)
    processed_data = preprocessing.preprocess_mapping_data(mapping_data, processed_data)

    processed_data, target_names  = preprocessing.preprocess_name_color(openpyxl_sheet, processed_data)
    # print(processed_data)

    # Generate and save the plots
    logger.info('Creating plots (%d targets)', len(target_names))
    plotting.create_amplification_plots(
        processed_data,
        target_names,
        config.target_thresholds,
        config.plot_properties,
        experiment_date_formatted,
        data_paths
        )

def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
        )

    try:
        run_pipeline()
    except (FileNotFoundError, KeyError, ValueError) as e:
        logger.error('Pipeline stopped: %s', e)
        return 1
    except Exception:
        logger.exception('Unexpected error. Pipeline stopped')
        return 1

    logger.info('Pipeline completed succesfully')
    return 0

if __name__ == '__main__':
    sys.exit(main())

