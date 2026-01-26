# Data Directory

## Structure

### `raw/`
- `question_dataset_full.json` - Original dataset (1,686 questions)
- `ca3104_official_syllabus.json` - Course syllabus
- Labels: 1 = In-syllabus, 0 = Out-of-syllabus

### `processed/`
- `train.json` - Training set (1,348 samples, 80%)
- `val.json` - Validation set (338 samples, 20%)
- `test.json` - Test set
- `augmented_dataset.json` - Format bias corrected dataset