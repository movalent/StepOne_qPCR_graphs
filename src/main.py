# Author: KlaudiaK
# Creation date: 28 July 2025

import logging

import file_utils
import preprocessing
import plotting
from paths import CONFIG, create_paths

logger = logging.getLogger(__name__)

def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Load configuation
    logger.info('Loading configuration')
    config = file_utils.load_config(CONFIG)

    # Resolve paths
    logger.info('Resolving paths')
    data_paths = create_paths(config.results_file_name)

    # Load raw data and plate mapping
    logger.info('Loading raw data')
    raw_data, mapping_data = file_utils.load_raw_data(data_paths['INPUT'], data_paths['LEGEND'])
    openpyxl_sheet = file_utils.load_plate_layout(data_paths['LEGEND'])  # Pandas does not support extracting color

    # Process the data
    logger.info('Preprocessing')
    experiment_date_formatted = preprocessing.extract_date(raw_data)
    raw_data = preprocessing.preprocess_raw_data(raw_data)
    raw_data = preprocessing.preprocess_mapping_data(mapping_data, raw_data)

    raw_data, target_names  = preprocessing.preprocess_name_color(openpyxl_sheet, raw_data)
    # print(raw_data)

    # Generate and save the plots
    logger.info('Creating plots (%d targets)', len(target_names))
    plotting.create_amplification_plots(raw_data, target_names,
                          config.target_thresholds, config.plot_properties,
                          experiment_date_formatted, data_paths)

if __name__ == '__main__':
    main()
