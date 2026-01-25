# Data Directory

## Purpose
This directory contains datasets for the Academic Doubt Clarification System - a two-layer intent classification model for validating student questions against the CA3104 syllabus.

## Structure

### `raw/`
Original, unmodified datasets as collected or received:
- `question_dataset_full.json` - **FROZEN FINAL DATASET** (300 questions, Q001-Q300)
- Labels: 1 = In-syllabus, 0 = Out-of-syllabus
- **⚠️ DO NOT MODIFY - Academic experiment dataset**

### `processed/`
Cleaned and split datasets ready for model training:
- `train.json` - Training set (210 samples, 70%)
- `val.json` - Validation set (45 samples, 15%)
- `test.json` - Test set (45 samples, 15%)

## Academic Best Practices
- **Raw data preservation**: Never modify files in `raw/` to maintain data lineage
- **Reproducible splits**: Fixed seed (42) ensures consistent train/val/test splits
- **Version control**: Track all preprocessing steps for research reproducibility