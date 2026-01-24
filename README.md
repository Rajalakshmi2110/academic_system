# Academic Doubt Clarification System

Two-Layer Intent Classification System for Academic Question Validation

## Project Structure
- `data/` - Dataset files (raw and processed)
- `src/` - Source code modules
- `notebooks/` - Jupyter notebooks for analysis
- `reports/` - Generated reports and documentation

## Setup
```bash
pip install -r requirements.txt
```

## Usage
1. ~~Place dataset in `data/raw/question_dataset_full.json`~~ **DATASET FROZEN**
2. Run preprocessing: `python src/data_preprocessing/split_dataset.py`

## Dataset Status
**FINAL LABELED DATASET - DO NOT MODIFY**
- File: `data/raw/question_dataset_full.json`
- Status: Frozen for academic experiment
- Entries: 300 questions (Q001-Q300)
- Labels: 150 in-syllabus (1), 150 out-of-syllabus (0)