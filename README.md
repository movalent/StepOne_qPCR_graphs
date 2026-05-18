# StepOne qPCR Data Visualisation
A Python-based tool for reproducible, high-quality visualization and analysis of StepOne™ qPCR system output data.

## Overview
The default StepOne™ software has several limitations:
- Cumbersome way to rename samples
- Poor customization of output plots
- Export restricted to low-quality .jpg files
- Graph dimensions depend on GUI window size (non-reproducible)

This project solves these issues by providing:
- Fully scriptable and reproducible visualization pipeline
- High-quality, publication-ready plots
- Flexible sample renaming and metadata handling
- Export to vector and standard formats (.png, .tiff)
- Integration with metadata templates (e.g., plate layouts)

## 📁 Project Structure
```
project-root/
│
├── data/
│   ├── input/              # Raw StepOne export files (e.g. .xls)
│   ├── metadata/           # Plate maps
│   └── output/             # Processed figures
│
├── src/
|   |── file_utils.py       # File loading & parsing
│   ├── paths.py            # File paths
│   ├── preprocessing.py    # Data cleaning & transformations
│   └── plotting.py         # Visualization functions
│
├── config.yaml             # User-defined settings (thresholds, targets, etc.)
├── main.py                 # Entry point
├── requirements.txt
└── README.md
```

## ⚙️ Installation

Shell
```
git clone https://github.com/movalent/StepOne_qPCR_graphs.git
cd StepOne_qPCR_graphs

python -m venv .venv
source .venv/bin/activate
#source .venv .venv\Scripts\activate # For Windows

pip install -r requirements.txt
```

## Usage

1. Export the amplification data:

> Export -> Amplification Data -> File type: xls

2. Place raw StepOne export file into:

> data/input/

3. Add metadata to the plate layout:

> data/metadata/Plate_layout.xlsx

4. Configure analysis parameters:

> config.yaml

5. Run the pipeline:

Shell
```
python main.py
```

## Output

- Publication-ready figures
- Configurable resolution and dimensions
- Export formats:
    - PNG
    - TIFF

## 🛠️ Dependencies

pandas
numpy
matplotlib
pyyaml
openpyxl

## 📌 Roadmap
-  Automatic Ct calling from raw fluorescence
- Plate layout visualization
- Batch processing support

## 🤝 Contributing
Contributions are welcome. Suggested workflow:
- Fork the repository
- Create a feature branch
- Commit changes with clear messages
- Submit a pull request

## ⚖️ License
```
AGPL-3.0
```
